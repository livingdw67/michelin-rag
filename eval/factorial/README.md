# Factorial Evaluation: 400 Questions

The [golden set](../golden_set.jsonl) shows the system works: 98% on 35 answerable questions. It can't say much more than that. With 35 questions, a 98% score has a 95% interval of roughly 85% to 99.5%, and the set can't tell you *what* makes a question hard. This eval is built to answer that: 400 new questions in a balanced factorial design, so a logistic model can attribute failures to the company, the kind of question, or how the question is worded.

**Results so far are [below](#results).** Full reports: `results/results_<system>.md` for each system, and `results/comparison*.md` for the head-to-head.

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

The same 400 questions can be put to the app running on local models (Ollama) instead of OpenAI, the way the Segment Assistant was compared with Cortex Analyst. Setting `LLM_PROFILE=local` points every app model at Ollama's OpenAI-compatible endpoint (`qwen3:8b` with thinking off for answering, query expansion and input screening, since round 2; round 1 used `qwen2.5:7b`; `nomic-embed-text` for embeddings, with its own index in `vector_db_local/`); any of these can be overridden in `.env`. **The judge stays on OpenAI in both profiles**, so the two systems are graded identically and the comparison measures the systems, not the graders.

[compare.py](compare.py) pairs the two runs question by question:

- the overall and answerable-only gap, with a paired bootstrap interval and a sign-flip permutation test on per-question differences
- McNemar's test on the first run (exact and mid-p) with Newcombe's paired interval, for comparison with single-run evaluations
- the gap by question type, wording and company
- a Firth logistic model with system × wording and system × type interactions, clustered by question, to ask *where* the local model loses ground (in simulation it catches a 25-point typo-specific gap 20 times in 20 and a 20-point calc gap 19 in 20, and fires in 0 of 20 runs with no effect)
- how each system's answers end (answered, declined, blocked) by type, latency, and every question the two split on, with both answers

The comparison only sees the questions both files contain, so a 20-question smoke test of each works too.

### Results

**Why 300 questions are held out.** Round 1 ran all 400 questions once per system. Before anything was tuned, [split.py](split.py) set aside a quarter of every design cell (100 questions) for development and held out the other 300 ([split.json](split.json)). The split uses the design and a fixed seed, not the results. Fixes to the local system are tuned on the 100 only, and the 300 are scored once per round, so a tuned system is judged on questions it wasn't tuned on.

**Round 1: gpt-5.4-mini against an untuned qwen2.5:7b.** One run each, both graded by the same gpt-5.4-mini judge ([full report](results/comparison_heldout.md)).

| 300 held-out questions | Questions | gpt-5.4-mini | qwen2.5:7b (local) | Gap (95% interval) |
|---|---:|---:|---:|---|
| All | 300 | **82.3%** | **25.7%** | +56.7 pts (+51.0 to +62.3) |
| Answerable | 228 | 77.2% | 2.2% | +75.0 pts (+69.3 to +80.7) |
| Should decline or block | 72 | 98.6% | 100% | |

All 400 questions give nearly the same scores (82.2% and 25.2%). Median time per question was 5.0 s against 21.1 s.

- **The local model's score is almost all refusals.** Of the 228 answerable questions it answered 7, said `not_found` to 185 and `out_of_scope` to 28; the rest failed or were blocked. 72 of its 77 passes are questions where declining is the right answer. Round 2 below traces much of this to fixable problems, so round 1 measures an untuned setup more than the model's ceiling.
- **The OpenAI system is weakest on comparisons (41.7%) and false premises (66.7%).** It scores 91.7% on single figures, 89.6% on text questions and 81.2% on calculations.
- **82% and the golden set's 98% aren't like for like.** The 400 questions weight hard types equally and add casual, terse and misspelled wordings. They were also graded by a cheaper judge (gpt-5.4-mini rather than gpt-5.5, to fit the budget) over one run rather than three.

| Test | Why it's needed | What it says here | Assumptions and checks |
|---|---|---|---|
| Paired bootstrap interval | Both systems answer the same questions, so the gap should be measured question by question and not as two separate averages | The gap is between 51 and 62 points | Questions are resampled as independent units. They are one designed set, so this describes questions like these, not all possible questions. With one run per system it leaves out run-to-run variation |
| McNemar's exact test | Questions both systems get right or wrong can't say which is better; only the questions they split on can | They split on 172 questions and gpt-5.4-mini won 171. If the systems were equally good each split would be a coin flip, and a result this lopsided would essentially never happen (p < 0.0001) | Pairs are independent across questions. The exact version has no minimum sample size |
| Firth logistic model with interactions | The gap might depend on the kind of question or its wording | It does. System × type: χ²(4) = 81.5, p < 0.001; the local model catches up only on not-found questions. System × wording: χ²(3) = 15.7, p = 0.001, driven by terse queries (odds ratio 0.10, 95% 0.02 to 0.49) | Errors are clustered by question, on 228 single-company questions. With the local model passing about 2% of answerable questions, effect sizes are very imprecise (one odds ratio is 554, interval 92 to 3,338), so read the direction and not the size. Interaction terms aren't adjusted for multiple comparisons |
| Cohen's κ against the model-free grader | The judge is an LLM, and here the same model as the OpenAI system, so it could favor that system's answers | On the 228 answerable questions the judge and the model-free check agree 95.2% of the time for gpt-5.4-mini (κ = 0.85) and 99.6% for the local model (κ = 0.91). Every disagreement is the judge failing an answer the check passed (11 and 1). Scored with no LLM at all, the systems split 181 to 0 (82.0% against 2.6%), so the result doesn't depend on the judge | The model-free check only looks for the right figure or name, so it's more lenient than the judge. κ carries little information when one system almost never passes |

**Round 2: tuning the local system.** Scored on the 76 answerable development questions with the model-free check, which costs nothing:

| Step | What changed | Passed (of 76) |
|---|---|---:|
| Round 1 | qwen2.5:7b, untuned | 0 |
| 2a, 2b | The verifier accepts cited chunk ids with brackets; for the local system only, a prompt rule against answering `not_found` when the answer was found, a named company overrules the classifier's off-topic verdict, and temperature 0 | 25, then 30 |
| 2c | The model writes the arithmetic and code evaluates it, only if every figure is in the excerpts; citations are built in code | 34 |
| 2d | qwen3:8b, thinking off, 12k context | 47 |
| Reference | gpt-5.4-mini | 65 |

These are development scores on the questions the fixes were tuned on, so they could run optimistic. The shared verifier changes only add verified citations, and they never changed a gpt-5.4-mini answer, so round 1's OpenAI scores stand.

**Round 2 on the 300 held-out questions: qwen3:8b against gpt-5.4-mini.** The 2d system answered each held-out question once, graded by the same gpt-5.4-mini judge as round 1 ([full report](results/comparison_heldout_r2.md)).

| 300 held-out questions | Questions | gpt-5.4-mini | qwen3:8b (local, round 2) | qwen2.5:7b (round 1) |
|---|---:|---:|---:|---:|
| All | 300 | **82.3%** | **61.7%** | 25.7% |
| Answerable | 228 | 77.2% | 57.5% | 2.2% |
| Should decline or block | 72 | 98.6% | 75.0% | 100% |

gpt-5.4-mini leads by 20.7 points (95% interval +15.0 to +26.7). Median time per question was 5.0 s against 32.2 s.

- **Tuning carried over to questions it wasn't tuned on.** By the model-free check, the 2d system passed 61.8% of the answerable development questions (47 of 76) and 64.5% of the answerable held-out ones (147 of 228), so there's no sign it was fitted to the 100.
- **The weakness flipped.** Round 1 refused nearly everything; round 2 answers nearly everything. It answered 214 of the 228 answerable questions, but also 20 of the 36 questions the reports can't answer (gpt-5.4-mini answered 5), and it answered 31 of the 36 false-premise questions but got 20 of them wrong. Not-found questions are where it loses most: 55.6% against 97.2%.
- **Comparisons are close.** Both systems are weak there: 36.1% for qwen3 and 41.7% for gpt-5.4-mini (difference 95% interval −13.9 to +25.0 points).
- **What to fix next:** the decline decision. A check that the excerpts actually contain the asked-for figure before answering, and that a question's stated figure matches the report, would target both not-found and false-premise misses.

| Test | Why it's needed | What it says here | Assumptions and checks |
|---|---|---|---|
| McNemar's exact test, round 2 against round 1 | Both local rounds answered the same 300 questions, so the improvement can be tested pair by pair | Round 2 got 126 questions right that round 1 missed, and missed 18 that round 1 got right (p < 0.0001): the tuning helped on questions it never saw | Pairs are independent across questions. The two rounds also differ in model (qwen2.5 to qwen3), so this credits the whole round 2 system, not each change |
| McNemar's exact test, gpt-5.4-mini against qwen3 | Only the questions the systems split on can say which is better | They split on 92: gpt-5.4-mini won 77 and qwen3 15 (p < 0.0001) | As above; the exact version has no minimum sample size |
| Firth logistic model with interactions | Is qwen3's gap the same everywhere? | Mostly. Neither system × type (χ²(4) = 7.6, p = 0.11) nor system × wording (χ²(3) = 3.9, p = 0.27) is significant as a set, but one term stands out: qwen3's odds fall much further on not-found questions (odds ratio 0.11, 95% 0.02 to 0.55, p = 0.007) | 228 single-company questions, errors clustered by question. Picking out one term after the set test isn't significant is exploratory; the not-found gap shows plainly in the raw rates too (20 of 36 answered) |
| Cohen's κ against the model-free grader | The judge is an LLM, and the same model as the OpenAI system | For qwen3 the judge and the model-free check agree on 88.6% of answerable questions (κ = 0.76); the judge failed 21 answers the check passed and passed 5 it failed. Scored with no LLM at all, gpt-5.4-mini still leads on answerable questions, 187 to 147, splitting 53 to 13 (p < 0.0001) | The model-free check only looks for the right figure or name, so it can't see a wrong premise accepted around a correct number; false premises are the largest group of the 21 (9) |

**How the run was done.** The laptop had no charger, so the 300 were answered over three battery charges by [wip/run_heldout_on_battery.py](wip/run_heldout_on_battery.py). It runs the questions in a seeded order stratified by type and company ([order](results/local_r2_heldout_order.json)), so the finished set kept the mix of the full 300 at every stop. Each question was answered once; six attempts lost their connection to the local model server and were retried, which the grader handles as outages, not answers.

## Running it

```bash
python -m eval.factorial.build_questions            # rebuild and re-verify questions.jsonl (no API calls)

# OpenAI system
python -m eval.factorial.run --runs 1 --limit 20    # smoke test
python -m eval.factorial.run                        # 3 runs x 400, resumable -> results/attempts_openai.jsonl
python -m eval.factorial.stats                      # -> results/results_openai.md

# Local system (Ollama running, OPENAI_API_KEY still set for the judge)
ollama pull qwen3:8b && ollama pull nomic-embed-text
ollama create qwen3-8b-12k -f config/ollama/qwen3-8b-12k.Modelfile   # 12k context; the 4k default truncates prompts
LLM_PROFILE=local python -m src.pipeline.index      # once: builds vector_db_local/
LLM_PROFILE=local python -m eval.factorial.run --workers 2 --out attempts_local_new.jsonl
# attempts_local.jsonl already holds round 1 (qwen2.5), so a new run needs its own --out
python -m eval.factorial.stats --attempts attempts_local_new.jsonl

python -m eval.factorial.compare --b attempts_local_new.jsonl --out comparison_new   # -> results/comparison_new.md
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
