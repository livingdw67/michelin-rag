"""Per-request telemetry: latency, token usage, cost estimate, outcome, and sources.

Each request appends one JSON line to logs/requests.jsonl, which can be shipped to any log
platform. For step-level traces of every LLM call, set LANGSMITH_TRACING=true and
LANGSMITH_API_KEY in .env; LangChain sends traces to LangSmith automatically.
"""
import json
import logging
import threading
import time
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone

from langchain_community.callbacks import get_openai_callback

from config.settings import settings

logger = logging.getLogger("report_analyst")
_write_lock = threading.Lock()


def estimate_cost(prompt_tokens, completion_tokens):
    if not (settings.price_input_per_million or settings.price_output_per_million):
        return None
    return round(prompt_tokens / 1e6 * settings.price_input_per_million
                 + completion_tokens / 1e6 * settings.price_output_per_million, 6)


@contextmanager
def track(endpoint, **fields):
    """Time a request and capture token usage. Add outcome fields to the yielded dict."""
    record = {"request_id": uuid.uuid4().hex[:12], "endpoint": endpoint,
              "timestamp": datetime.now(timezone.utc).isoformat(), **fields}
    started = time.perf_counter()
    with get_openai_callback() as usage:
        try:
            yield record
        except Exception as e:
            record.setdefault("status", "error")
            record["error"] = f"{type(e).__name__}: {e}"
            raise
        finally:
            record["latency_ms"] = round((time.perf_counter() - started) * 1000)
            record["prompt_tokens"] = usage.prompt_tokens
            record["completion_tokens"] = usage.completion_tokens
            record["total_tokens"] = usage.total_tokens
            record["cost_usd"] = estimate_cost(usage.prompt_tokens, usage.completion_tokens)
            write(record)


def write(record):
    settings.log_dir.mkdir(parents=True, exist_ok=True)
    line = json.dumps(record, ensure_ascii=False, default=str)
    with _write_lock, open(settings.log_dir / "requests.jsonl", "a", encoding="utf-8") as f:
        f.write(line + "\n")
    logger.info(line)
