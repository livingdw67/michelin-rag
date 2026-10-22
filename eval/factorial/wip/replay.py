"""Replay development questions through the answer step (retrieval, model, calculator, citation check).

    LLM_PROFILE=local python -m eval.factorial.wip.replay ID [ID ...]
"""
import json
import sys

from eval.factorial.split import load_split
from src.pipeline.answer import answer_question
from src.pipeline.retrieval import get_retriever

questions = {q["id"]: q for q in map(json.loads, open("eval/factorial/questions.jsonl", encoding="utf-8"))}
dev = set(load_split()["dev"])
retriever = get_retriever()

for qid in sys.argv[1:]:
    assert qid in dev, f"{qid} is held out"
    q = questions[qid]
    r = answer_question(q["question"], retriever=retriever)
    print(f"\n=== {qid} [{q['type']}] {q['question']}\n    expected: {q['expected']}")
    print(f"    status: {r.status} | verified citations {len(r.sources)}, rejected {r.rejected_citations}")
    print(f"    answer: {' '.join(r.answer.split())[:400]}")
