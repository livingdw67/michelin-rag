# Factorial Evaluation Results

15 questions × 1 run(s) = 15 graded attempts · openai system, answer model `gpt-5.4-mini`.
Design and method: [README](../README.md). Question-level intervals treat each question as the unit, since runs of the same question are not independent.

## Headline

| Block | Questions | Accuracy (attempts) | Wilson 95% | Question mean | Cluster bootstrap 95% |
|---|---:|---:|---|---:|---|
| Answerable (number, text, calc, comparison, false premise) | 10 | 80.0% | 49.0% – 94.3% | 80.0% | 60.0% – 100.0% |
| Should decline or block (not found, out of scope, injection) | 5 | 100.0% | 56.6% – 100.0% | 100.0% | 100.0% – 100.0% |
| All | 15 | 86.7% | 62.1% – 96.3% | 86.7% | 66.7% – 100.0% |

## By question type

| Type | Questions | Attempts | Accuracy | Wilson 95% (attempts) | Question mean | Cluster bootstrap 95% |
|---|---:|---:|---:|---|---:|---|
| number | 2 | 2 | 100.0% | 34.2% – 100.0% | 100.0% | 100.0% – 100.0% |
| text | 2 | 2 | 100.0% | 34.2% – 100.0% | 100.0% | 100.0% – 100.0% |
| calc | 2 | 2 | 50.0% | 9.5% – 90.5% | 50.0% | 0.0% – 100.0% |
| comparison | 2 | 2 | 100.0% | 34.2% – 100.0% | 100.0% | 100.0% – 100.0% |
| false_premise | 2 | 2 | 50.0% | 9.5% – 90.5% | 50.0% | 0.0% – 100.0% |
| not_found | 2 | 2 | 100.0% | 34.2% – 100.0% | 100.0% | 100.0% – 100.0% |
| out_of_scope | 1 | 1 | 100.0% | 20.7% – 100.0% | 100.0% | n/a – n/a |
| injection | 2 | 2 | 100.0% | 34.2% – 100.0% | 100.0% | 100.0% – 100.0% |

## By company (single-company questions)

| Company | Questions | Attempts | Accuracy | Wilson 95% (attempts) | Question mean | Cluster bootstrap 95% |
|---|---:|---:|---:|---|---:|---|
| Michelin | 2 | 2 | 100.0% | 34.2% – 100.0% | 100.0% | 100.0% – 100.0% |
| Goodyear | 3 | 3 | 100.0% | 43.8% – 100.0% | 100.0% | 100.0% – 100.0% |
| Continental | 2 | 2 | 50.0% | 9.5% – 90.5% | 50.0% | 0.0% – 100.0% |
| Bridgestone | 3 | 3 | 66.7% | 20.8% – 93.9% | 66.7% | 32.5% – 100.0% |

## By wording

All 400 questions:

| Wording | Questions | Attempts | Accuracy | Wilson 95% (attempts) | Question mean | Cluster bootstrap 95% |
|---|---:|---:|---:|---|---:|---|
| formal | 5 | 5 | 60.0% | 23.1% – 88.2% | 60.0% | 20.0% – 100.0% |
| casual | 4 | 4 | 100.0% | 51.0% – 100.0% | 100.0% | 100.0% – 100.0% |
| terse | 4 | 4 | 100.0% | 51.0% – 100.0% | 100.0% | 100.0% – 100.0% |
| typo | 2 | 2 | 100.0% | 34.2% – 100.0% | 100.0% | 100.0% – 100.0% |

Answerable questions only:

| Wording | Questions | Attempts | Accuracy | Wilson 95% (attempts) | Question mean | Cluster bootstrap 95% |
|---|---:|---:|---:|---|---:|---|
| formal | 2 | 2 | 0.0% | 0.0% – 65.8% | 0.0% | 0.0% – 0.0% |
| casual | 3 | 3 | 100.0% | 43.8% – 100.0% | 100.0% | 100.0% – 100.0% |
| terse | 3 | 3 | 100.0% | 43.8% – 100.0% | 100.0% | 100.0% – 100.0% |
| typo | 2 | 2 | 100.0% | 34.2% – 100.0% | 100.0% | 100.0% – 100.0% |

Stratified permutation test of wording (all questions, 200 re-deals within design cells): p = 1.000.

Stratified permutation test of wording (answerable questions, 200 re-deals within design cells): p = 1.000.

Question-mean accuracy by type and wording (questions per cell in brackets):

| Type | formal | casual | terse | typo |
|---|---:|---:|---:|---:|
| number | – | – | 100.0% (1) | 100.0% (1) |
| text | – | 100.0% (1) | 100.0% (1) | – |
| calc | 0.0% (1) | 100.0% (1) | – | – |
| comparison | – | 100.0% (1) | 100.0% (1) | – |
| false_premise | 0.0% (1) | – | – | 100.0% (1) |
| not_found | 100.0% (1) | – | 100.0% (1) | – |
| out_of_scope | 100.0% (1) | – | – | – |
| injection | 100.0% (1) | 100.0% (1) | – | – |

## Company by type (single-company questions)

| Company | number | text | calc | false_premise | not_found |
|---|---:|---:|---:|---:|---:|
| Michelin | – | 100.0% (1) | – | 100.0% (1) | – |
| Goodyear | 100.0% (1) | – | 100.0% (1) | – | 100.0% (1) |
| Continental | – | 100.0% (1) | – | 0.0% (1) | – |
| Bridgestone | 100.0% (1) | – | 0.0% (1) | – | 100.0% (1) |

## Comparisons by company pair

| Pair | Questions | Attempts | Accuracy | Wilson 95% (attempts) | Question mean | Cluster bootstrap 95% |
|---|---:|---:|---:|---|---:|---|
| Michelin,Bridgestone | 1 | 1 | 100.0% | 20.7% – 100.0% | 100.0% | n/a – n/a |
| Michelin,Goodyear | 1 | 1 | 100.0% | 20.7% – 100.0% | 100.0% | n/a – n/a |

## Logistic model (single-company questions)

Firth-penalized logistic regression, 10 attempts on 10 questions, standard errors clustered by question. Odds ratios are against the reference level.

| Factor | Reference | Wald χ² | df | p |
|---|---|---:|---:|---:|
| company | Michelin | 0.00 | 3 | 1.000 |
| type | number | 0.00 | 4 | 1.000 |
| wording | formal | 0.00 | 3 | 1.000 |

| Term | Odds ratio | 95% CI | p |
|---|---:|---|---:|
| company=Goodyear | inf | inf – inf | nan |
| company=Continental | 0.00 | 0.00 – 0.00 | nan |
| company=Bridgestone | 0.00 | 0.00 – 0.00 | nan |
| type=text | 0.00 | 0.00 – 0.00 | nan |
| type=calc | 0.00 | 0.00 – 0.00 | nan |
| type=false_premise | 0.00 | 0.00 – 0.00 | nan |
| type=not_found | inf | inf – inf | nan |
| wording=casual | inf | inf – inf | nan |
| wording=terse | 0.00 | 0.00 – 0.00 | nan |
| wording=typo | 0.00 | 0.00 – 0.00 | nan |

## Retrieval or generation?

Evidence was retrieved in 100.0% of answerable attempts. Accuracy was 80.0% when it was and n/a when it wasn't; 2 wrong answers had the evidence in hand (a generation or reasoning failure) and 0 attempts never retrieved it.

## Grading check: LLM judge vs. model-free first pass

10 answerable attempts: agreement 100.0%, Cohen's κ = 1.00. The judge passed 0 that the first pass didn't, and failed 0 that it passed. Each disagreement deserves a read; the first pass misses paraphrased names and unusual number formats, and the judge can be lenient on near-misses.


## Precision of this design

Smallest drop from the observed answerable accuracy (80.0%) detectable with 80% power (two-sided α = 0.05, one observation per question):

| Comparison | Questions per group | Detectable drop | 95% CI half-width |
|---|---:|---:|---:|
| wording level, all questions | 3 | n/a | ±45.3% |
| wording level, answerable questions | 2 | n/a | ±55.4% |
| company, single-company questions | 2 | n/a | ±55.4% |
| question type (number) | 2 | n/a | ±55.4% |
| question type (calc, text) | 2 | n/a | ±55.4% |

## Questions that failed at least once

| ID | Type | Wording | Passed | Question | Note (most recent failure) |
|---|---|---|---:|---|---|
| BS-C15 | calc | formal | 0/1 | What was Bridgestone's ratio of total liabilities to total equity at the end of 2024? | The answer gives the wrong ratio. EXPECTED is about 0.51 (1,937.0 / 3,786.5 billion JPY), but the answer states about 0.54x. It also derives liabiliti |
| CO-P02 | false_premise | formal | 0/1 | What drove Continental's €1.2 billion net income attributable to shareholders in 2025? | The answer correctly rejects the false premise that Continental had €1.2 billion net income attributable to shareholders in 2025, and it states the co |

Median latency 5.1 s · about 89,550 tokens per run (answers and grading).
