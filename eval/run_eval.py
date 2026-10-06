"""Score the RAG system against the hand-checked golden set.

LLM steps are not fully deterministic, so the suite runs several times and reports
the mean and range across runs, plus how often each question passed.

Usage:
    python -m eval.run_eval              # 3 runs, writes eval/results.md
    python -m eval.run_eval --runs 1     # quick check
"""
import argparse
import json
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from langchain_community.callbacks import get_openai_callback
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from config.settings import settings
from src.pipeline.answer import answer_question
from src.pipeline.guardrails import GuardrailError
from src.pipeline.retrieval import get_retriever

EVAL_DIR = Path(__file__).resolve().parent
ANSWERABLE = {"fact", "comparison", "false_premise"}

JUDGE_PROMPT = """Grade whether the ANSWER correctly answers the QUESTION, using EXPECTED as the reference.
- All key facts in EXPECTED must be present and consistent. Numbers must match (rounding and equivalent \
units like "€19.7 billion" vs "€19,676 million" are fine).
- Extra detail not mentioned in EXPECTED (dates, context, related figures) is fine unless it directly \
contradicts EXPECTED. Do not use outside knowledge to judge extra detail; it comes from the source reports.
- A figure for the asked-about metric that differs from EXPECTED makes the answer incorrect.
- For a false-premise question, the answer must reject the false claim and give the correct figure.

QUESTION: {question}
EXPECTED: {expected}
ANSWER: {answer}"""


class Grade(BaseModel):
    correct: bool
    reason: str


def judge():
    return ChatOpenAI(model=settings.judge_model, api_key=settings.openai_api_key).with_structured_output(Grade)


def run_case(case, retriever, grader):
    # Usage tracking lives in a context variable, so each worker thread needs its own callback
    with get_openai_callback() as usage:
        row = _run_case(case, retriever, grader)
    row["tokens"] = usage.total_tokens
    return row


def _run_case(case, retriever, grader):
    started = time.perf_counter()
    try:
        result = answer_question(case["question"], retriever=retriever)
        status, answer, sources, retrieved = result.status, result.answer, result.sources, result.retrieved
        rejected = result.rejected_citations
    except GuardrailError as e:
        status, answer, sources, retrieved, rejected = "blocked", str(e), [], [], 0
    row = {"id": case["id"], "type": case["type"], "status": status, "seconds": time.perf_counter() - started,
           "answer": answer, "cited_pages": sorted({s["page"] for s in sources}), "rejected_citations": rejected}

    if case["type"] in ANSWERABLE:
        companies = set(case["company"].split(","))
        pages = set(case["pages"])
        evidence = case.get("evidence", [])

        def supports(doc):
            # A chunk supports the answer if it is from the right company and either is a known
            # source page or contains the key evidence (many facts are repeated on several pages)
            return doc.metadata["company"] in companies and (
                doc.metadata["page"] in pages or any(e.lower() in doc.page_content.lower() for e in evidence))

        cited_ids = {s["chunk_id"] for s in sources}
        row["retrieval_hit"] = any(supports(d) for d in retrieved)
        row["citation_hit"] = any(supports(d) for d in retrieved if d.metadata["chunk_id"] in cited_ids)
        grade = grader.invoke(JUDGE_PROMPT.format(question=case["question"], expected=case["expected"], answer=answer))
        row["correct"] = status == "answered" and grade.correct
        row["judge_reason"] = grade.reason
    elif case["type"] in ("not_found", "out_of_scope"):
        row["correct"] = status in ("not_found", "out_of_scope", "blocked")
    elif case["type"] == "injection":
        row["correct"] = status == "blocked"
    return row


def rate(rows, key):
    vals = [r[key] for r in rows if key in r]
    return sum(vals) / len(vals) if vals else float("nan")


def summarize(rows):
    answerable = [r for r in rows if r["type"] in ANSWERABLE]
    traps = [r for r in rows if r["type"] not in ANSWERABLE]
    return {
        "Answer accuracy (answerable questions)": rate(answerable, "correct"),
        "Retrieval hit rate (evidence retrieved)": rate(answerable, "retrieval_hit"),
        "Citation hit rate (evidence cited)": rate(answerable, "citation_hit"),
        "Declined or blocked correctly (unanswerable, off-topic, injection)": rate(traps, "correct"),
    }


def main(runs):
    cases = [json.loads(line) for line in open(EVAL_DIR / "golden_set.jsonl", encoding="utf-8") if line.strip()]
    retriever, grader = get_retriever(), judge()
    all_runs = []
    for n in range(runs):
        with ThreadPoolExecutor(max_workers=6) as pool:
            all_runs.append(list(pool.map(lambda c: run_case(c, retriever, grader), cases)))
        accuracy = summarize(all_runs[-1])["Answer accuracy (answerable questions)"]
        print(f"run {n + 1}/{runs}: answer accuracy {accuracy:.0%}")

    per_run = [summarize(rows) for rows in all_runs]
    flat = [r for rows in all_runs for r in rows]
    table = ["| Metric | Mean | Range across runs |", "|---|---|---|"]
    for metric in per_run[0]:
        vals = [p[metric] for p in per_run]
        table.append(f"| {metric} | {sum(vals) / len(vals):.0%} | {min(vals):.0%} – {max(vals):.0%} |")
    table += [
        f"| Citations rejected by the verifier (all runs) | {sum(r['rejected_citations'] for r in flat)} | |",
        f"| Median latency per question | {sorted(r['seconds'] for r in flat)[len(flat) // 2]:.1f}s | |",
        f"| Tokens per full run (answers + grading) | {sum(r['tokens'] for r in flat) / runs:,.0f} | |",
    ]

    per_question = ["| ID | Type | Question | Passed | Notes (most recent failure) |", "|---|---|---|---|---|"]
    for i, case in enumerate(cases):
        results = [rows[i] for rows in all_runs]
        failures = [r for r in results if not r["correct"]]
        note = (failures[-1].get("judge_reason") or failures[-1]["status"]) if failures else ""
        note = " ".join(note.replace("|", "/").split())[:150]
        question = case["question"].replace("|", "/")
        per_question.append(f"| {case['id']} | {case['type']} | {question} | "
                            f"{sum(r['correct'] for r in results)}/{runs} | {note} |")

    header = (f"# Evaluation Results\n\n{len(cases)} questions × {runs} runs · answer model `{settings.chat_model}` · "
              f"query expansion `{settings.rewrite_model}` · grader `{settings.judge_model}`\n\n"
              "LLM steps are not fully deterministic, so the suite runs several times and reports the mean "
              "and range.\n")
    report = "\n".join([header, *table, "", "## Per-question results", "", *per_question]) + "\n"
    (EVAL_DIR / "results.md").write_text(report, encoding="utf-8")
    (EVAL_DIR / "results.json").write_text(json.dumps(all_runs, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\n".join(table))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=3)
    main(parser.parse_args().runs)
