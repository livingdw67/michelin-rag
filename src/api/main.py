"""REST API for the report analyst.

Run:
    uvicorn src.api.main:app --port 8000
Docs:
    http://localhost:8000/docs
"""
import threading
import time
from collections import defaultdict, deque
from typing import Optional

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from pydantic import BaseModel, Field

from config.settings import COMPANIES, settings
from src.agent.brief import build_brief
from src.agent.graph import run_agent
from src.observability import track
from src.pipeline.guardrails import GuardrailError
from src.pipeline.metrics import load_metrics
from src.pipeline.retrieval import get_retriever

app = FastAPI(title="Tire Industry Report Analyst API", version="2.0",
              description="Grounded answers from four tire companies' 2025 annual reports, with verified citations.")


# --- Security and rate limiting ---------------------------------------------------------------

def require_api_key(x_api_key: Optional[str] = Header(default=None)):
    if settings.api_auth_token and x_api_key != settings.api_auth_token:
        raise HTTPException(status_code=401, detail="Missing or invalid X-API-Key header.")


class RateLimiter:
    """Sliding-window limiter per client. In-memory, so it applies per API process."""

    def __init__(self, per_minute):
        self.per_minute = per_minute
        self.calls = defaultdict(deque)
        self.lock = threading.Lock()

    def allow(self, client, now=None):
        now = time.monotonic() if now is None else now
        with self.lock:
            window = self.calls[client]
            while window and now - window[0] > 60:
                window.popleft()
            if len(window) >= self.per_minute:
                return False
            window.append(now)
            return True


limiter = RateLimiter(settings.rate_limit_per_minute)


def rate_limit(request: Request):
    client = request.client.host if request.client else "unknown"
    if not limiter.allow(client):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again in a minute.")


guarded = [Depends(require_api_key), Depends(rate_limit)]


# --- Schemas ----------------------------------------------------------------------------------

class Turn(BaseModel):
    role: str = Field(pattern="^(user|assistant)$")
    content: str


class AskRequest(BaseModel):
    question: str
    history: list[Turn] = Field(default_factory=list, max_length=20)


class Source(BaseModel):
    doc: str
    page: int
    quote: str


class AskResponse(BaseModel):
    request_id: str
    status: str
    answer: str
    route: str
    sources: list[Source]
    calculations: list[dict]
    latency_ms: int
    total_tokens: int


class BriefRequest(BaseModel):
    company_a: str
    company_b: str


# --- Endpoints --------------------------------------------------------------------------------

@app.get("/health")
def health():
    retriever = get_retriever()
    return {"status": "ok", "chunks_indexed": len(retriever.chunks), "companies": list(COMPANIES),
            "model": settings.chat_model}


@app.post("/ask", response_model=AskResponse, dependencies=guarded)
def ask(body: AskRequest):
    with track("ask", question=body.question) as record:
        try:
            result = run_agent(body.question, history=[(t.role, t.content) for t in body.history])
        except GuardrailError as e:
            record["status"] = "blocked"
            raise HTTPException(status_code=400, detail=str(e))
        record.update(status=result.status, route=result.route,
                      cited=[f"{s['doc']} p.{s['page']}" for s in result.sources])
    return AskResponse(request_id=record["request_id"], status=result.status, answer=result.answer,
                       route=result.route, sources=[Source(**{k: s[k] for k in ("doc", "page", "quote")})
                                                    for s in result.sources],
                       calculations=result.calculations, latency_ms=record["latency_ms"],
                       total_tokens=record["total_tokens"])


@app.get("/metrics", dependencies=[Depends(require_api_key)])
def metrics():
    data = load_metrics()
    if not data:
        raise HTTPException(status_code=404, detail="Metrics table not built. Run python -m src.pipeline.metrics.")
    return data


@app.post("/brief", dependencies=guarded)
def brief(body: BriefRequest):
    if body.company_a not in COMPANIES or body.company_b not in COMPANIES or body.company_a == body.company_b:
        raise HTTPException(status_code=400, detail=f"Choose two different companies from {list(COMPANIES)}.")
    with track("brief", companies=[body.company_a, body.company_b]) as record:
        memo, unsupported = build_brief(body.company_a, body.company_b)
        record.update(status="ok", unsupported_numbers=unsupported)
    return {"request_id": record["request_id"], "memo": memo, "unsupported_numbers": unsupported,
            "latency_ms": record["latency_ms"]}
