"""Generate a one-page competitive brief comparing two companies, with numbered citations.

Every input to the memo is already verified: metrics come from the cited metrics table and
qualitative points come from the citation-checked RAG pipeline. The memo may only cite those
sources, and its numbers are checked against them before it is returned.
"""
from concurrent.futures import ThreadPoolExecutor

from langchain_openai import ChatOpenAI

from config.settings import COMPANIES, settings
from src.pipeline.answer import answer_question
from src.pipeline.calculator import ungrounded_numbers
from src.pipeline.metrics import load_metrics
from src.pipeline.retrieval import get_retriever

TOPICS = {
    "strategy": "What are {company}'s main strategic priorities according to its 2025 annual report?",
    "headwinds": "What were the main headwinds or challenges {company} faced in 2025?",
    "outlook": "What outlook or guidance did {company} give for 2026?",
}

MEMO_PROMPT = """Write a one-page competitive brief comparing {a} and {b} for a strategy team.

Use ONLY the numbered sources below. After every factual claim, cite the source number in brackets, e.g. [3]. \
Do not use outside knowledge, do not convert currencies, and do not compute new figures. If a topic has no \
source for a company, say the reports don't cover it.

Structure (Markdown):
## {a} vs {b}: Competitive Brief
**Bottom line:** 2-3 sentences.
### Financial snapshot
A table of the metrics provided, with citations.
### Strategy
### Headwinds
### Outlook
### What to watch
2-3 bullets that follow from the sources.

Sources:
{sources}"""


def _gather(company):
    retriever = get_retriever()
    with ThreadPoolExecutor(max_workers=3) as pool:
        answers = dict(zip(TOPICS, pool.map(
            lambda q: answer_question(q.format(company=company), retriever=retriever), TOPICS.values())))
    return answers


def build_brief(company_a, company_b):
    if company_a == company_b or {company_a, company_b} - set(COMPANIES):
        raise ValueError("Choose two different companies.")
    metrics = load_metrics() or {"rows": []}
    sources, refs = [], []

    def add_source(text, doc, page):
        refs.append(f"{doc}, p. {page}")
        sources.append(f"[{len(refs)}] {text}")

    for company in (company_a, company_b):
        for row in metrics["rows"]:
            if row["company"] == company and row["status"] == "verified":
                add_source(f"{company} {row['label']} ({row.get('period', '')}): {row['display']}. "
                           f"Quote: \"{row['quote']}\"", row["doc"], row["page"])
            elif row["company"] == company and row["status"] == "calculated":
                sources.append(f"[calc] {company} {row['label']} ({row['period']}): {row['display']}, "
                               f"calculated from the cited figures")

    with ThreadPoolExecutor(max_workers=2) as pool:
        gathered = dict(zip((company_a, company_b), pool.map(_gather, (company_a, company_b))))
    for company, answers in gathered.items():
        for topic, result in answers.items():
            if result.status == "answered" and result.sources:
                first = result.sources[0]
                add_source(f"{company} {topic}: {result.answer}", first["doc"], first["page"])

    llm = ChatOpenAI(model=settings.chat_model, api_key=settings.openai_api_key, reasoning_effort="low")
    memo = llm.invoke(MEMO_PROMPT.format(a=company_a, b=company_b, sources="\n\n".join(sources))).content

    # Numbers in the memo must come from the sources (citation markers like [3] are small ints, ignored)
    unsupported = ungrounded_numbers(memo, "\n".join(sources))
    references = "\n".join(f"{i}. {ref}" for i, ref in enumerate(refs, 1))
    memo = f"{memo}\n\n---\n**Sources**\n\n{references}"
    if unsupported:
        memo += ("\n\n> ⚠️ Some figures in this brief could not be matched to a source and should be checked: "
                 + ", ".join(f"{v:g}" for v in unsupported))
    return memo, unsupported
