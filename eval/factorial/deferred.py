"""Answer now, grade later, on a budget: the same attempts as eval.factorial.run, with the judge deferred.

Answering and grading are separate passes, so a local model can answer without the GPU swapping models for a
judge, a run can be priced before anything is graded, and both systems can be graded by one judge chosen
after the fact. Every OpenAI call is metered and priced, and --max-dollars stops starting new work at a cap.

    python -m eval.factorial.deferred answer [--runs 1] [--only IDS] [--workers 4] [--max-dollars 3]
        -> results/pending_<profile>.jsonl (resumable; each row keeps the prompt the judge would have seen)
    python -m eval.factorial.deferred grade --file pending_openai.jsonl [--max-dollars 1]
        -> results/attempts_<profile>.jsonl, the file stats.py and compare.py read

Grading applies the rules of eval.factorial.run.attempt: an answerable item passes only if it was answered
and the judge accepts it (so unanswered ones need no judge call); not-found and injection items take the
judge's verdict. An attempt whose model ran past its output limit is the system's failure, not an outage, so
it is graded wrong rather than dropped or retried (older files record it as an error; those are converted,
and a retry recorded after it is ignored). Other errors are retried by rerunning `answer`.
"""
import argparse
import json
import threading
from concurrent.futures import ThreadPoolExecutor

from langchain_core.callbacks import get_usage_metadata_callback

from eval.factorial import run as R
from eval.factorial.grading import ANSWERABLE
from eval.factorial.split import load_split
from eval.run_eval import Grade

PENDING = "PENDING_JUDGE"
RAN_AWAY = "LengthFinishReasonError"
PRICES = {"gpt-5.5": (5.0, 30.0), "gpt-5.4-mini": (0.75, 4.5), "gpt-5.4-nano": (0.20, 1.25)}  # $ per 1M in, out


def dollars(usage):
    """Cost of a usage_metadata dict ({model: usage}); unpriced (local) models cost nothing."""
    total = 0.0
    for model, u in usage.items():
        price = next((p for name, p in PRICES.items() if model.startswith(name)), None)
        if price:
            total += u.get("input_tokens", 0) * price[0] / 1e6 + u.get("output_tokens", 0) * price[1] / 1e6
    return total


def ran_away(row):
    """The model ran past its output limit: a scored failure, not an outage to retry."""
    return row["status"] == "error" and row.get("error", "").startswith(RAN_AWAY)


def read_rows(path):
    """Rows of a JSONL file, skipping a last line cut short by a crash or power loss (that attempt reruns)."""
    rows = []
    for line in open(path, encoding="utf-8"):
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            print(f"skipping a partial line in {path.name}")
    return rows


class Deferred:
    """Stands in for the judge: remembers the prompt and returns a placeholder grade."""

    def __init__(self):
        self.prompt = None

    def invoke(self, prompt):
        self.prompt = prompt
        return Grade(correct=False, reason=PENDING)


def answer(runs, only, workers, max_dollars, subset=None, out=None):
    items = R.load_questions()
    if only:
        wanted = set(only.split(","))
        items = [i for i in items if i["id"] in wanted]
    if subset:  # "dev" or "heldout" (eval/factorial/split.py)
        wanted = set(load_split()[subset])
        items = [i for i in items if i["id"] in wanted]
    path = R.RESULTS / (out or f"pending_{R.SYSTEM['profile']}.jsonl")
    R.RESULTS.mkdir(exist_ok=True)
    done, spent = set(), [0.0]
    if path.exists():
        rows = read_rows(path)
        done = {(r["id"], r["run"]) for r in rows if r["status"] != "error" or ran_away(r)}
        spent[0] = sum(r.get("usd", 0) for r in rows)
    todo = [(item, run) for run in range(1, runs + 1) for item in items if (item["id"], run) not in done]
    print(f"system: {R.SYSTEM}\n{len(todo)} attempts to go, {len(done)} already in {path.name}, "
          f"${spent[0]:.3f} spent so far (cap ${max_dollars:.2f})", flush=True)
    R.get_retriever()
    lock, finished = threading.Lock(), [0]

    def work(job):
        if spent[0] >= max_dollars:
            return None
        stub = Deferred()
        with get_usage_metadata_callback() as cb:
            row = R.attempt(*job, stub)
        row["usd"] = dollars(cb.usage_metadata)
        if stub.prompt is not None:
            row.update(correct=None, judge_reason=PENDING, judge_prompt=stub.prompt)
        with lock:
            spent[0] += row["usd"]
            with open(path, "a", encoding="utf-8") as f:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
            finished[0] += 1
            print(f"  {finished[0]}/{len(todo)} {row['id']} {row['status']} {row.get('seconds', 0):.0f}s "
                  f"${spent[0]:.3f}", flush=True)
        return row

    with ThreadPoolExecutor(max_workers=workers) as pool:
        rows = [r for r in pool.map(work, todo) if r is not None]
    skipped = len(todo) - len(rows)
    print(f"done: {len(rows)} attempts, {sum(r['status'] == 'error' for r in rows)} errors (rerun to retry), "
          f"${spent[0]:.3f} spent" + (f"; cap reached, {skipped} not started" if skipped else ""))


def grade(file, max_dollars, out=None):
    src = R.RESULTS / file
    rows = read_rows(src)
    # The first scored outcome of each attempt counts. Outages are skipped (their retry is the attempt); a
    # run past the output limit is the system failing, so a later retry of it doesn't get a second chance.
    ok = {}
    for r in rows:
        key = (r["id"], r["run"])
        if key in ok or (r["status"] == "error" and not ran_away(r)):
            continue
        ok[key] = r
        if ran_away(r):
            ok[key] = {**r, "status": "failed", "answer": r["error"], "judge_reason": "output limit reached",
                       "correct": False}
    out = R.RESULTS / (out or f"attempts_{rows[0]['system']}.jsonl")
    graded = set()
    if out.exists():
        graded = {(r["id"], r["run"]) for r in read_rows(out)}
    rows = [r for key, r in ok.items() if key not in graded]
    print(f"{len(rows)} rows to grade from {src.name} into {out.name} ({len(graded)} already there), "
          f"judge {R.settings.judge_model}", flush=True)
    grader, lock, spent = R.judge(), threading.Lock(), [0.0]

    def work(r):
        prompt = r.pop("judge_prompt", None)
        if prompt is not None and r["status"] != "failed":
            if r["type"] in ANSWERABLE and r["status"] != "answered":
                r.update(correct=False, judge_reason="not answered")
            elif spent[0] >= max_dollars:
                return None
            else:
                with get_usage_metadata_callback() as cb:
                    g = grader.invoke(prompt)
                r["judge_usd"] = dollars(cb.usage_metadata)
                r["correct"] = (r["status"] == "answered" and g.correct) if r["type"] in ANSWERABLE else g.correct
                r["judge_reason"] = g.reason
        with lock, open(out, "a", encoding="utf-8") as f:
            spent[0] += r.get("judge_usd", 0)
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
        return r

    with ThreadPoolExecutor(max_workers=6) as pool:
        rows = [r for r in pool.map(work, rows) if r is not None]
    print(f"graded {len(rows)}: {sum(bool(r['correct']) for r in rows)} correct, judge cost ${spent[0]:.3f}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("mode", choices=["answer", "grade"])
    p.add_argument("--runs", type=int, default=1)
    p.add_argument("--only", default="")
    p.add_argument("--workers", type=int, default=2)
    p.add_argument("--file", default="pending_local.jsonl")
    p.add_argument("--max-dollars", type=float, default=float("inf"))
    p.add_argument("--subset", choices=["dev", "heldout"], help="answer only the development or held-out questions")
    p.add_argument("--out", help="output file in results/ (default pending_<profile>.jsonl / attempts_<system>.jsonl)")
    a = p.parse_args()
    if a.mode == "answer":
        answer(a.runs, a.only, a.workers, a.max_dollars, a.subset, a.out)
    else:
        grade(a.file, a.max_dollars, a.out)
