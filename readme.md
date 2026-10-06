# Tire Industry Report Analyst: Grounded RAG with Verified Citations

Ask questions about the 2025 annual reports of **Michelin, Goodyear, Continental, and Bridgestone** (about 1,250 pages) and get answers that cite the exact page they came from. If the reports don't support an answer, the system says so instead of guessing.

![Report Q&A with verified sources](report_qa_demo.png)

## Why This Exists

A general-purpose chatbot or a web search can tell you roughly what Michelin earns. What it can't do reliably is pull an exact figure from a 556-page regulatory filing, tell you which page it came from, keep consolidated group figures separate from parent-company accounts, and refuse to answer when the document doesn't contain the fact. That is what an analyst working with internal or regulatory documents needs, and what this project is built and measured to do.

## Results

Measured on a hand-checked set of 38 questions, run 3 times (LLM steps are not fully deterministic). Full per-question results: [eval/results.md](eval/results.md).

| Metric | Mean | Range |
|---|---|---|
| Answer accuracy (32 answerable questions) | **97%** | 94–100% |
| Correct evidence retrieved | 99% | 97–100% |
| Correct evidence cited | 98% | 94–100% |
| Unanswerable, off-topic, and prompt-injection questions handled correctly | **100%** | 100% |
| Median latency | 3.6 s | |

The question set covers financial figures, leadership, workforce, and strategy for all four companies, cross-company comparisons, a parent-company vs. group distinction, questions the reports can't answer (future years, a company not covered), off-topic requests, a prompt-injection attempt, and a false-premise question ("Michelin's sales were €99 billion, right?").

## How It Works

```text
Question
  ├─ Input guardrails ── empty / oversized / prompt-injection → rejected before any model call
  ├─ Company detection ── deterministic name matching (a Goodyear question never sees Michelin's report)
  ├─ Query expansion ──── small model rewrites the question in annual-report terms ("employees" → "global workforce")
  ├─ Hybrid retrieval ─── BM25 keyword search + vector search, merged with reciprocal rank fusion;
  │                       comparisons retrieve per company so no company is crowded out
  ├─ Grounded answer ──── structured output: status, answer, and citations (chunk id + verbatim quote)
  └─ Citation verifier ── every citation must point to a retrieved chunk and its quote must appear there;
                          numbers must match exactly. No verified citation → no answer shown.
```

**Ingestion details that matter for financial documents:**
* **Page-level metadata** on every chunk (company, document, page), plus a contextual header so even a bare table is findable by company.
* **Tables kept intact** as Markdown (about 800 tables), so a figure stays attached to its row and year.
* **Image-only pages transcribed.** Bridgestone's report is almost entirely images (12,000 extractable characters across 57 pages). Those pages are transcribed once with a vision model and cached in `data/ocr/`, taking Bridgestone from 13 searchable chunks to 140 complete ones.
* **Entity scoping.** Michelin's filing includes the parent company's statutory accounts, whose figures differ from the consolidated group's. Those pages are tagged and only searched when a question asks for them.

## Guardrails

| Risk | Control |
|---|---|
| Hallucinated facts | Answers must cite retrieved text; the verifier rejects citations whose quote isn't in the source |
| Altered figures | A quote whose numbers don't match the source exactly is rejected (unit tested) |
| Unanswerable questions | Model returns `not_found` and says what's missing; tested with future years and an uncovered company |
| Off-topic requests | Returned as `out_of_scope` |
| Prompt injection | Pattern checks on input; retrieved text and web results are treated as data, not instructions |
| Wrong entity or period | Deterministic company filtering, parent-company page scoping, and prompt rules for year and entity |

## Run It

```bash
git clone https://github.com/livingdw67/michelin-rag.git
cd michelin-rag
echo OPENAI_API_KEY=sk-... > .env

# Docker (builds the index on first start)
docker compose up --build            # http://localhost:8501

# Or locally
pip install -r requirements.txt
python -m src.pipeline.index         # parse PDFs, build the vector + keyword indexes (~10 min first time)
streamlit run src/ui/app.py
```

```bash
pytest -q tests                      # unit tests: retrieval logic and guardrails (no API key needed)
python -m eval.run_eval --runs 3     # full evaluation (uses the API; about 200k tokens per run)
```

## Project Structure

```text
config/settings.py          Models, retrieval parameters, company/document registry
src/pipeline/documents.py   PDF parsing, table extraction, image-page transcription, chunking
src/pipeline/index.py       Builds the Chroma vector store and the BM25 chunk file
src/pipeline/retrieval.py   Company detection, query expansion, hybrid retrieval with rank fusion
src/pipeline/answer.py      Grounded answering with structured citations
src/pipeline/guardrails.py  Input checks and citation verification
src/ui/app.py               Streamlit app: report Q&A and live news sentiment
eval/                       Golden question set, evaluation runner, results
tests/                      Unit tests (run in GitHub Actions)
data/                       Annual report PDFs and cached page transcriptions
```

## Tech Stack

LangChain 1.x, OpenAI (`gpt-5.4-mini` for answers, `gpt-5.4-nano` for query expansion, `gpt-5.5` as evaluation grader, `text-embedding-3-small`), ChromaDB, BM25 (`rank_bm25`), PyMuPDF, Streamlit, Docker, pytest, GitHub Actions.

## Known Limitations and Next Steps

* **Multi-metric comparisons are the weakest area** (for example, two metrics across two companies in one question). Planned: an agent that splits a comparison into one sub-question per company and metric, then combines verified answers.
* **Footnote markers in tables** can attach to numbers (a €2.70 dividend with footnote 4 extracted as "2.704"). The prompt handles common cases; superscript-aware table parsing is planned.
* **Calculations** (ratios, growth rates) are done by the model; a calculator tool over extracted figures is planned so arithmetic is exact.
* **Single-turn questions.** Follow-up questions don't use conversation history yet.

*Originally built as a take-home assessment; rebuilt to add verified citations, guardrails, and a measured evaluation.*
