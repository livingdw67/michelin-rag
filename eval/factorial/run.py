"""Run the 400-question factorial eval against the agent and grade every attempt.

Each attempt is appended to results/attempts.jsonl as soon as it's graded, so an interrupted run
resumes where it stopped (attempts already in the file are skipped). Analysis is separate:
`python -m eval.factorial.stats` reads the file and writes the report.

Usage:
    python -m eval.factorial.run                     # 3 runs of all 400 (about 1,200 agent calls)
    python -m eval.factorial.run --runs 1 --limit 20 # smoke test
    python -m eval.factorial.run --only GY-N01,X-MC2 # specific items
    LLM_PROFILE=local python -m eval.factorial.run   # the same questions against local models (Ollama)

Attempts go to results/attempts_<profile>.jsonl (attempts_openai.jsonl, attempts_local.jsonl), and
each row records the models that produced it. The judge is OpenAI in both profiles.

Cost: the 41-question golden set uses about 200k tokens per run including grading, so expect
roughly 2M tokens per run of this set. Check with --limit first.
"""
import argparse
import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from langchain_community.callbacks import get_openai_callback
from openai import LengthFinishReasonError

from eval.factorial.grading import (ANSWERABLE, INJECTION_PROMPT, NOT_FOUND_PROMPT, auto_check,
                                    passes_by_status)
from config.settings import settings
from eval.run_eval import JUDGE_PROMPT, judge
from src.agent.graph import run_agent
from src.llm import describe
from src.pipeline.guardrails import GuardrailError
from src.pipeline.retrieval import get_retriever

HERE = Path(__file__).resolve().parent
QUESTIONS = HERE / "questions.jsonl"
RESULTS = HERE / "results"
SYSTEM = describe()


def load_questions():
    if not QUESTIONS.exists():
        raise SystemExit("questions.jsonl is missing: run `python -m eval.factorial.build_questions` first")
    return [json.loads(line) for line in open(QUESTIONS, encoding="utf-8") if line.strip()]


def _supports(item):
    companies = {c for c in item["company"].split(",") if c}
    pages, evidence = set(item.get("pages", [])), [e.lower() for e in item.get("evidence", [])]

    def check(doc):
        # Same rule as eval/run_eval.py: right company, and a known source page or the key evidence
        return doc.metadata["company"] in companies and (
            doc.metadata["page"] in pages or any(e in doc.page_content.lower() for e in evidence))
    return check


def attempt(item, run, grader):
    started = time.perf_counter()
    row = {"id": item["id"], "run": run, "type": item["type"], "company": item["company"],
           "wording": item["wording"], "question": item["question"], "system": SYSTEM["profile"],
           "chat_model": SYSTEM["chat_model"]}
    with get_openai_callback() as usage:
        try:
            result = run_agent(item["question"])
            status, answer, route = result.status, result.answer, result.route
            sources, retrieved, rejected = result.sources, result.retrieved, result.rejected_citations
        except GuardrailError as e:
            status, answer, route, sources, retrieved, rejected = "blocked", str(e), "blocked", [], [], 0
        except LengthFinishReasonError as e:  # the model ran past its output limit: its failure, not an outage
            row.update(status="failed", route="failed", answer=f"{type(e).__name__}: {e}", correct=False,
                       judge_reason="output limit reached", seconds=time.perf_counter() - started)
            return row
        except Exception as e:  # an API or pipeline failure is recorded, not scored as a model error
            row.update(status="error", error=f"{type(e).__name__}: {e}", seconds=time.perf_counter() - started)
            return row
        row.update(status=status, route=route, answer=answer, cited_pages=sorted({s["page"] for s in sources}),
                   rejected_citations=rejected, seconds=time.perf_counter() - started)

        if item["type"] in ANSWERABLE or (item["type"] == "injection" and item.get("legit_expected")):
            supports = _supports(item)
            cited = {s["chunk_id"] for s in sources}
            row["retrieval_hit"] = any(supports(d) for d in retrieved)
            row["citation_hit"] = any(supports(d) for d in retrieved if d.metadata["chunk_id"] in cited)

        decided = passes_by_status(item, status)
        if item["type"] in ANSWERABLE:
            grade = grader.invoke(JUDGE_PROMPT.format(question=item["question"], expected=item["expected"], answer=answer))
            row["correct"] = status == "answered" and grade.correct
            row["judge_reason"] = grade.reason
        elif decided is not None:
            row["correct"] = decided
        elif item["type"] == "not_found":
            grade = grader.invoke(NOT_FOUND_PROMPT.format(why=item["expected"], question=item["question"], answer=answer))
            row["correct"], row["judge_reason"] = grade.correct, grade.reason
        else:  # injection carrying a real question, answered
            grade = grader.invoke(INJECTION_PROMPT.format(question=item["question"], expected=item["legit_expected"], answer=answer))
            row["correct"], row["judge_reason"] = grade.correct, grade.reason
        row["auto_correct"] = auto_check(item, status, answer)
    row["tokens"] = usage.total_tokens
    return row


def main(runs, limit, only, out, workers):
    items = load_questions()
    if only:
        wanted = set(only.split(","))
        items = [i for i in items if i["id"] in wanted]
    if limit:
        items = items[:limit]
    RESULTS.mkdir(exist_ok=True)
    path = RESULTS / out
    done = set()
    if path.exists():
        for line in open(path, encoding="utf-8"):
            r = json.loads(line)
            if r.get("status") != "error":  # errors are retried
                done.add((r["id"], r["run"]))
    todo = [(item, run) for run in range(1, runs + 1) for item in items if (item["id"], run) not in done]
    print(f"system: {SYSTEM}")
    print(f"{len(items)} questions x {runs} runs: {len(done)} attempts already in {path.name}, {len(todo)} to go")
    if not todo:
        return

    get_retriever()  # load the index once before the threads start
    grader = judge()
    lock, finished = threading.Lock(), [0]

    def work(job):
        row = attempt(*job, grader)
        with lock:
            with open(path, "a", encoding="utf-8") as f:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
            finished[0] += 1
            if finished[0] % 25 == 0 or finished[0] == len(todo):
                print(f"  {finished[0]}/{len(todo)}")
        return row

    with ThreadPoolExecutor(max_workers=workers) as pool:
        rows = list(pool.map(work, todo))
    errors = [r for r in rows if r["status"] == "error"]
    graded = [r for r in rows if "correct" in r]
    print(f"done: {sum(r['correct'] for r in graded)}/{len(graded)} correct this session, {len(errors)} errors "
          f"(rerun the same command to retry them)")
    print(f"analyse with: python -m eval.factorial.stats --attempts {out}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--limit", type=int, default=0, help="only the first N questions")
    parser.add_argument("--only", default="", help="comma-separated question ids")
    parser.add_argument("--out", default=f"attempts_{settings.llm_profile}.jsonl")
    parser.add_argument("--workers", type=int, default=6)
    args = parser.parse_args()
    main(args.runs, args.limit, args.only, args.out, args.workers)
