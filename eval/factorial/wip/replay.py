"""Replay development questions through the answer step and show the model's raw structured output.

    LLM_PROFILE=local python -m eval.factorial.wip.replay ID [ID ...]
"""
import json
import sys

from langchain_core.prompts import ChatPromptTemplate

from eval.factorial.split import load_split
from src.pipeline.answer import HUMAN_PROMPT, GroundedAnswer, format_context, get_llm, system_prompt
from src.pipeline.guardrails import quote_in_text
from src.pipeline.retrieval import get_retriever

questions = {q["id"]: q for q in map(json.loads, open("eval/factorial/questions.jsonl", encoding="utf-8"))}
dev = set(load_split()["dev"])
retriever = get_retriever()
chain = ChatPromptTemplate.from_messages([("system", system_prompt()), ("human", HUMAN_PROMPT)]) | \
    get_llm().with_structured_output(GroundedAnswer)

for qid in sys.argv[1:]:
    assert qid in dev, f"{qid} is held out"
    q = questions[qid]
    docs = retriever.retrieve(q["question"])
    by_id = {d.metadata["chunk_id"]: d for d in docs}
    hits = [d.metadata["chunk_id"] for d in docs
            if d.metadata["page"] in q.get("pages", []) or any(e.lower() in d.page_content.lower() for e in q.get("evidence", []))]
    r = chain.invoke({"question": q["question"], "context": format_context(docs)})
    print(f"\n=== {qid} [{q['type']}] {q['question']}\n    expected: {q['expected']}\n    evidence chunks: {hits}")
    print(f"    retrieved ids: {[d.metadata['chunk_id'] for d in docs]}")
    print(f"    status: {r.status}\n    answer: {' '.join(r.answer.split())[:300]}")
    for c in r.citations:
        c = c.model_copy(update={"chunk_id": c.chunk_id.strip().strip("[]\"'` ").strip()})
        doc = by_id.get(c.chunk_id)
        ok = doc is not None and quote_in_text(c.quote, doc.page_content)
        print(f"    cite {c.chunk_id!r} known={doc is not None} verbatim={ok}: {c.quote[:140]!r}")
