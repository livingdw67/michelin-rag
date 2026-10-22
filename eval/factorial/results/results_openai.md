# Factorial Evaluation Results

400 questions × 1 run(s) = 400 graded attempts · openai system, answer model `gpt-5.4-mini`.
Design and method: [README](../README.md). Question-level intervals treat each question as the unit, since runs of the same question are not independent.

## Headline

| Block | Questions | Accuracy (attempts) | Wilson 95% | Question mean | Cluster bootstrap 95% |
|---|---:|---:|---|---:|---|
| Answerable (number, text, calc, comparison, false premise) | 304 | 77.0% | 71.9% – 81.4% | 77.0% | 72.0% – 81.6% |
| Should decline or block (not found, out of scope, injection) | 96 | 99.0% | 94.3% – 99.8% | 99.0% | 96.9% – 100.0% |
| All | 400 | 82.2% | 78.2% – 85.7% | 82.2% | 78.5% – 85.8% |

## By question type

| Type | Questions | Attempts | Accuracy | Wilson 95% (attempts) | Question mean | Cluster bootstrap 95% |
|---|---:|---:|---:|---|---:|---|
| number | 80 | 80 | 88.8% | 80.0% – 94.0% | 88.8% | 81.2% – 95.0% |
| text | 64 | 64 | 90.6% | 81.0% – 95.6% | 90.6% | 82.8% – 96.9% |
| calc | 64 | 64 | 84.4% | 73.6% – 91.3% | 84.4% | 75.0% – 92.2% |
| comparison | 48 | 48 | 41.7% | 28.8% – 55.7% | 41.7% | 29.2% – 56.2% |
| false_premise | 48 | 48 | 64.6% | 50.4% – 76.6% | 64.6% | 50.0% – 79.2% |
| not_found | 48 | 48 | 97.9% | 89.1% – 99.6% | 97.9% | 93.8% – 100.0% |
| out_of_scope | 24 | 24 | 100.0% | 86.2% – 100.0% | 100.0% | 100.0% – 100.0% |
| injection | 24 | 24 | 100.0% | 86.2% – 100.0% | 100.0% | 100.0% – 100.0% |

## By company (single-company questions)

| Company | Questions | Attempts | Accuracy | Wilson 95% (attempts) | Question mean | Cluster bootstrap 95% |
|---|---:|---:|---:|---|---:|---|
| Michelin | 76 | 76 | 86.8% | 77.4% – 92.7% | 86.8% | 77.6% – 93.4% |
| Goodyear | 76 | 76 | 94.7% | 87.2% – 97.9% | 94.7% | 89.5% – 98.7% |
| Continental | 76 | 76 | 82.9% | 72.9% – 89.7% | 82.9% | 73.7% – 90.8% |
| Bridgestone | 76 | 76 | 78.9% | 68.5% – 86.6% | 78.9% | 69.7% – 88.2% |

## By wording

All 400 questions:

| Wording | Questions | Attempts | Accuracy | Wilson 95% (attempts) | Question mean | Cluster bootstrap 95% |
|---|---:|---:|---:|---|---:|---|
| formal | 100 | 100 | 81.0% | 72.2% – 87.5% | 81.0% | 73.0% – 88.0% |
| casual | 100 | 100 | 86.0% | 77.9% – 91.5% | 86.0% | 79.0% – 93.0% |
| terse | 100 | 100 | 83.0% | 74.5% – 89.1% | 83.0% | 76.0% – 90.0% |
| typo | 100 | 100 | 79.0% | 70.0% – 85.8% | 79.0% | 71.0% – 87.0% |

Answerable questions only:

| Wording | Questions | Attempts | Accuracy | Wilson 95% (attempts) | Question mean | Cluster bootstrap 95% |
|---|---:|---:|---:|---|---:|---|
| formal | 76 | 76 | 75.0% | 64.2% – 83.4% | 75.0% | 64.5% – 84.2% |
| casual | 76 | 76 | 82.9% | 72.9% – 89.7% | 82.9% | 73.7% – 90.8% |
| terse | 76 | 76 | 77.6% | 67.1% – 85.5% | 77.6% | 68.4% – 86.8% |
| typo | 76 | 76 | 72.4% | 61.4% – 81.2% | 72.4% | 61.8% – 81.6% |

Stratified permutation test of wording (all questions, 10,000 re-deals within design cells): p = 0.489.

Stratified permutation test of wording (answerable questions, 10,000 re-deals within design cells): p = 0.351.

Question-mean accuracy by type and wording (questions per cell in brackets):

| Type | formal | casual | terse | typo |
|---|---:|---:|---:|---:|
| number | 85.0% (20) | 95.0% (20) | 85.0% (20) | 90.0% (20) |
| text | 87.5% (16) | 87.5% (16) | 100.0% (16) | 87.5% (16) |
| calc | 93.8% (16) | 87.5% (16) | 87.5% (16) | 68.8% (16) |
| comparison | 25.0% (12) | 58.3% (12) | 33.3% (12) | 50.0% (12) |
| false_premise | 66.7% (12) | 75.0% (12) | 66.7% (12) | 50.0% (12) |
| not_found | 100.0% (12) | 91.7% (12) | 100.0% (12) | 100.0% (12) |
| out_of_scope | 100.0% (6) | 100.0% (6) | 100.0% (6) | 100.0% (6) |
| injection | 100.0% (6) | 100.0% (6) | 100.0% (6) | 100.0% (6) |

## Company by type (single-company questions)

| Company | number | text | calc | false_premise | not_found |
|---|---:|---:|---:|---:|---:|
| Michelin | 95.0% (20) | 81.2% (16) | 81.2% (16) | 75.0% (12) | 100.0% (12) |
| Goodyear | 100.0% (20) | 100.0% (16) | 100.0% (16) | 66.7% (12) | 100.0% (12) |
| Continental | 85.0% (20) | 87.5% (16) | 81.2% (16) | 66.7% (12) | 91.7% (12) |
| Bridgestone | 75.0% (20) | 93.8% (16) | 75.0% (16) | 50.0% (12) | 100.0% (12) |

## Comparisons by company pair

| Pair | Questions | Attempts | Accuracy | Wilson 95% (attempts) | Question mean | Cluster bootstrap 95% |
|---|---:|---:|---:|---|---:|---|
| Continental,Bridgestone | 8 | 8 | 0.0% | 0.0% – 32.4% | 0.0% | 0.0% – 0.0% |
| Goodyear,Bridgestone | 8 | 8 | 37.5% | 13.7% – 69.4% | 37.5% | 12.5% – 75.0% |
| Goodyear,Continental | 8 | 8 | 37.5% | 13.7% – 69.4% | 37.5% | 12.5% – 75.0% |
| Michelin,Bridgestone | 8 | 8 | 25.0% | 7.1% – 59.1% | 25.0% | 0.0% – 62.5% |
| Michelin,Continental | 8 | 8 | 50.0% | 21.5% – 78.5% | 50.0% | 12.5% – 87.5% |
| Michelin,Goodyear | 8 | 8 | 100.0% | 67.6% – 100.0% | 100.0% | 100.0% – 100.0% |

## Logistic model (single-company questions)

Firth-penalized logistic regression, 304 attempts on 304 questions, standard errors clustered by question. Odds ratios are against the reference level.

| Factor | Reference | Wald χ² | df | p |
|---|---|---:|---:|---:|
| company | Michelin | 10.97 | 3 | 0.012 |
| type | number | 22.62 | 4 | 0.000 |
| wording | formal | 3.05 | 3 | 0.384 |

| Term | Odds ratio | 95% CI | p |
|---|---:|---|---:|
| company=Goodyear | 2.69 | 0.95 – 7.61 | 0.062 |
| company=Continental | 0.72 | 0.29 – 1.79 | 0.483 |
| company=Bridgestone | 0.55 | 0.23 – 1.30 | 0.175 |
| type=text | 1.20 | 0.44 – 3.31 | 0.724 |
| type=calc | 0.68 | 0.28 – 1.70 | 0.413 |
| type=false_premise | 0.23 | 0.09 – 0.56 | 0.001 |
| type=not_found | 4.28 | 0.99 – 18.46 | 0.051 |
| wording=casual | 1.14 | 0.43 – 3.01 | 0.798 |
| wording=terse | 1.14 | 0.43 – 2.97 | 0.796 |
| wording=typo | 0.59 | 0.24 – 1.44 | 0.247 |

## Retrieval or generation?

Evidence was retrieved in 97.7% of answerable attempts. Accuracy was 78.5% when it was and 14.3% when it wasn't; 64 wrong answers had the evidence in hand (a generation or reasoning failure) and 7 attempts never retrieved it.

## Grading check: LLM judge vs. model-free first pass

304 answerable attempts: agreement 93.4%, Cohen's κ = 0.80. The judge passed 1 that the first pass didn't, and failed 19 that it passed. Each disagreement deserves a read; the first pass misses paraphrased names and unusual number formats, and the judge can be lenient on near-misses.

| ID | Run | Judge | First pass | Judge's reason |
|---|---:|---|---|---|
| MI-N18 | 1 | fail | pass | The expected cost is €668 million, but the answer states €665 million (€665,000,000). The figure for the asked metric does not match. |
| MI-T12 | 1 | fail | pass | The answer captures the main idea that Michelin’s sales fell mainly due to lower volumes and that price-mix partly offset this, but it misse |
| MI-C10 | 1 | fail | pass | The answer gives the right percentage change (down about 11.9%) but reverses the direction of the figures. EXPECTED says net cash from opera |
| MI-P04 | 1 | fail | pass | The answer correctly rejects the false premise and gives the overall workforce figure, but it does not provide the required regional split.  |
| CO-N18 | 1 | fail | pass | The expected figure for ‘continental operating cash flow 2025’ is €2,014 million. The answer does mention €2,014 million, but it gives it on |
| CO-C10 | 1 | fail | pass | EXPECTED says Continental's share price was up about 40.2% in 2025, from €48.49 to €67.96 adjusted for the Aumovio spin-off. The answer give |
| CO-P04 | 1 | pass | fail | The answer gives the correct number of employees in Continental's Tires segment: 56,187. It matches the expected figure and is consistent wi |
| CO-P08 | 1 | fail | pass | EXPECTED says Continental’s free cash flow from continuing operations increased to €967 million from €603 million, so the premise that it de |
| CO-P06 | 1 | fail | pass | The answer does not match the expected reference. The question is based on a false premise: Wolfgang Reitzle is not Continental’s CEO; he ch |
| CO-P10 | 1 | fail | pass | The answer gets the direction right that net indebtedness did not fall and ended at €5,154 million, but it does not match EXPECTED on the re |
| BS-N01 | 1 | fail | pass | The answer gives 485.6 billion JPY, but the expected adjusted operating profit for Bridgestone in 2024 is 483.3 billion JPY. The figure does |
| BS-C15 | 1 | fail | pass | The answer gives the ratio as about 0.54, but EXPECTED is about 0.51 (1,937.0 / 3,786.5 billion JPY). Since the asked-about metric differs,  |
| X-MC7 | 1 | fail | pass | The answer gives Michelin employees as 122,586 instead of the expected 122,600, and therefore the difference is 29,933 instead of about 29,9 |
| X-MB2 | 1 | fail | pass | The answer gives Bridgestone as 3%, but the expected figure is 2.9%. Since the asked-about metric differs from EXPECTED, the comparison is n |
| X-MB3 | 1 | fail | pass | The answer gets Michelin correct at 6.4%, but Bridgestone is wrong: EXPECTED says Bridgestone’s net profit margin was about 6.4% (profit att |
| X-GC7 | 1 | fail | pass | The question asks whether Goodyear and Continental use the same auditor. Expected answer is yes: both are audited by PricewaterhouseCoopers  |
| X-GC4 | 1 | fail | pass | The answer gets Goodyear correct at 5.8%, but it gives Continental as 1.4% instead of the expected 10.3% adjusted EBIT margin. Although it l |
| X-GC8 | 1 | fail | pass | The answer is incorrect because it fails to identify Continental’s head of finance as expected. Expected: Goodyear CFO Christina L. Zamarro; |
| X-CB8 | 1 | fail | pass | The answer gives Bridgestone as 3.0%, but EXPECTED says Bridgestone was 2.9% in 2024, roughly the same as Continental’s 2.9%. Since the aske |
| X-CB4 | 1 | fail | pass | The answer gets Continental right at 23.4%, but Bridgestone is not correctly reported. EXPECTED asks for Bridgestone’s end-2024 equity ratio |

## Precision of this design

Smallest drop from the observed answerable accuracy (77.0%) detectable with 80% power (two-sided α = 0.05, one observation per question):

| Comparison | Questions per group | Detectable drop | 95% CI half-width |
|---|---:|---:|---:|
| wording level, all questions | 100 | 18.5% | ±8.3% |
| wording level, answerable questions | 76 | 21.5% | ±9.5% |
| company, single-company questions | 76 | 21.5% | ±9.5% |
| question type (number) | 80 | 20.7% | ±9.2% |
| question type (calc, text) | 64 | 23.5% | ±10.3% |
| company x type cell (number) | 20 | 42.7% | ±18.5% |

## Questions that failed at least once

| ID | Type | Wording | Passed | Question | Note (most recent failure) |
|---|---|---|---:|---|---|
| BS-C03 | calc | casual | 0/1 | what share of bridgestone's 2024 revenue came from the americas segment? | not answered |
| BS-C07 | calc | typo | 0/1 | What was Bridgestone's total equuity as a perceentage of total assets at the end of 2024? | The answer gives 65% as the total equity ratio, but the expected value is about 66.2% (3,786.5 / 5,723.5 billion JPY). It also conflates this with the |
| BS-C10 | calc | terse | 0/1 | bridgestone americas share of employees end 2024 | The answer gives the Americas employee share as 33%, but EXPECTED is about 39.5% (47,946 of 121,464). The figure for the asked metric is incorrect, so |
| BS-C15 | calc | formal | 0/1 | What was Bridgestone's ratio of total liabilities to total equity at the end of 2024? | The answer gives the ratio as about 0.54, but EXPECTED is about 0.51 (1,937.0 / 3,786.5 billion JPY). Since the asked-about metric differs, it is inco |
| BS-N01 | number | formal | 0/1 | What was Bridgestone's adjusted operating profit in 2024? | The answer gives 485.6 billion JPY, but the expected adjusted operating profit for Bridgestone in 2024 is 483.3 billion JPY. The figure does not match |
| BS-N04 | number | typo | 0/1 | What were Bridgestone's ttal asseets at the end of 2024? | not answered |
| BS-N07 | number | typo | 0/1 | What was Bridgestone's reeturn on eauity (ROE) in 2024? | not answered |
| BS-N13 | number | casual | 0/1 | how much revenue did bridgestone's americas segment bring in during 2024? | not answered |
| BS-N14 | number | terse | 0/1 | bridgestone japan segment adjusted operating margin 2024 | not answered |
| BS-P02 | false_premise | typo | 0/1 | Why was Bridgestone's adjuted oeprating profit margin so high at 18% in 2024? | not answered |
| BS-P04 | false_premise | formal | 0/1 | Bridgestone's 2024 R&D expenses were 400 billion yen; what share of revenue is that? | The answer fails to reject the false premise and gives an incorrect share. EXPECTED says Bridgestone’s 2024 R&D expenses were 126.2 billion JPY, which |
| BS-P07 | false_premise | casual | 0/1 | what's naoki hishinuma focused on as bridgestone's global CEO? | not answered |
| BS-P08 | false_premise | terse | 0/1 | bridgestone 2024 profit attributable to owners rise why | not answered |
| BS-P11 | false_premise | typo | 0/1 | When did Bridgestone mrege wtih Goodyear? | not answered |
| BS-P12 | false_premise | formal | 0/1 | Why did Bridgestone drop its Nominating Committee governance structure in 2024? | not answered |
| BS-T07 | text | formal | 0/1 | What are the commitments in the Bridgestone E8 Commitment? | not answered |
| CO-C10 | calc | typo | 0/1 | By what percenttage did Continental's share price chajge during 2025? | EXPECTED says Continental's share price was up about 40.2% in 2025, from €48.49 to €67.96 adjusted for the Aumovio spin-off. The answer gives 40.1% in |
| CO-C11 | calc | casual | 0/1 | how much did continental's operating cash flow change in 2025, in %? | The answer gives the wrong operating cash flow change and figures. Expected is an increase of about 23.7% from €1,628 million to €2,014 million, but t |
| CO-C16 | calc | terse | 0/1 | continental capex change 2024 to 2025 % | The answer gives the wrong CapEx figures and percentage. Expected is an increase from about €1,251 million to €1,316 million, or about +5.2%. The answ |
| CO-N16 | number | terse | 0/1 | continental capex 2025 | The answer does not match the expected figure. EXPECTED says Continental capex for 2025 is €1,316 million (continuing operations), but the answer give |
| CO-N18 | number | terse | 0/1 | continental operating cash flow 2025 | The expected figure for ‘continental operating cash flow 2025’ is €2,014 million. The answer does mention €2,014 million, but it gives it only as ‘con |
| CO-N20 | number | formal | 0/1 | What were Continental's depreciation and amortization in 2025? | The expected depreciation and amortization in 2025 is €1,586 million (8.1% of sales), but the answer gives €1,277 million. The figure does not match t |
| CO-P06 | false_premise | casual | 0/1 | what's wolfgang reitzle been prioritizing as continental's CEO? | The answer does not match the expected reference. The question is based on a false premise: Wolfgang Reitzle is not Continental’s CEO; he chairs the S |
| CO-P07 | false_premise | typo | 0/1 | What are Ulrike Hintze's gals as heead of ContiTech? | not answered |
| CO-P08 | false_premise | typo | 0/1 | Why did Continental's free caash flow deecline in 2025? | EXPECTED says Continental’s free cash flow from continuing operations increased to €967 million from €603 million, so the premise that it declined is  |
| CO-P10 | false_premise | terse | 0/1 | continental net indebtedness fall 2025 reason | The answer gets the direction right that net indebtedness did not fall and ended at €5,154 million, but it does not match EXPECTED on the reason. EXPE |
| CO-T03 | text | typo | 0/1 | Which Executive Board member is responnsible for Continental's ContiTech group sdctor? | not answered |
| CO-T08 | text | casual | 0/1 | what's OESL and what happened with it? | not answered |
| CO-U09 | not_found | casual | 0/1 | what was continental's net promoter score in 2025? | The answer gives a specific figure (0.707) as Continental’s 2025 net promoter score instead of making clear that the reports do not provide this metri |
| GY-P03 | false_premise | formal | 0/1 | What drove Goodyear's $2.1 billion of capital expenditures in 2025? | not answered |
| GY-P06 | false_premise | terse | 0/1 | nathaniel madarang goodyear CFO priorities | not answered |
| GY-P09 | false_premise | formal | 0/1 | What drove the increase in Goodyear's Asia Pacific net sales in 2025? | not answered |
| GY-P11 | false_premise | typo | 0/1 | When in 2025 did Goodyear sll its Americas tire busiess? | not answered |
| MI-C10 | calc | typo | 0/1 | By what percentage did Michelin's net cash from opreating activiteis change in 2025? | The answer gives the right percentage change (down about 11.9%) but reverses the direction of the figures. EXPECTED says net cash from operating activ |
| MI-C14 | calc | typo | 0/1 | What was Michelin's grss marrgin in 2025? | not answered |
| MI-C16 | calc | typo | 0/1 | How much did Michelin return to shareholders in 2025 through divdends and sahre buybacks combined? | The answer is very close, but it does not match the expected combined amount. Expected is about €1,642 million, made up of €974 million in dividends p |
| MI-N18 | number | formal | 0/1 | How much did Michelin's 2025 share buyback program cost? | The expected cost is €668 million, but the answer states €665 million (€665,000,000). The figure for the asked metric does not match. |
| MI-P04 | false_premise | typo | 0/1 | Michelin has 200,000 employees; how are they solit by retion? | The answer correctly rejects the false premise and gives the overall workforce figure, but it does not provide the required regional split. EXPECTED s |
| MI-P11 | false_premise | terse | 0/1 | michelin downgraded to BBB 2025 why | not answered |
| MI-P12 | false_premise | casual | 0/1 | why's yves chapot running for re-election as michelin's general manager in 2026? | not answered |
| MI-T02 | text | formal | 0/1 | Who chairs Michelin's Supervisory Board? | not answered |
| MI-T12 | text | casual | 0/1 | why did michelin's sales go down in 2025? | The answer captures the main idea that Michelin’s sales fell mainly due to lower volumes and that price-mix partly offset this, but it misses a key EX |
| MI-T14 | text | typo | 0/1 | Who sts on Michelin's Stakeholders Committee? | not answered |
| X-CB1 | comparison | formal | 0/1 | Which has more employees, Continental or Bridgestone? | The expected answer says Bridgestone has 121,464 employees and Continental has 92,653, so Bridgestone has more employees. The response fails to provid |
| X-CB2 | comparison | casual | 0/1 | how does capex as a % of sales compare between continental and bridgestone? | Continental matches the expected 6.7%, but Bridgestone does not: expected is about 8.8% (2024), while the answer gives 9.4%. Since the asked-about met |
| X-CB3 | comparison | typo | 0/1 | Compare the operating margiins repotred by Continental and Bridgestone. | Continental’s 10.3% matches EXPECTED, but Bridgestone’s margin is incorrect. EXPECTED says Bridgestone’s adjusted operating profit margin was 10.9% (2 |
| X-CB4 | comparison | typo | 0/1 | Compare the euity ratois of Continental and Bridgestone. | The answer gets Continental right at 23.4%, but Bridgestone is not correctly reported. EXPECTED asks for Bridgestone’s end-2024 equity ratio of about  |
| X-CB5 | comparison | formal | 0/1 | Who are the chief financial officers of Continental and Bridgestone? | The answer correctly names Bridgestone’s CFO as Naoki Hishinuma, but it fails to identify Continental’s CFO. Expected is Roland Welzbacher (Group Fina |
| X-CB6 | comparison | terse | 0/1 | continental vs bridgestone latest revenue growth | Continental matches the expected figure (-2.0%), but Bridgestone does not. Expected says Bridgestone's revenue rose about 2.7% in 2024, while the answ |
| X-CB7 | comparison | casual | 0/1 | was continental or bridgestone profitable in their latest year? | The answer is incorrect because it fails to identify Bridgestone as profitable in its latest year. EXPECTED states Bridgestone had profit attributable |
| X-CB8 | comparison | terse | 0/1 | continental vs bridgestone r&d % revenue | The answer gives Bridgestone as 3.0%, but EXPECTED says Bridgestone was 2.9% in 2024, roughly the same as Continental’s 2.9%. Since the asked-about me |
| X-GB1 | comparison | casual | 0/1 | how many more employees does bridgestone have compared to goodyear? | The answer does not give the requested difference in employees. Expected: Bridgestone has about 58,464 more employees than Goodyear (121,464 vs about  |
| X-GB2 | comparison | terse | 0/1 | goodyear vs bridgestone r&d % revenue | The answer gives Goodyear correctly at 2.1%, but Bridgestone is listed as 3.0% instead of the expected 2.9%. Since the asked-about metric differs, the |
| X-GB3 | comparison | formal | 0/1 | Compare capital expenditure as a percentage of revenue at Goodyear and Bridgestone. | The answer gets Goodyear correct at 4.5%, but Bridgestone is incorrect. Expected is about 8.8% (2024), while the answer gives 9.4%. Since the asked me |
| X-GB5 | comparison | terse | 0/1 | goodyear vs bridgestone operating margin | The answer gets Goodyear correct at 5.8%, but it does not match the expected Bridgestone figure. Expected Bridgestone adjusted operating profit margin |
| X-GB6 | comparison | formal | 0/1 | Compare Goodyear's and Bridgestone's net margins. | The answer gets Goodyear right at about -9.4%, but it fails to provide Bridgestone’s net margin of 6.4% for 2024 as required by the expected compariso |
| X-GC1 | comparison | formal | 0/1 | Compare Goodyear's and Continental's research and development spending as a share of sales in 2025. | The answer gets Goodyear correct at 2.1%, but it fails to provide Continental’s 2025 R&D spending as a share of sales. Expected says Continental is ab |
| X-GC3 | comparison | formal | 0/1 | Which has more employees, Goodyear or Continental? | The answer identifies the correct company, but the employee figure for Continental does not match EXPECTED. EXPECTED says Continental has 92,653 emplo |
| X-GC4 | comparison | typo | 0/1 | Compare the oprating margins Goodyear and Continental repotred for 2025. | The answer gets Goodyear correct at 5.8%, but it gives Continental as 1.4% instead of the expected 10.3% adjusted EBIT margin. Although it later menti |
| X-GC7 | comparison | typo | 0/1 | Do Goodyear and Continental use the saame audtor? | The question asks whether Goodyear and Continental use the same auditor. Expected answer is yes: both are audited by PricewaterhouseCoopers (PwC). The |
| X-GC8 | comparison | terse | 0/1 | goodyear vs continental head of finance | The answer is incorrect because it fails to identify Continental’s head of finance as expected. Expected: Goodyear CFO Christina L. Zamarro; Continent |
| X-MB2 | comparison | casual | 0/1 | who spends more of their revenue on r&d, michelin or bridgestone? | The answer gives Bridgestone as 3%, but the expected figure is 2.9%. Since the asked-about metric differs from EXPECTED, the comparison is not correct |
| X-MB3 | comparison | formal | 0/1 | Compare Michelin's and Bridgestone's net profit margins. | The answer gets Michelin correct at 6.4%, but Bridgestone is wrong: EXPECTED says Bridgestone’s net profit margin was about 6.4% (profit attributable  |
| X-MB4 | comparison | terse | 0/1 | michelin vs bridgestone capex % revenue | Michelin matches the expected 7.6%, but Bridgestone is incorrect: the expected figure is about 8.8% for 2024, not 9.4%. Since the asked-about metric d |
| X-MB5 | comparison | formal | 0/1 | Compare the operating margins reported by Michelin and Bridgestone. | The answer correctly gives Michelin's operating margin as 10.5%, but it fails to report Bridgestone's operating margin from the expected reference. EX |
| X-MB7 | comparison | typo | 0/1 | Compare the latest anunal revenue gdowth of Michelin and Bridgestone. | The answer does not match the expected figures. EXPECTED says Michelin's sales fell 4.4% in 2025 and Bridgestone's revenue rose about 2.7% in 2024. Th |
| X-MB8 | comparison | terse | 0/1 | michelin vs bridgestone operating cash flow % revenue | Michelin matches the expected 14.7%, but Bridgestone is incorrect: the expected figure is about 12.4% (2024), while the answer gives 12.7%. Since the  |
| X-MC1 | comparison | casual | 0/1 | how does michelin's 2025 r&d spend compare with continental's? | The answer gets Michelin’s 2025 R&D spend correct at €788 million, but it does not provide Continental’s 2025 R&D spend as expected. The expected comp |
| X-MC2 | comparison | formal | 0/1 | Which company spent more on capital expenditure in 2025, Michelin or Continental, and by how much? | The answer gets Michelin’s 2025 capital expenditure correct, but Continental’s figure is wrong. Expected is €1,316 million, not €1,752 million. Theref |
| X-MC7 | comparison | terse | 0/1 | michelin minus continental employees | The answer gives Michelin employees as 122,586 instead of the expected 122,600, and therefore the difference is 29,933 instead of about 29,947. Since  |
| X-MC8 | comparison | typo | 0/1 | Compare Michelin's and Continental's cash flow from opearting activiites in 2025. | The answer gives Michelin’s cash flow correctly at €3,819 million, but Continental’s figure is incorrect. Expected is €2,014 million, not €2,193 milli |

Median latency 5.1 s · about 2,146,166 tokens per run (answers and grading).
