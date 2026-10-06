"""Build a cross-company metrics table where every figure is extracted, cited, and verified.

Usage:
    python -m src.pipeline.metrics      # writes data/metrics/metrics.json
"""
import json
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from typing import Literal, Optional

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from config.settings import COMPANIES, settings
from src.pipeline.answer import Citation, format_context
from src.pipeline.calculator import calculate, ungrounded_numbers
from src.pipeline.guardrails import verify_citations
from src.pipeline.retrieval import get_retriever

METRICS_FILE = settings.data_dir / "metrics" / "metrics.json"

METRICS = {
    "revenue": ("Revenue / sales", "What were {company}'s total consolidated sales (revenue) for the most recent "
                "fiscal year with reported results?"),
    "operating_profit": ("Operating profit (company-defined)", "What was {company}'s headline operating profit "
                         "measure (segment operating income, adjusted EBIT, or adjusted operating profit) for the "
                         "most recent fiscal year with reported results?"),
    "net_income": ("Net income attributable to shareholders", "What was {company}'s net income (or loss) "
                   "attributable to shareholders of the company for the most recent fiscal year with reported results?"),
    "employees": ("Employees", "How many employees did {company} have at the end of the most recent fiscal year?"),
    "capex": ("Capital expenditures", "What were {company}'s capital expenditures for the most recent fiscal "
              "year with reported results?"),
    "dividend": ("Dividend per share", "What dividend per share did {company} pay or propose for the most recent "
                 "fiscal year?"),
    "rd": ("R&D expenses", "What were {company}'s research and development expenses for the most recent fiscal "
           "year with reported results?"),
}
MONETARY = {"revenue", "operating_profit", "net_income", "capex", "rd"}

EXTRACT_PROMPT = """Extract one metric from the report excerpts. Use ONLY the excerpts.
- Prefer consolidated group figures for the latest fiscal year with actual (not planned) results.
- `display` is the figure as reported, with currency and unit (e.g. "€25,992 million").
- For money, `value_millions` is the amount in millions of the reported currency (e.g. 19.7 billion -> 19700).
  For employees, `value_millions` is the headcount itself. For dividends, it is the amount per share.
- `definition` is the company's own label for the figure (e.g. "segment operating income").
- The citation quote must be copied exactly from the excerpt and contain the number.
- If the excerpts don't contain it, set status to "not_found".

Metric: {metric}
Question: {question}

Excerpts:
{context}"""


class MetricValue(BaseModel):
    status: Literal["found", "not_found"]
    display: Optional[str] = None
    value_millions: Optional[float] = Field(default=None, description="See instructions for units")
    currency: Optional[str] = Field(default=None, description="ISO code, e.g. EUR, USD, JPY")
    period: Optional[str] = Field(default=None, description="e.g. FY2025 or FY2024")
    definition: Optional[str] = None
    citation: Optional[Citation] = None


def extract_metric(company, key, retriever=None, llm=None):
    label, template = METRICS[key]
    question = template.format(company=company)
    docs = (retriever or get_retriever()).retrieve(question)
    llm = llm or ChatOpenAI(model=settings.chat_model, api_key=settings.openai_api_key, reasoning_effort="low")
    prompt = ChatPromptTemplate.from_messages([("human", EXTRACT_PROMPT)])
    result = (prompt | llm.with_structured_output(MetricValue)).invoke(
        {"metric": label, "question": question, "context": format_context(docs)})

    row = {"company": company, "metric": key, "label": label, "status": "not_found"}
    if result.status != "found" or not result.citation or result.display is None:
        return row
    verified, _ = verify_citations([result.citation], docs)
    # The reported figure must literally appear in the verified quote
    if not verified or ungrounded_numbers(result.display, result.citation.quote):
        return {**row, "status": "unverified"}
    doc = next(d for d in docs if d.metadata["chunk_id"] == result.citation.chunk_id)
    return {**row, "status": "verified", "display": result.display, "value": result.value_millions,
            "currency": result.currency, "period": result.period, "definition": result.definition,
            "doc": doc.metadata["doc"], "page": doc.metadata["page"], "quote": result.citation.quote}


def _year(period):
    match = re.search(r"20\d\d", period or "")
    return match.group(0) if match else None


def add_margins(rows):
    """Operating and net margins, computed exactly from verified figures in the same currency."""
    by_key = {(r["company"], r["metric"]): r for r in rows}
    derived = []
    for company in COMPANIES:
        revenue = by_key.get((company, "revenue"), {})
        for key, label in (("operating_profit", "Operating margin"), ("net_income", "Net margin")):
            part = by_key.get((company, key), {})
            same_basis = (revenue.get("status") == part.get("status") == "verified"
                          and revenue.get("currency") == part.get("currency")
                          and _year(revenue.get("period")) == _year(part.get("period")) and revenue.get("value"))
            if same_basis:
                pct = calculate(f"{part['value']} / {revenue['value']} * 100")
                derived.append({"company": company, "metric": key.replace("_profit", "") + "_margin",
                                "label": label, "status": "calculated", "display": f"{pct:.1f}%",
                                "period": f"FY{_year(revenue['period'])}",
                                "definition": f"{part['definition']} / {revenue['definition']}"})
    return derived


def build_metrics():
    retriever = get_retriever()
    jobs = [(c, k) for c in COMPANIES for k in METRICS]
    with ThreadPoolExecutor(max_workers=6) as pool:
        rows = list(pool.map(lambda job: extract_metric(*job, retriever=retriever), jobs))
    rows += add_margins(rows)
    METRICS_FILE.parent.mkdir(parents=True, exist_ok=True)
    METRICS_FILE.write_text(json.dumps({"generated": date.today().isoformat(), "model": settings.chat_model,
                                        "rows": rows}, indent=2, ensure_ascii=False), encoding="utf-8")
    verified = sum(r["status"] in ("verified", "calculated") for r in rows)
    print(f"{verified}/{len(rows)} figures verified or calculated -> {METRICS_FILE}")
    for r in rows:
        print(f"  {r['company']:<12} {r['label']:<40} {r['status']:<10} {r.get('display', '')} "
              f"{r.get('period', '') or ''} p.{r.get('page', '-')}")


def load_metrics():
    return json.loads(METRICS_FILE.read_text(encoding="utf-8")) if METRICS_FILE.exists() else None


if __name__ == "__main__":
    build_metrics()
