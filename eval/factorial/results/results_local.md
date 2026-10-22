# Factorial Evaluation Results

400 questions × 1 run(s) = 400 graded attempts · local system, answer model `qwen2.5-7b-16k`.
Design and method: [README](../README.md). Question-level intervals treat each question as the unit, since runs of the same question are not independent.

## Headline

| Block | Questions | Accuracy (attempts) | Wilson 95% | Question mean | Cluster bootstrap 95% |
|---|---:|---:|---|---:|---|
| Answerable (number, text, calc, comparison, false premise) | 304 | 1.6% | 0.7% – 3.8% | 1.6% | 0.3% – 3.3% |
| Should decline or block (not found, out of scope, injection) | 96 | 100.0% | 96.2% – 100.0% | 100.0% | 100.0% – 100.0% |
| All | 400 | 25.2% | 21.2% – 29.7% | 25.2% | 21.0% – 29.5% |

## By question type

| Type | Questions | Attempts | Accuracy | Wilson 95% (attempts) | Question mean | Cluster bootstrap 95% |
|---|---:|---:|---:|---|---:|---|
| number | 80 | 80 | 3.8% | 1.3% – 10.5% | 3.8% | 0.0% – 8.8% |
| text | 64 | 64 | 0.0% | 0.0% – 5.7% | 0.0% | 0.0% – 0.0% |
| calc | 64 | 64 | 1.6% | 0.3% – 8.3% | 1.6% | 0.0% – 4.7% |
| comparison | 48 | 48 | 2.1% | 0.4% – 10.9% | 2.1% | 0.0% – 6.2% |
| false_premise | 48 | 48 | 0.0% | 0.0% – 7.4% | 0.0% | 0.0% – 0.0% |
| not_found | 48 | 48 | 100.0% | 92.6% – 100.0% | 100.0% | 100.0% – 100.0% |
| out_of_scope | 24 | 24 | 100.0% | 86.2% – 100.0% | 100.0% | 100.0% – 100.0% |
| injection | 24 | 24 | 100.0% | 86.2% – 100.0% | 100.0% | 100.0% – 100.0% |

## By company (single-company questions)

| Company | Questions | Attempts | Accuracy | Wilson 95% (attempts) | Question mean | Cluster bootstrap 95% |
|---|---:|---:|---:|---|---:|---|
| Michelin | 76 | 76 | 17.1% | 10.3% – 27.1% | 17.1% | 9.2% – 26.3% |
| Goodyear | 76 | 76 | 17.1% | 10.3% – 27.1% | 17.1% | 9.2% – 26.3% |
| Continental | 76 | 76 | 18.4% | 11.3% – 28.6% | 18.4% | 9.2% – 27.6% |
| Bridgestone | 76 | 76 | 15.8% | 9.3% – 25.6% | 15.8% | 7.9% – 25.0% |

## By wording

All 400 questions:

| Wording | Questions | Attempts | Accuracy | Wilson 95% (attempts) | Question mean | Cluster bootstrap 95% |
|---|---:|---:|---:|---|---:|---|
| formal | 100 | 100 | 27.0% | 19.3% – 36.4% | 27.0% | 18.0% – 36.0% |
| casual | 100 | 100 | 25.0% | 17.5% – 34.3% | 25.0% | 17.0% – 34.0% |
| terse | 100 | 100 | 24.0% | 16.7% – 33.2% | 24.0% | 16.0% – 33.0% |
| typo | 100 | 100 | 25.0% | 17.5% – 34.3% | 25.0% | 17.0% – 34.0% |

Answerable questions only:

| Wording | Questions | Attempts | Accuracy | Wilson 95% (attempts) | Question mean | Cluster bootstrap 95% |
|---|---:|---:|---:|---|---:|---|
| formal | 76 | 76 | 3.9% | 1.4% – 11.0% | 3.9% | 0.0% – 9.2% |
| casual | 76 | 76 | 1.3% | 0.2% – 7.1% | 1.3% | 0.0% – 3.9% |
| terse | 76 | 76 | 0.0% | 0.0% – 4.8% | 0.0% | 0.0% – 0.0% |
| typo | 76 | 76 | 1.3% | 0.2% – 7.1% | 1.3% | 0.0% – 3.9% |

Stratified permutation test of wording (all questions, 10,000 re-deals within design cells): p = 0.394.

Stratified permutation test of wording (answerable questions, 10,000 re-deals within design cells): p = 0.410.

Question-mean accuracy by type and wording (questions per cell in brackets):

| Type | formal | casual | terse | typo |
|---|---:|---:|---:|---:|
| number | 5.0% (20) | 5.0% (20) | 0.0% (20) | 5.0% (20) |
| text | 0.0% (16) | 0.0% (16) | 0.0% (16) | 0.0% (16) |
| calc | 6.2% (16) | 0.0% (16) | 0.0% (16) | 0.0% (16) |
| comparison | 8.3% (12) | 0.0% (12) | 0.0% (12) | 0.0% (12) |
| false_premise | 0.0% (12) | 0.0% (12) | 0.0% (12) | 0.0% (12) |
| not_found | 100.0% (12) | 100.0% (12) | 100.0% (12) | 100.0% (12) |
| out_of_scope | 100.0% (6) | 100.0% (6) | 100.0% (6) | 100.0% (6) |
| injection | 100.0% (6) | 100.0% (6) | 100.0% (6) | 100.0% (6) |

## Company by type (single-company questions)

| Company | number | text | calc | false_premise | not_found |
|---|---:|---:|---:|---:|---:|
| Michelin | 0.0% (20) | 0.0% (16) | 6.2% (16) | 0.0% (12) | 100.0% (12) |
| Goodyear | 5.0% (20) | 0.0% (16) | 0.0% (16) | 0.0% (12) | 100.0% (12) |
| Continental | 10.0% (20) | 0.0% (16) | 0.0% (16) | 0.0% (12) | 100.0% (12) |
| Bridgestone | 0.0% (20) | 0.0% (16) | 0.0% (16) | 0.0% (12) | 100.0% (12) |

## Comparisons by company pair

| Pair | Questions | Attempts | Accuracy | Wilson 95% (attempts) | Question mean | Cluster bootstrap 95% |
|---|---:|---:|---:|---|---:|---|
| Continental,Bridgestone | 8 | 8 | 0.0% | 0.0% – 32.4% | 0.0% | 0.0% – 0.0% |
| Goodyear,Bridgestone | 8 | 8 | 0.0% | 0.0% – 32.4% | 0.0% | 0.0% – 0.0% |
| Goodyear,Continental | 8 | 8 | 0.0% | 0.0% – 32.4% | 0.0% | 0.0% – 0.0% |
| Michelin,Bridgestone | 8 | 8 | 0.0% | 0.0% – 32.4% | 0.0% | 0.0% – 0.0% |
| Michelin,Continental | 8 | 8 | 0.0% | 0.0% – 32.4% | 0.0% | 0.0% – 0.0% |
| Michelin,Goodyear | 8 | 8 | 12.5% | 2.2% – 47.1% | 12.5% | 0.0% – 37.5% |

## Logistic model (single-company questions)

Firth-penalized logistic regression, 304 attempts on 304 questions, standard errors clustered by question. Odds ratios are against the reference level.

| Factor | Reference | Wald χ² | df | p |
|---|---|---:|---:|---:|
| company | Michelin | 26.87 | 3 | 0.000 |
| type | number | 1350.30 | 4 | 0.000 |
| wording | formal | 26.79 | 3 | 0.000 |

| Term | Odds ratio | 95% CI | p |
|---|---:|---|---:|
| company=Goodyear | 1.00 | 0.26 – 3.79 | 1.000 |
| company=Continental | 1.72 | 0.49 – 6.07 | 0.397 |
| company=Bridgestone | 0.31 | 0.12 – 0.78 | 0.013 |
| type=text | 0.18 | 0.08 – 0.40 | 0.000 |
| type=calc | 0.53 | 0.15 – 1.84 | 0.317 |
| type=false_premise | 0.23 | 0.10 – 0.54 | 0.001 |
| type=not_found | 1966.20 | 1039.62 – 3718.61 | 0.000 |
| wording=casual | 0.58 | 0.17 – 1.98 | 0.386 |
| wording=terse | 0.18 | 0.07 – 0.42 | 0.000 |
| wording=typo | 0.58 | 0.16 – 2.05 | 0.399 |

## Retrieval or generation?

Evidence was retrieved in 85.7% of answerable attempts. Accuracy was 2.0% when it was and 0.0% when it wasn't; 247 wrong answers had the evidence in hand (a generation or reasoning failure) and 42 attempts never retrieved it.

## Grading check: LLM judge vs. model-free first pass

294 answerable attempts: agreement 99.7%, Cohen's κ = 0.91. The judge passed 0 that the first pass didn't, and failed 1 that it passed. Each disagreement deserves a read; the first pass misses paraphrased names and unusual number formats, and the judge can be lenient on near-misses.

| ID | Run | Judge | First pass | Judge's reason |
|---|---:|---|---|---|
| X-GB8 | 1 | fail | pass | The answer is incomplete and does not fully match the expected comparison. It correctly gives Bridgestone's 2024 dividend of 210 JPY and 202 |

## Precision of this design

Smallest drop from the observed answerable accuracy (1.6%) detectable with 80% power (two-sided α = 0.05, one observation per question):

| Comparison | Questions per group | Detectable drop | 95% CI half-width |
|---|---:|---:|---:|
| wording level, all questions | 100 | n/a | ±2.5% |
| wording level, answerable questions | 76 | n/a | ±2.9% |
| company, single-company questions | 76 | n/a | ±2.9% |
| question type (number) | 80 | n/a | ±2.8% |
| question type (calc, text) | 64 | n/a | ±3.1% |
| company x type cell (number) | 20 | n/a | ±5.6% |

## Questions that failed at least once

| ID | Type | Wording | Passed | Question | Note (most recent failure) |
|---|---|---|---:|---|---|
| BS-C01 | calc | formal | 0/1 | By what percentage did Bridgestone's revenue change from 2023 to 2024? | not answered |
| BS-C02 | calc | typo | 0/1 | By what percentwge did Bridgestone's adjusted operating profit chnage from 2023 to 2024? | not answered |
| BS-C03 | calc | casual | 0/1 | what share of bridgestone's 2024 revenue came from the americas segment? | not answered |
| BS-C04 | calc | formal | 0/1 | What were Bridgestone's 2024 capital expenditures as a percentage of revenue? | not answered |
| BS-C05 | calc | terse | 0/1 | bridgestone FCF % of revenue 2024 | not answered |
| BS-C06 | calc | casual | 0/1 | how much did bridgestone's r&d spending change from 2023 to 2024, in %? | not answered |
| BS-C07 | calc | typo | 0/1 | What was Bridgestone's total equuity as a perceentage of total assets at the end of 2024? | not answered |
| BS-C08 | calc | typo | 0/1 | How many percentage points higher was the Japan segment's adjusted operqting mrgin than EMEA's in 2024? | not answered |
| BS-C09 | calc | terse | 0/1 | bridgestone revenue per employee 2024 | not answered |
| BS-C10 | calc | terse | 0/1 | bridgestone americas share of employees end 2024 | not answered |
| BS-C11 | calc | casual | 0/1 | how much would bridgestone's dividend per share go up from 2024 to the 2025 forecast, in %? | not answered |
| BS-C12 | calc | terse | 0/1 | bridgestone 2025 revenue target vs 2024 revenue % | not answered |
| BS-C13 | calc | typo | 0/1 | By what percentage does Bridgestone's 2025 plan for profit from continuing opreations differ from its 2024 profit? | not answered |
| BS-C14 | calc | casual | 0/1 | by how much (in %) did bridgestone's profit attributable to owners of the parent change from 2023 to 2024? | not answered |
| BS-C15 | calc | formal | 0/1 | What was Bridgestone's ratio of total liabilities to total equity at the end of 2024? | not answered |
| BS-C16 | calc | formal | 0/1 | By what percentage did Bridgestone's operating cash flow change from 2023 to 2024? | not answered |
| BS-N01 | number | formal | 0/1 | What was Bridgestone's adjusted operating profit in 2024? | not answered |
| BS-N02 | number | casual | 0/1 | what was bridgestone's adjusted operating margin in 2024? | not answered |
| BS-N03 | number | formal | 0/1 | What was Bridgestone's profit attributable to owners of the parent in 2024? | not answered |
| BS-N04 | number | typo | 0/1 | What were Bridgestone's ttal asseets at the end of 2024? | not answered |
| BS-N05 | number | formal | 0/1 | What was Bridgestone's total equity at the end of 2024? | not answered |
| BS-N06 | number | typo | 0/1 | What was Bridgestone's reyurn on invested capiital (ROIC) in 2024? | not answered |
| BS-N07 | number | typo | 0/1 | What was Bridgestone's reeturn on eauity (ROE) in 2024? | not answered |
| BS-N08 | number | terse | 0/1 | bridgestone operating cash flow 2024 | not answered |
| BS-N09 | number | typo | 0/1 | What was Bridgestone's free csh foow in 2024? | not answered |
| BS-N10 | number | terse | 0/1 | bridgestone capex 2024 | not answered |
| BS-N11 | number | terse | 0/1 | bridgestone r&d expenses 2024 | not answered |
| BS-N12 | number | formal | 0/1 | What was Bridgestone's depreciation and amortization in 2024? | not answered |
| BS-N13 | number | casual | 0/1 | how much revenue did bridgestone's americas segment bring in during 2024? | not answered |
| BS-N14 | number | terse | 0/1 | bridgestone japan segment adjusted operating margin 2024 | not answered |
| BS-N15 | number | casual | 0/1 | how many employees did bridgestone have at the end of 2024? | not answered |
| BS-N16 | number | casual | 0/1 | how much did bridgestone produce in tires in 2024 (production volume)? | not answered |
| BS-N17 | number | casual | 0/1 | how much capex is bridgestone planning for 2025? | not answered |
| BS-N18 | number | formal | 0/1 | What revenue does Bridgestone's 2025 plan target for its premium tire business? | not answered |
| BS-N19 | number | terse | 0/1 | bridgestone LTIFR employees 2024 | not answered |
| BS-N20 | number | typo | 0/1 | What share of Bridgestone's emloyees were woen at the end of 2024? | not answered |
| BS-P01 | false_premise | terse | 0/1 | bridgestone 2024 revenue ~2 trillion yen? | not answered |
| BS-P02 | false_premise | typo | 0/1 | Why was Bridgestone's adjuted oeprating profit margin so high at 18% in 2024? | not answered |
| BS-P03 | false_premise | terse | 0/1 | bridgestone 50,000 employees how many americas | not answered |
| BS-P04 | false_premise | formal | 0/1 | Bridgestone's 2024 R&D expenses were 400 billion yen; what share of revenue is that? | not answered |
| BS-P05 | false_premise | casual | 0/1 | shuichi ishibashi is bridgestone's global CFO - what's his financial strategy? | not answered |
| BS-P06 | false_premise | casual | 0/1 | harvey firestone started bridgestone back in 1931 - how did it grow after that? | not answered |
| BS-P07 | false_premise | casual | 0/1 | what's naoki hishinuma focused on as bridgestone's global CEO? | not answered |
| BS-P08 | false_premise | terse | 0/1 | bridgestone 2024 profit attributable to owners rise why | not answered |
| BS-P09 | false_premise | typo | 0/1 | Why is Bridgestone ctting its dividrnd for 2025? | not answered |
| BS-P10 | false_premise | formal | 0/1 | What caused Bridgestone's free cash flow to rise in 2024? | not answered |
| BS-P11 | false_premise | typo | 0/1 | When did Bridgestone mrege wtih Goodyear? | not answered |
| BS-P12 | false_premise | formal | 0/1 | Why did Bridgestone drop its Nominating Committee governance structure in 2024? | not answered |
| BS-T01 | text | terse | 0/1 | bridgestone global CFO | not answered |
| BS-T02 | text | typo | 0/1 | Who foundded Bridgestone? | not answered |
| BS-T03 | text | casual | 0/1 | when and where did bridgestone get started? | not answered |
| BS-T04 | text | casual | 0/1 | when did bridgestone and firestone merge? | not answered |
| BS-T05 | text | typo | 0/1 | How is Bridgestone's Board of Directors coposed? | not answered |
| BS-T06 | text | typo | 0/1 | How has Bridgestone dividded its business retionally since January 2024? | not answered |
| BS-T07 | text | formal | 0/1 | What are the commitments in the Bridgestone E8 Commitment? | not answered |
| BS-T08 | text | formal | 0/1 | What is Bridgestone's corporate mission? | not answered |
| BS-T09 | text | terse | 0/1 | bridgestone MSCI ESG rating | not answered |
| BS-T10 | text | formal | 0/1 | What was Bridgestone's CDP Climate Change score? | not answered |
| BS-T11 | text | casual | 0/1 | what are the four parts of bridgestone's business portfolio? | not answered |
| BS-T12 | text | formal | 0/1 | What is BCMA at Bridgestone? | not answered |
| BS-T13 | text | typo | 0/1 | How did Bridgestone charcaterize 2025 in its bussiness plan? | not answered |
| BS-T14 | text | terse | 0/1 | bridgestone ENLITEN tire launched india 2024 | not answered |
| BS-T15 | text | terse | 0/1 | bridgestone 2050 vision | not answered |
| BS-T16 | text | casual | 0/1 | what governance setup did bridgestone switch to in march 2016? | not answered |
| CO-C01 | calc | formal | 0/1 | By what percentage did Continental's sales change from 2024 to 2025? | not answered |
| CO-C02 | calc | casual | 0/1 | what % of sales did continental spend on r&d in 2025? | not answered |
| CO-C03 | calc | formal | 0/1 | What share of Continental's 2025 sales came from the Tires group sector? | not answered |
| CO-C04 | calc | formal | 0/1 | What was Continental's EBITDA margin in 2025? | not answered |
| CO-C05 | calc | typo | 0/1 | By what peercentage did Continental's adjusted EBIT chaange from 2024 to 2025? | not answered |
| CO-C06 | calc | typo | 0/1 | By what percentage did Continental's free cash flow from contiuing operrations change in 2025? | not answered |
| CO-C07 | calc | typo | 0/1 | By what percentage did Continental's emploee count change duing 2025? | not answered |
| CO-C08 | calc | terse | 0/1 | continental net indebtedness / equity end 2025 | not answered |
| CO-C09 | calc | casual | 0/1 | how many points higher was continental's tires adjusted EBIT margin vs contitech's in 2025? | not answered |
| CO-C10 | calc | typo | 0/1 | By what percenttage did Continental's share price chajge during 2025? | not answered |
| CO-C11 | calc | casual | 0/1 | how much did continental's operating cash flow change in 2025, in %? | not answered |
| CO-C12 | calc | terse | 0/1 | continental contitech share of employees end 2025 | not answered |
| CO-C13 | calc | formal | 0/1 | What share of Continental's 2025 research and development expenses was attributable to Tires? | not answered |
| CO-C14 | calc | terse | 0/1 | continental sales per employee 2025 | not answered |
| CO-C15 | calc | casual | 0/1 | how much did continental's tires sector sell per tires employee in 2025? | not answered |
| CO-C16 | calc | terse | 0/1 | continental capex change 2024 to 2025 % | output limit reached |
| CO-N01 | number | casual | 0/1 | what was continental's EBITDA in 2025? | not answered |
| CO-N02 | number | formal | 0/1 | What was Continental's EBIT in 2025? | not answered |
| CO-N03 | number | formal | 0/1 | What were Continental's basic earnings per share in 2025? | not answered |
| CO-N04 | number | formal | 0/1 | What was Continental's adjusted EBIT in 2025? | output limit reached |
| CO-N05 | number | casual | 0/1 | how much free cash flow did continental generate from continuing ops in 2025? | not answered |
| CO-N07 | number | terse | 0/1 | continental leverage ratio end 2025 | not answered |
| CO-N08 | number | typo | 0/1 | What was Continental's toal eqquity at the end of 2025? | not answered |
| CO-N09 | number | typo | 0/1 | What was Continental's euqity raatio at the end of 2025? | not answered |
| CO-N11 | number | casual | 0/1 | how much did continental's tires sector sell in 2025? | not answered |
| CO-N12 | number | typo | 0/1 | What was the adjusted EBIT margin of Continental's Tires gorup seector in 2025? | not answered |
| CO-N13 | number | casual | 0/1 | how many people worked in continental's tires business at the end of 2025? | not answered |
| CO-N14 | number | typo | 0/1 | What was the EBIT of Continental's ContiTech grooup seector in 2025? | not answered |
| CO-N15 | number | terse | 0/1 | continental r&d spend 2025 | not answered |
| CO-N16 | number | terse | 0/1 | continental capex 2025 | not answered |
| CO-N17 | number | terse | 0/1 | continental capex ratio 2025 | not answered |
| CO-N18 | number | terse | 0/1 | continental operating cash flow 2025 | not answered |
| CO-N19 | number | typo | 0/1 | What was Continental's grooss indebtedneess at the end of 2025? | not answered |
| CO-N20 | number | formal | 0/1 | What were Continental's depreciation and amortization in 2025? | not answered |
| CO-P01 | false_premise | formal | 0/1 | Continental's 2025 sales were €41 billion, correct? | not answered |
| CO-P02 | false_premise | formal | 0/1 | What drove Continental's €1.2 billion net income attributable to shareholders in 2025? | not answered |
| CO-P03 | false_premise | casual | 0/1 | continental's leverage ratio is 0.5, so how are they funding growth? | not answered |
| CO-P04 | false_premise | casual | 0/1 | continental has like 190,000 employees - how many are in tires? | not answered |
| CO-P05 | false_premise | typo | 0/1 | As Continental's CFO, waht is Christian Kötz resppnsible for? | not answered |
| CO-P06 | false_premise | casual | 0/1 | what's wolfgang reitzle been prioritizing as continental's CEO? | not answered |
| CO-P07 | false_premise | typo | 0/1 | What are Ulrike Hintze's gals as heead of ContiTech? | not answered |
| CO-P08 | false_premise | typo | 0/1 | Why did Continental's free caash flow deecline in 2025? | not answered |
| CO-P09 | false_premise | formal | 0/1 | What drove the increase in Continental's EBIT in 2025? | not answered |
| CO-P10 | false_premise | terse | 0/1 | continental net indebtedness fall 2025 reason | not answered |
| CO-P11 | false_premise | terse | 0/1 | continental contitech spin-off 2025 why | output limit reached |
| CO-P12 | false_premise | terse | 0/1 | continental dividend cut fiscal 2025 why | not answered |
| CO-T01 | text | formal | 0/1 | Who is responsible for finance on Continental's Executive Board? | not answered |
| CO-T02 | text | typo | 0/1 | Who is repsonsible for human reations on Continental's Executive Board? | not answered |
| CO-T03 | text | typo | 0/1 | Which Executive Board member is responnsible for Continental's ContiTech group sdctor? | not answered |
| CO-T04 | text | casual | 0/1 | who's the chair of continental's supervisory board? | not answered |
| CO-T05 | text | terse | 0/1 | continental auditor | not answered |
| CO-T06 | text | typo | 0/1 | When and whree is Continental's 2026 Annual Shareholders' Meeting? | not answered |
| CO-T07 | text | casual | 0/1 | what were continental's group sectors in 2025 after everything (continuing ops)? | not answered |
| CO-T08 | text | casual | 0/1 | what's OESL and what happened with it? | not answered |
| CO-T09 | text | formal | 0/1 | What does Continental plan to do with its ContiTech group sector? | not answered |
| CO-T10 | text | formal | 0/1 | Why did Continental's EBIT fall so sharply in 2025? | not answered |
| CO-T11 | text | terse | 0/1 | continental why leverage ratio instead of gearing | not answered |
| CO-T12 | text | terse | 0/1 | continental may 2025 euro bond terms | not answered |
| CO-T13 | text | typo | 0/1 | On wgich German sttock exchanges is Continental's share listed? | not answered |
| CO-T14 | text | casual | 0/1 | who's continental's controlling shareholder? | not answered |
| CO-T15 | text | terse | 0/1 | continental why stopped reporting net r&d expenses | not answered |
| CO-T16 | text | formal | 0/1 | What share of Continental's 2025 sales related to the automotive industry, excluding the replacement business? | not answered |
| GY-C01 | calc | formal | 0/1 | What was Goodyear's 2025 net loss as a percentage of net sales? | not answered |
| GY-C02 | calc | typo | 0/1 | What were Goodyear's 2025 capital expendituers as a percentage of net saes? | not answered |
| GY-C03 | calc | typo | 0/1 | What was Goodyear's research and devwlopment spending as a perxentage of net sales in 2025? | not answered |
| GY-C04 | calc | casual | 0/1 | how much did goodyear's r&d spending go up or down from 2024 to 2025, in %? | not answered |
| GY-C05 | calc | terse | 0/1 | goodyear 2025 operating cash flow minus capex | not answered |
| GY-C06 | calc | casual | 0/1 | can you work out goodyear's gross margin for 2025 from sales and cost of goods sold? | not answered |
| GY-C07 | calc | terse | 0/1 | goodyear SAG % of net sales 2025 | not answered |
| GY-C08 | calc | formal | 0/1 | What share of Goodyear's total assets was funded by total shareholders' equity at the end of 2025? | not answered |
| GY-C09 | calc | typo | 0/1 | What was Goodyear's currrent raito at December 31, 2025? | not answered |
| GY-C10 | calc | terse | 0/1 | goodyear americas share of 2025 net sales | not answered |
| GY-C11 | calc | formal | 0/1 | By what percentage did Goodyear's total assets change between the end of 2024 and the end of 2025? | not answered |
| GY-C12 | calc | terse | 0/1 | goodyear asia pacific vs emea operating margin gap 2025 | not answered |
| GY-C13 | calc | formal | 0/1 | What were Goodyear's 2025 net sales per associate? | not answered |
| GY-C14 | calc | casual | 0/1 | how many dollars did goodyear's total segment operating income drop between 2024 and 2025? | not answered |
| GY-C15 | calc | typo | 0/1 | By what percentage did Goodyear's interest exxpense chnage from 2024 to 2025? | not answered |
| GY-C16 | calc | casual | 0/1 | roughly what share of goodyear's 2025 tire units came out of asia pacific? | not answered |
| GY-N01 | number | terse | 0/1 | goodyear net sales 2024 | not answered |
| GY-N02 | number | terse | 0/1 | goodyear 2025 loss per share | not answered |
| GY-N03 | number | terse | 0/1 | goodyear total segment operating income 2025 | not answered |
| GY-N04 | number | formal | 0/1 | What was Goodyear's total segment operating margin in 2025? | not answered |
| GY-N05 | number | typo | 0/1 | How much net cash did Goodyear's operating activiies proide in 2025? | not answered |
| GY-N06 | number | typo | 0/1 | How mch cwsh and cash equivalents did Goodyear hold at December 31, 2025? | not answered |
| GY-N07 | number | formal | 0/1 | How many manufacturing facilities does Goodyear operate? | not answered |
| GY-N08 | number | terse | 0/1 | goodyear number of retail outlets | not answered |
| GY-N09 | number | casual | 0/1 | how much did goodyear's americas business sell in 2025? | not answered |
| GY-N10 | number | casual | 0/1 | what did goodyear's europe/middle east/africa segment make in operating income last year (2025)? | not answered |
| GY-N11 | number | casual | 0/1 | hey, what kind of operating margin did goodyear get in asia pacific in 2025? | not answered |
| GY-N12 | number | formal | 0/1 | How much did Goodyear spend on research and development in 2025? | not answered |
| GY-N13 | number | terse | 0/1 | goodyear total assets end 2025 | not answered |
| GY-N14 | number | casual | 0/1 | how much did goodyear's tire shipments drop in 2025, percentage-wise? | output limit reached |
| GY-N15 | number | formal | 0/1 | What was Goodyear's worldwide tire capacity utilization rate in 2025? | not answered |
| GY-N16 | number | typo | 0/1 | How large was the gopdwill impairment charge Goodyear recorded in its Americas segmnt in 2025? | not answered |
| GY-N17 | number | typo | 0/1 | What was Goodyear's intereest exlense in 2025? | not answered |
| GY-N18 | number | casual | 0/1 | how much did goodyear get for selling off its polymer chemicals business? | not answered |
| GY-N19 | number | formal | 0/1 | Approximately how many Goodyear associates are covered by collective bargaining agreements? | not answered |
| GY-P01 | false_premise | terse | 0/1 | goodyear 2025 net sales ~$22B? | not answered |
| GY-P02 | false_premise | terse | 0/1 | goodyear 120,000 associates how many collective bargaining | not answered |
| GY-P03 | false_premise | formal | 0/1 | What drove Goodyear's $2.1 billion of capital expenditures in 2025? | not answered |
| GY-P04 | false_premise | formal | 0/1 | Goodyear's Americas segment earned a 12% operating margin in 2025, right? | output limit reached |
| GY-P05 | false_premise | typo | 0/1 | As Goodyear's CEO, wat is Christina Zamarro's backgrund? | not answered |
| GY-P06 | false_premise | terse | 0/1 | nathaniel madarang goodyear CFO priorities | not answered |
| GY-P07 | false_premise | casual | 0/1 | so mark stewart came to goodyear from ford, what was his job there? | not answered |
| GY-P08 | false_premise | casual | 0/1 | why'd goodyear's net income go up in 2025? | not answered |
| GY-P09 | false_premise | formal | 0/1 | What drove the increase in Goodyear's Asia Pacific net sales in 2025? | not answered |
| GY-P10 | false_premise | typo | 0/1 | Why did operafing incme in Goodyear's EMEA segment fall in 2025? | not answered |
| GY-P11 | false_premise | typo | 0/1 | When in 2025 did Goodyear sll its Americas tire busiess? | not answered |
| GY-P12 | false_premise | casual | 0/1 | how much did goodyear pay out in common stock dividends in 2025? | not answered |
| GY-T01 | text | formal | 0/1 | Who is Goodyear's Chief Financial Officer? | not answered |
| GY-T02 | text | terse | 0/1 | goodyear chief technical officer | output limit reached |
| GY-T03 | text | formal | 0/1 | Who leads Goodyear's Asia Pacific business? | output limit reached |
| GY-T04 | text | casual | 0/1 | where's goodyear headquartered? | not answered |
| GY-T05 | text | casual | 0/1 | when and where was goodyear set up as a company? | not answered |
| GY-T06 | text | typo | 0/1 | What are Goodyear's opertaing segemnts? | output limit reached |
| GY-T07 | text | formal | 0/1 | Which firm audits Goodyear's financial statements? | not answered |
| GY-T08 | text | terse | 0/1 | goodyear polymer chemicals business buyer | not answered |
| GY-T09 | text | casual | 0/1 | what's goodyear's plan for a fully sustainable-material tire? | not answered |
| GY-T10 | text | typo | 0/1 | What was the Goodyear Forward plan maent to acieve? | not answered |
| GY-T11 | text | formal | 0/1 | Which businesses did Goodyear sell in 2025? | not answered |
| GY-T12 | text | casual | 0/1 | did goodyear pay shareholders a dividend in 2025? | not answered |
| GY-T13 | text | typo | 0/1 | When does Goodyear's master collctive bargaining agreement with the United Steelworkers expre? | not answered |
| GY-T14 | text | typo | 0/1 | Why did Goodyear rport a net lsos in 2025? | The answer does not match the expected explanation. EXPECTED says the net loss was mainly due to a full valuation allowance on U.S. net deferred tax a |
| GY-T15 | text | terse | 0/1 | goodyear asia pacific major competitors | not answered |
| GY-T16 | text | terse | 0/1 | goodyear americas net sales top country | not answered |
| MI-C01 | calc | terse | 0/1 | michelin operating income % of sales 2025 | not answered |
| MI-C02 | calc | terse | 0/1 | michelin r&d % of sales 2025 | not answered |
| MI-C03 | calc | terse | 0/1 | michelin effective tax rate 2025 | not answered |
| MI-C04 | calc | casual | 0/1 | michelin's capex as a % of sales in 2025 - what was it? | not answered |
| MI-C05 | calc | casual | 0/1 | how much of michelin's 2025 sales came from the automotive segment, as a share? | not answered |
| MI-C06 | calc | formal | 0/1 | By what percentage did segment operating income in Michelin's Road transportation segment change in 2025? | not answered |
| MI-C07 | calc | casual | 0/1 | how many points higher was michelin's specialty margin than road transportation's in 2025? | not answered |
| MI-C08 | calc | formal | 0/1 | What was the ratio of Michelin's free cash flow before M&A to its net income in 2025? | not answered |
| MI-C09 | calc | formal | 0/1 | By how much did Michelin's net debt change during 2025? | not answered |
| MI-C10 | calc | typo | 0/1 | By what percentage did Michelin's net cash from opreating activiteis change in 2025? | not answered |
| MI-C11 | calc | casual | 0/1 | what % of michelin's workforce is in europe? | not answered |
| MI-C12 | calc | typo | 0/1 | What were Michelin's 2025 saels per emploeye? | not answered |
| MI-C14 | calc | typo | 0/1 | What was Michelin's grss marrgin in 2025? | not answered |
| MI-C15 | calc | terse | 0/1 | michelin ROCE change 2025 percentage points | not answered |
| MI-C16 | calc | typo | 0/1 | How much did Michelin return to shareholders in 2025 through divdends and sahre buybacks combined? | not answered |
| MI-N01 | number | terse | 0/1 | michelin gross income 2025 | not answered |
| MI-N02 | number | casual | 0/1 | what was michelin's operating income in 2025? | not answered |
| MI-N03 | number | terse | 0/1 | michelin basic EPS 2025 | not answered |
| MI-N04 | number | terse | 0/1 | michelin r&d expenses 2025 | not answered |
| MI-N05 | number | terse | 0/1 | michelin income tax 2025 | not answered |
| MI-N06 | number | typo | 0/1 | What was Michelin's coost of net dbt in 2025? | not answered |
| MI-N07 | number | typo | 0/1 | What were the salles of Michelin's Automotive and related disyribution segment in 2025? | not answered |
| MI-N08 | number | terse | 0/1 | michelin road transportation segment operating income 2025 | not answered |
| MI-N09 | number | casual | 0/1 | what margin did michelin's specialty businesses make in 2025 (segment operating margin)? | not answered |
| MI-N10 | number | casual | 0/1 | how much net debt did michelin have at the end of 2025? | not answered |
| MI-N11 | number | typo | 0/1 | What was Michelin's gearng at the end of 2025? | not answered |
| MI-N12 | number | formal | 0/1 | How much cash and cash equivalents did Michelin hold at the end of 2025? | not answered |
| MI-N13 | number | typo | 0/1 | What was Michelin's tofal equtiy at December 31, 2025? | not answered |
| MI-N14 | number | typo | 0/1 | What was Michelin's fdee cash flow befroe M&A in 2025? | not answered |
| MI-N15 | number | casual | 0/1 | how much did michelin spend on capex in 2025? | not answered |
| MI-N16 | number | formal | 0/1 | What was Michelin's net cash from operating activities in 2025? | not answered |
| MI-N17 | number | casual | 0/1 | what was michelin's ROCE in 2025? | not answered |
| MI-N18 | number | formal | 0/1 | How much did Michelin's 2025 share buyback program cost? | not answered |
| MI-N19 | number | formal | 0/1 | How many active patents are in Michelin's portfolio? | not answered |
| MI-N20 | number | formal | 0/1 | By how much did Michelin's sales volumes decline in 2025? | not answered |
| MI-P01 | false_premise | formal | 0/1 | Michelin's net income was €3.2 billion in 2025, wasn't it? | not answered |
| MI-P02 | false_premise | typo | 0/1 | With gearnig of 45%, how lsveraged is Michelin? | not answered |
| MI-P03 | false_premise | terse | 0/1 | michelin ROCE up to 12% 2025 drivers | not answered |
| MI-P04 | false_premise | typo | 0/1 | Michelin has 200,000 employees; how are they solit by retion? | not answered |
| MI-P05 | false_premise | formal | 0/1 | What is Barbara Dalibard's role as Michelin's CFO? | not answered |
| MI-P06 | false_premise | formal | 0/1 | As Michelin's Managing Chairman, what responsibilities does Yves Chapot have? | not answered |
| MI-P07 | false_premise | casual | 0/1 | philippe jacquin runs michelin's north america region, right? what's he focused on? | not answered |
| MI-P08 | false_premise | casual | 0/1 | why did michelin's sales grow in 2025? | not answered |
| MI-P09 | false_premise | typo | 0/1 | Why did Michelin's net dwbt incraese in 2025? | not answered |
| MI-P10 | false_premise | terse | 0/1 | michelin road transportation segment operating income rise 2025 cause | not answered |
| MI-P11 | false_premise | terse | 0/1 | michelin downgraded to BBB 2025 why | not answered |
| MI-P12 | false_premise | casual | 0/1 | why's yves chapot running for re-election as michelin's general manager in 2026? | not answered |
| MI-T01 | text | casual | 0/1 | who's michelin's CFO? | not answered |
| MI-T02 | text | formal | 0/1 | Who chairs Michelin's Supervisory Board? | not answered |
| MI-T03 | text | typo | 0/1 | Who hads research and deevlopment on Michelin's Executive Committee? | not answered |
| MI-T04 | text | formal | 0/1 | Who is Michelin's Chief People Officer? | not answered |
| MI-T05 | text | terse | 0/1 | michelin 2030 strategic plan name launch year | not answered |
| MI-T06 | text | formal | 0/1 | What are Michelin's three reporting segments? | not answered |
| MI-T07 | text | terse | 0/1 | michelin CGEM S&P long-term rating | not answered |
| MI-T08 | text | terse | 0/1 | michelin moody's rating 2025 | not answered |
| MI-T09 | text | typo | 0/1 | Will Yves Chapot sttand for re-ellection as Michelin's General Manager in 2026? | not answered |
| MI-T10 | text | formal | 0/1 | When is Michelin's 2026 Annual Shareholders Meeting? | not answered |
| MI-T11 | text | casual | 0/1 | how does michelin tell if it actually created value in a given year? | not answered |
| MI-T12 | text | casual | 0/1 | why did michelin's sales go down in 2025? | not answered |
| MI-T13 | text | typo | 0/1 | Why did Michelin's coost of net debt incraese in 2025? | not answered |
| MI-T14 | text | typo | 0/1 | Who sts on Michelin's Stakeholders Committee? | not answered |
| MI-T15 | text | terse | 0/1 | michelin organization structure business lines regions | not answered |
| MI-T16 | text | casual | 0/1 | where does michelin rank on the list of the world's strongest brands? | not answered |
| X-CB1 | comparison | formal | 0/1 | Which has more employees, Continental or Bridgestone? | not answered |
| X-CB2 | comparison | casual | 0/1 | how does capex as a % of sales compare between continental and bridgestone? | not answered |
| X-CB3 | comparison | typo | 0/1 | Compare the operating margiins repotred by Continental and Bridgestone. | not answered |
| X-CB4 | comparison | typo | 0/1 | Compare the euity ratois of Continental and Bridgestone. | not answered |
| X-CB5 | comparison | formal | 0/1 | Who are the chief financial officers of Continental and Bridgestone? | not answered |
| X-CB6 | comparison | terse | 0/1 | continental vs bridgestone latest revenue growth | output limit reached |
| X-CB7 | comparison | casual | 0/1 | was continental or bridgestone profitable in their latest year? | not answered |
| X-CB8 | comparison | terse | 0/1 | continental vs bridgestone r&d % revenue | not answered |
| X-GB1 | comparison | casual | 0/1 | how many more employees does bridgestone have compared to goodyear? | not answered |
| X-GB2 | comparison | terse | 0/1 | goodyear vs bridgestone r&d % revenue | not answered |
| X-GB3 | comparison | formal | 0/1 | Compare capital expenditure as a percentage of revenue at Goodyear and Bridgestone. | not answered |
| X-GB4 | comparison | typo | 0/1 | Which compnay is olfer, Goodyear or Bridgestone? | not answered |
| X-GB5 | comparison | terse | 0/1 | goodyear vs bridgestone operating margin | not answered |
| X-GB6 | comparison | formal | 0/1 | Compare Goodyear's and Bridgestone's net margins. | not answered |
| X-GB7 | comparison | casual | 0/1 | who are the CFOs at goodyear and bridgestone? | not answered |
| X-GB8 | comparison | typo | 0/1 | Compare Goodyear's and Bridgestone's dicidends. | The answer is incomplete and does not fully match the expected comparison. It correctly gives Bridgestone's 2024 dividend of 210 JPY and 2025 forecast |
| X-GC1 | comparison | formal | 0/1 | Compare Goodyear's and Continental's research and development spending as a share of sales in 2025. | not answered |
| X-GC2 | comparison | casual | 0/1 | who invested more relative to sales in 2025, goodyear or continental? | not answered |
| X-GC3 | comparison | formal | 0/1 | Which has more employees, Goodyear or Continental? | not answered |
| X-GC4 | comparison | typo | 0/1 | Compare the oprating margins Goodyear and Continental repotred for 2025. | not answered |
| X-GC5 | comparison | terse | 0/1 | goodyear vs continental 2025 sales decline % | not answered |
| X-GC6 | comparison | casual | 0/1 | did goodyear and continental both lose money in 2025? | not answered |
| X-GC7 | comparison | typo | 0/1 | Do Goodyear and Continental use the saame audtor? | not answered |
| X-GC8 | comparison | terse | 0/1 | goodyear vs continental head of finance | not answered |
| X-MB1 | comparison | typo | 0/1 | Which has moore emmployees, Michelin or Bridgestone? | not answered |
| X-MB2 | comparison | casual | 0/1 | who spends more of their revenue on r&d, michelin or bridgestone? | not answered |
| X-MB3 | comparison | formal | 0/1 | Compare Michelin's and Bridgestone's net profit margins. | not answered |
| X-MB4 | comparison | terse | 0/1 | michelin vs bridgestone capex % revenue | not answered |
| X-MB5 | comparison | formal | 0/1 | Compare the operating margins reported by Michelin and Bridgestone. | not answered |
| X-MB6 | comparison | casual | 0/1 | who runs michelin and who runs bridgestone? | not answered |
| X-MB7 | comparison | typo | 0/1 | Compare the latest anunal revenue gdowth of Michelin and Bridgestone. | not answered |
| X-MB8 | comparison | terse | 0/1 | michelin vs bridgestone operating cash flow % revenue | not answered |
| X-MC1 | comparison | casual | 0/1 | how does michelin's 2025 r&d spend compare with continental's? | not answered |
| X-MC2 | comparison | formal | 0/1 | Which company spent more on capital expenditure in 2025, Michelin or Continental, and by how much? | not answered |
| X-MC3 | comparison | casual | 0/1 | michelin's net income vs continental's (attributable to shareholders) in 2025 - how do they compare? | The answer does not correctly provide Michelin’s 2025 net income figure, which is required by the question and present in EXPECTED (€1,664 million). I |
| X-MC4 | comparison | typo | 0/1 | Compare Michelin's and Continental's frree cash fow in 2025. | not answered |
| X-MC5 | comparison | terse | 0/1 | michelin vs continental net debt end 2025 | output limit reached |
| X-MC6 | comparison | formal | 0/1 | Compare Michelin's and Continental's total equity at the end of 2025. | not answered |
| X-MC7 | comparison | terse | 0/1 | michelin minus continental employees | not answered |
| X-MC8 | comparison | typo | 0/1 | Compare Michelin's and Continental's cash flow from opearting activiites in 2025. | not answered |
| X-MG1 | comparison | formal | 0/1 | Which spent a larger share of sales on research and development in 2025, Michelin or Goodyear? | not answered |
| X-MG2 | comparison | terse | 0/1 | michelin vs goodyear capex % of sales 2025 | not answered |
| X-MG3 | comparison | typo | 0/1 | Compare Michelin's and Goodyear's net magins in 2025. | not answered |
| X-MG4 | comparison | terse | 0/1 | michelin vs goodyear 2025 sales decline % | not answered |
| X-MG5 | comparison | casual | 0/1 | how do michelin's and goodyear's 2025 operating margins stack up? | not answered |
| X-MG6 | comparison | typo | 0/1 | Compare Michelin's and Goodyear's operatng cash flow reltaive to sales in 2025. | not answered |
| X-MG7 | comparison | casual | 0/1 | are michelin and goodyear paying dividends for 2025? | not answered |

Median latency 21.1 s · about 1,999,855 tokens per run (answers and grading).
