"""Score development runs for free: the model-free check for answerable questions, status rules for the rest.

    python -m eval.factorial.wip.dev_score attempts_local.jsonl pending_local_r2a_dev.jsonl ...

Answerable: answered and the model-free first pass finds the right figure or name. Should-decline: the
status rule; a not-found or injection question the system answered can't be scored without the judge, so it is
counted separately. The same rule is applied to every file, so rounds compare like for like.
"""
import json
import sys
from collections import Counter

from eval.factorial.grading import ANSWERABLE, passes_by_status
from eval.factorial.split import load_split

RESULTS = "eval/factorial/results/"
questions = {q["id"]: q for q in map(json.loads, open("eval/factorial/questions.jsonl", encoding="utf-8"))}
dev = set(load_split()["dev"])


def first_outcomes(path):
    rows = {}
    for line in open(RESULTS + path, encoding="utf-8"):
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue
        key = (r["id"], r["run"])
        if r["id"] in dev and key not in rows and (r["status"] != "error" or "LengthFinish" in r.get("error", "")):
            rows[key] = r
    return list(rows.values())


for path in sys.argv[1:]:
    rows = first_outcomes(path)
    score, unjudged, stages = Counter(), 0, Counter()
    for r in rows:
        if r["type"] in ANSWERABLE:
            ok = r["status"] == "answered" and bool(r.get("auto_correct"))
            score["answerable"] += ok
            score["answerable_n"] += 1
            stages[r["status"] if r.get("route") != "classifier" else "classifier"] += 1
        else:
            decided = passes_by_status(questions[r["id"]], r["status"] if r["status"] != "error" else "failed")
            if decided is None:
                unjudged += 1
            else:
                score["decline"] += decided
                score["decline_n"] += 1
    print(f"{path}: {len(rows)} dev rows | answerable {score['answerable']}/{score['answerable_n']} "
          f"| decline {score['decline']}/{score['decline_n']} (+{unjudged} need the judge) | answerable ended: {dict(stages)}")
