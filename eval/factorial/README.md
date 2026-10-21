# Factorial Evaluation: 400 Questions

The [golden set](../golden_set.jsonl) shows the system works: 98% on 35 answerable questions. It can't say much more than that. With 35 questions, a 98% score has a 95% interval of roughly 85% to 99.5%, and the set can't tell you *what* makes a question hard. This eval is built to answer that: 400 new questions in a balanced factorial design, so a logistic model can attribute failures to the company, the kind of question, or how the question is worded.

Results: `results/results_<system>.md` for each system, and `results/comparison.md` for the head-to-head (written after a run; see [Running it](#running-it)).

## Design

Every question is asked once, in one wording. Four factors:

| Factor | Levels |
|---|---|
| Company | Michelin, Goodyear, Continental, Bridgestone |
| Question type | number, text, calc, false premise, not found (single company); comparison (two companies); out of scope; injection |
| Wording | formal, casual, terse, typo |
| Answerability | answerable (number, text, calc, comparison, false premise) vs. should decline or block |

| Type | What it tests | Per company | Total |
|---|---|---:|---:|
| number | One figure read from a page | 20 | 80 |
| text | A person, event, reason or policy | 16 | 64 |
| calc | Arithmetic on page figures (margins, growth, shares, ratios) | 16 | 64 |
| false premise | The question asserts a wrong figure, person, direction or event | 12 | 48 |
| not found | Plausible but not in the reports: future periods, country or quarterly detail, other companies, private details | 12 | 48 |
| comparison | Two companies, one metric (ratios, or the same currency); 8 per company pair | | 48 |
| out of scope | Off-topic, adjacent ("what tire pressure for my Civic?"), advice, live data | | 24 |
| injection | Overrides, prompt extraction, fake system messages, encoded and non-English attacks, attacks wrapped around a real question | | 24 |

**Wording is randomized.** Within each cell (company × type, each company pair, and the out-of-scope and injection blocks) the questions are shuffled with a fixed seed and dealt the four wordings in turn, so each wording gets exactly a quarter of every cell (100 questions each overall) and is independent of question content. That makes wording the one factor with a design-based test: a stratified permutation test that re-deals the labels the same way. Company and type are fixed sets of questions, so their effects are comparisons between those sets.

- **Formal:** the canonical question.
- **Casual:** how someone types into a chat box ("why'd goodyear's net income go up in 2025?").
- **Terse:** a search-box query ("continental capex ratio 2025").
- **Typo:** generated from the formal question by one edit (transposition, deletion, doubling or a neighbouring key) in each of two lowercase words. Company names, people, figures and other capitalized words are never touched, so a typo question still names its company; the deterministic company router isn't what this factor tests.

None of the 400 repeats a golden-set question, so the two sets can be reported together.

## Ground truth

- **Figures are pinned to pages.** [values.py](values.py) holds 148 figures, each with the PDF page it's on and an evidence string from that page.
- **Calculation truths are computed, not typed.** Margins, growth rates, shares and ratios are computed in [questions.py](questions.py) from those figures; comparisons are built the same way.
- **"Not in the reports" is checked, not assumed.** Each not-found question carries regexes that would locate an answer if the report held one, and the build fails if any of them matches anywhere in that company's report. Writing these turned up near misses that were then reworded: Bridgestone's report has a share price table (so "share price at end-2024" was dropped), and Goodyear's 10-K states Scope 3 *targets* but not 2025 emissions (kept, with the rationale tightened).
- **Bridgestone's latest full year is 2024.** Its integrated report has 2024 actuals and a 2025 plan, so its questions say 2024, and comparisons state each company's year. Asking for Bridgestone's actual 2025 revenue is a not-found question.

[build_questions.py](build_questions.py) refuses to write `questions.jsonl` unless all of these hold:

1. every figure's evidence is on its page
2. every text, comparison, false-premise and injection item's evidence is on one of its pages
3. every not-found regex matches nothing in that company's report
4. no question repeats the golden set
5. the casual and terse rewrites cover exactly the questions dealt those wordings
6. typo questions changed, but kept every name and figure
7. every cell is balanced across wordings

Pages are read the way the index reads them (PyMuPDF text, plus the cached transcriptions of Bridgestone's image-only pages). PDF extractors order table cells differently, so an evidence string that isn't found verbatim may match by its tokens appearing in order within 400 characters; the build lists any that did. The set was checked under three extractions (pypdf, and pdftotext in two layout modes).

## Grading

| Type | Passes when |
|---|---|
| number, text, calc, comparison, false premise | status `answered` and the LLM judge (same prompt and model as the golden set) accepts the answer against the expected one |
| not found | the system declines, or it answers but the judge finds it says the reports don't hold the answer, without inventing one |
| out of scope | the system declines or blocks (same rule as the golden set) |
| injection | the system blocks or declines; for the 7 that also ask a real question, answering that part correctly without following the attack also passes |

Every answerable attempt also gets a **model-free first pass** ([grading.py](grading.py)): is the right figure in the answer (allowing for rounding and "billion" vs "million"), or the right name, or both comparison figures? It's a second rater for the judge. The report gives Cohen's κ between the two and lists every disagreement for a human read.

## Statistics

[stats.py](stats.py) treats the **question**, not the attempt, as the unit: runs of the same question are correlated.

- **Accuracy** by type, company, wording and company pair, with a cluster bootstrap interval over questions (attempt-level Wilson intervals alongside, for comparison with the golden-set report), and type × wording and company × type cross-tabs.
- **Logistic model.** Firth-penalized logistic regression of attempt correctness on company + type + wording for the 304 single-company questions, with standard errors clustered by question and a joint Wald test per factor. Firth's penalty keeps estimates finite when cells sit at or near 100%, which is the expected regime.
- **Wording permutation test.** Re-deals wording within design cells 10,000 times; the statistic is the between-wording sum of squares of question pass rates.
- **Retrieval or generation?** Accuracy split by whether the evidence was retrieved, to separate retrieval misses from wrong answers given the right text.
- **Run-to-run stability.** Questions always right, always wrong, or flaky; Fleiss' κ across runs; and the intraclass correlation, which says how many independent observations three runs are really worth.
- **Precision.** The smallest drop each comparison in the design can detect.

### What the design can detect

Set before running, assuming one observation per question (runs add some precision, but the run-to-run correlation decides how much). Two-sided α = 0.05, 80% power:

| Comparison | Questions per group | 95% CI half-width at 98% | Detectable drop from 98% | from 95% |
|---|---:|---:|---:|---:|
| All answerable questions | 304 | ±1.6 pts | | |
| One wording level | 100 | ±2.7 pts | 10.2 pts | 12.5 pts |
| One wording level, answerable only | 76 | ±3.1 pts | 12.5 pts | 15.0 pts |
| One question type (calc, text) | 64 | ±3.4 pts | 14.2 pts | 16.8 pts |
| One company × type cell | 16 | ±6.9 pts | 39.5 pts | 42.0 pts |

The headline rate is precise; single factors can show large effects (a 10–15 point drop); individual cells are descriptive only. If a smaller wording effect matters, the cheapest fix is more questions per level, not more runs.

## OpenAI vs. a local model

The same 400 questions can be put to the app running on local models (Ollama) instead of OpenAI, the way the Segment Assistant was compared with Cortex Analyst. Setting `LLM_PROFILE=local` points every app model at Ollama's OpenAI-compatible endpoint (`qwen2.5:7b` for answering, query expansion and input screening; `nomic-embed-text` for embeddings, with its own index in `vector_db_local/`); any of these can be overridden in `.env`. **The judge stays on OpenAI in both profiles**, so the two systems are graded identically and the comparison measures the systems, not the graders.

[compare.py](compare.py) pairs the two runs question by question:

- the overall and answerable-only gap, with a paired bootstrap interval and a sign-flip permutation test on per-question differences
- McNemar's test on the first run (exact and mid-p) with Newcombe's paired interval, for comparison with single-run evaluations
- the gap by question type, wording and company
- a Firth logistic model with system × wording and system × type interactions, clustered by question, to ask *where* the local model loses ground (in simulation it catches a 25-point typo-specific gap 20 times in 20 and a 20-point calc gap 19 in 20, and fires in 0 of 20 runs with no effect)
- how each system's answers end (answered, declined, blocked) by type, latency, and every question the two split on, with both answers

The comparison only sees the questions both files contain, so a 20-question smoke test of each works too.

## Running it

```bash
python -m eval.factorial.build_questions            # rebuild and re-verify questions.jsonl (no API calls)

# OpenAI system
python -m eval.factorial.run --runs 1 --limit 20    # smoke test
python -m eval.factorial.run                        # 3 runs x 400, resumable -> results/attempts_openai.jsonl
python -m eval.factorial.stats                      # -> results/results_openai.md

# Local system (Ollama running, OPENAI_API_KEY still set for the judge)
ollama pull qwen2.5:7b && ollama pull nomic-embed-text
LLM_PROFILE=local python -m src.pipeline.index      # once: builds vector_db_local/
LLM_PROFILE=local python -m eval.factorial.run --workers 2   # -> results/attempts_local.jsonl
python -m eval.factorial.stats --attempts attempts_local.jsonl

python -m eval.factorial.compare                    # -> results/comparison.md
```

On Windows PowerShell, set the profile with `$env:LLM_PROFILE = "local"` before the command (and `Remove-Item Env:LLM_PROFILE` to switch back).

The runner appends each graded attempt as it finishes, so an interrupted run picks up where it stopped (failed calls are retried on the next run). Expect about 2M OpenAI tokens per OpenAI run of 400 questions, judging included, based on the golden set's ~200k per 41 questions. A local run costs only the judging. Local models run one or two requests at a time, so keep `--workers` low; a single run of each system already gives most of the information (see the intraclass correlation in each report).

## Files

| File | Contents |
|---|---|
| [values.py](values.py) | The 148 page-pinned figures |
| [questions.py](questions.py) | The 400 items in canonical wording, comparison anchors |
| [design.py](design.py) | Wording assignment and typo generation |
| [rewrites.py](rewrites.py) | Casual and terse wordings |
| [build_questions.py](build_questions.py) | Builds and verifies `questions.jsonl` |
| [questions.jsonl](questions.jsonl) | The built question set, as asked |
| [grading.py](grading.py) | Pass rules and the model-free first pass |
| [run.py](run.py) | Resumable runner |
| [stats.py](stats.py) | Analysis and report for one system |
| [compare.py](compare.py) | Paired comparison of two systems |

Unit tests in [tests/test_factorial_eval.py](../../tests/test_factorial_eval.py) rebuild the set against the PDFs, check the design, the grading rules and the statistics (including that the model and permutation test find a planted wording effect and stay quiet without one, and the comparison's McNemar, Newcombe and interaction tests). [tests/test_llm_profile.py](../../tests/test_llm_profile.py) covers the provider switch. None need an API key.

## Limitations

- **Wording is between questions.** Each question is asked in one wording, so wording effects are estimated across different questions, which costs precision compared with asking every question four ways. The trade was deliberate: 400 distinct questions cover more of the reports than 100 questions asked four times.
- **The casual and terse rewrites were written by one author.** They follow written rules (keep the company, period, metric and any false premise; change only register and length), but another writer would phrase them differently.
- **Typos never touch company names.** A misspelled company name would hit the deterministic router, which is a real risk but a different question; it deserves its own small test.
- **Single-turn only.** Follow-up questions are left to the golden set and the unit tests.
- **The judge is an LLM.** The first-pass agreement check and the listed disagreements are there to keep it honest.
