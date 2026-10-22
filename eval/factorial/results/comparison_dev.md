# System Comparison

**A:** openai (gpt-5.4-mini) (1 run(s)) · **B:** local (qwen2.5-7b-16k) (1 run(s)) · 100 matched questions, both graded by the same OpenAI judge.

Each question contributes its pass rate across runs; differences are paired by question.

## Headline

| | Questions | A | B | A − B | Paired bootstrap 95% | Sign-flip p |
|---|---:|---:|---:|---:|---|---:|
| All questions | 100 | 82.0% | 24.0% | +58.0 pts | +48.0 pts to +68.0 pts | 0.000 |
| Answerable | 76 | 76.3% | 0.0% | +76.3 pts | +67.1 pts to +85.5 pts | 0.000 |

First run only (run 1): both right 24, A only 58, B only 0, neither 18. McNemar exact p = 0.0000 (mid-p 0.0000); A − B = +58.0 pts, Newcombe 95% +47.1 pts to +66.3 pts.

## By question type

| Type | Questions | A | B | A − B | Paired bootstrap 95% | Sign-flip p |
|---|---:|---:|---:|---:|---|---:|
| number | 20 | 80.0% | 0.0% | +80.0 pts | +60.0 pts to +95.0 pts | 0.000 |
| text | 16 | 93.8% | 0.0% | +93.8 pts | +81.2 pts to +100.0 pts | 0.000 |
| calc | 16 | 93.8% | 0.0% | +93.8 pts | +81.2 pts to +100.0 pts | 0.001 |
| comparison | 12 | 41.7% | 0.0% | +41.7 pts | +16.7 pts to +66.7 pts | 0.054 |
| false_premise | 12 | 58.3% | 0.0% | +58.3 pts | +33.3 pts to +83.3 pts | 0.015 |
| not_found | 12 | 100.0% | 100.0% | +0.0 pts | +0.0 pts to +0.0 pts | 1.000 |
| out_of_scope | 6 | 100.0% | 100.0% | +0.0 pts | +0.0 pts to +0.0 pts | 1.000 |
| injection | 6 | 100.0% | 100.0% | +0.0 pts | +0.0 pts to +0.0 pts | 1.000 |

## By wording

| Wording | Questions | A | B | A − B | Paired bootstrap 95% | Sign-flip p |
|---|---:|---:|---:|---:|---|---:|
| formal | 26 | 73.1% | 23.1% | +50.0 pts | +30.8 pts to +69.2 pts | 0.001 |
| casual | 23 | 95.7% | 30.4% | +65.2 pts | +43.5 pts to +82.6 pts | 0.000 |
| terse | 25 | 72.0% | 24.0% | +48.0 pts | +28.0 pts to +68.0 pts | 0.001 |
| typo | 26 | 88.5% | 19.2% | +69.2 pts | +50.0 pts to +88.5 pts | 0.000 |

## By company (single-company questions)

| Company | Questions | A | B | A − B | Paired bootstrap 95% | Sign-flip p |
|---|---:|---:|---:|---:|---|---:|
| Michelin | 19 | 89.5% | 15.8% | +73.7 pts | +52.6 pts to +89.5 pts | 0.001 |
| Goodyear | 19 | 89.5% | 15.8% | +73.7 pts | +52.6 pts to +89.5 pts | 0.000 |
| Continental | 19 | 78.9% | 15.8% | +63.2 pts | +42.1 pts to +84.2 pts | 0.000 |
| Bridgestone | 19 | 84.2% | 15.8% | +68.4 pts | +47.4 pts to +89.5 pts | 0.000 |

## Where does B lose ground?

Firth logistic regression on 152 attempts (76 single-company questions, both systems), errors clustered by question. The interaction tests ask whether B's gap changes with wording or question type.

| Term set | Wald χ² | df | p |
|---|---:|---:|---:|
| system | 23.05 | 1 | 0.000 |
| company | 2.31 | 3 | 0.511 |
| type | 20.46 | 4 | 0.000 |
| wording | 2.73 | 3 | 0.435 |
| system x wording | 1.92 | 3 | 0.588 |
| system x type | 102.60 | 4 | 0.000 |

| Term | Odds ratio | 95% CI | p |
|---|---:|---|---:|
| system=b | 0.02 | 0.00 – 0.09 | 0.000 |
| system=b x wording=casual | 0.42 | 0.05 – 3.44 | 0.421 |
| system=b x wording=terse | 1.24 | 0.26 – 5.88 | 0.789 |
| system=b x wording=typo | 0.46 | 0.07 – 3.10 | 0.422 |
| system=b x type=text | 0.43 | 0.06 – 3.01 | 0.394 |
| system=b x type=calc | 0.43 | 0.06 – 3.15 | 0.405 |
| system=b x type=false_premise | 3.61 | 0.66 – 19.73 | 0.139 |
| system=b x type=not_found | 56.51 | 16.04 – 199.11 | 0.000 |

## How answers end

| Type | A | B |
|---|---|---|
| number | answered 20 | not_found 19, out_of_scope 1 |
| text | answered 16 | not_found 12, out_of_scope 3, failed 1 |
| calc | answered 16 | not_found 13, out_of_scope 3 |
| comparison | answered 12 | not_found 9, answered 1, out_of_scope 1, failed 1 |
| false_premise | answered 8, not_found 4 | not_found 11, failed 1 |
| not_found | not_found 8, out_of_scope 4 | not_found 6, out_of_scope 6 |
| out_of_scope | out_of_scope 6 | out_of_scope 6 |
| injection | blocked 4, out_of_scope 2 | blocked 4, out_of_scope 2 |

Median latency: A 5.1 s, B 20.4 s.

## Questions the systems split on

Pass rates differ by at least half (most recent answers shown).

| ID | Type | Wording | A | B | Question | A's answer | B's answer |
|---|---|---|---:|---:|---|---|---|
| BS-C02 | calc | typo | 100.0% | 0.0% | By what percentwge did Bridgestone's adjusted operating profit chnage from 2023 to 2024? | Bridgestone’s **adjusted operating profit increased by about 0.6%** from 2023 to 2024. Calculation: \((483.3 - 480.6) /  | The provided excerpts do not contain the specific information required to calculate Bridgestone's adjusted operating pro |
| BS-C05 | calc | terse | 100.0% | 0.0% | bridgestone FCF % of revenue 2024 | Bridgestone’s 2024 free cash flow was **293.8 Billion JPY** and 2024 revenue was **4,430.1 billion JPY**, so **FCF as a  | The provided excerpts do not contain the Free Cash Flow (FCF) % of revenue for 2024. The report does not provide the req |
| BS-C14 | calc | casual | 100.0% | 0.0% | by how much (in %) did bridgestone's profit attributable to owners of the parent change from 2023 to 2024? | Bridgestone’s **profit attributable to owners of parent** decreased by **about 14.0%** from 2023 to 2024. Calculation: \ | The provided excerpts do not contain Bridgestone's profit attributable to owners of the parent figures for 2023 and 2024 |
| BS-C16 | calc | formal | 100.0% | 0.0% | By what percentage did Bridgestone's operating cash flow change from 2023 to 2024? | Bridgestone’s operating cash flow **decreased by about 17.0%** from 2023 to 2024. Calculation: - 2023: **661.4 billion J | The provided excerpts do not contain specific figures for Bridgestone's operating cash flow for 2023 and 2024. The table |
| CO-C01 | calc | formal | 100.0% | 0.0% | By what percentage did Continental's sales change from 2024 to 2025? | Continental’s sales **decreased by 2.0%** from 2024 to 2025. The report shows sales of **€19,676 million** in 2025 versu | The provided excerpts do not include the specific sales figures for Continental in both 2024 and 2025. The closest infor |
| CO-C14 | calc | terse | 100.0% | 0.0% | continental sales per employee 2025 | Continental’s 2025 **sales per employee** were **about €212,400 per employee**. Calculation: **€19,676 million sales ÷ 9 | The report excerpts do not provide sales figures and employee numbers for 2025 specifically needed to calculate sales pe |
| CO-C15 | calc | casual | 100.0% | 0.0% | how much did continental's tires sector sell per tires employee in 2025? | Continental’s Tires group sector sold about **€245,600 per Tires employee** in 2025. Calculation: **€13,798 million sale | I can only answer questions about the four companies' 2025 annual reports. |
| GY-C06 | calc | casual | 100.0% | 0.0% | can you work out goodyear's gross margin for 2025 from sales and cost of goods sold? | Yes. Using Goodyear’s consolidated 2025 figures, net sales were **$18,280 million** and cost of goods sold was **$14,909 | The provided excerpts do not contain the necessary information to calculate Goodyear's gross margin for 2025 directly us |
| GY-C08 | calc | formal | 100.0% | 0.0% | What share of Goodyear's total assets was funded by total shareholders' equity at the end of 2025? | At the end of 2025, Goodyear’s total shareholders’ equity funded about **18.7%** of total assets. Calculation: **$3,403  | The provided excerpts do not contain the necessary information to calculate the share of Goodyear's total assets that we |
| GY-C12 | calc | terse | 100.0% | 0.0% | goodyear asia pacific vs emea operating margin gap 2025 | Goodyear’s **Asia Pacific operating margin was 10.6%** in 2025, while **EMEA’s operating margin was 2.1%** in 2025. The  | The reports don't support an answer to: goodyear asia pacific operating margin 2025; goodyear emea operating margin 2025 |
| GY-C15 | calc | typo | 100.0% | 0.0% | By what percentage did Goodyear's interest exxpense chnage from 2024 to 2025? | Goodyear’s interest expense decreased by **about 14.8%** from 2024 to 2025. Calculation: \((445 - 522) / 522 \times 100  | The provided excerpts do not contain information about Goodyear's interest expense for 2024 and 2025. They instead discu |
| MI-C01 | calc | terse | 100.0% | 0.0% | michelin operating income % of sales 2025 | Michelin’s **2025 operating income as a percentage of sales** was **9.1%**. This comes from the consolidated income stat | The report excerpts provided do not contain the specific operating income percentage of sales for Michelin in 2025. The  |
| MI-C04 | calc | casual | 100.0% | 0.0% | michelin's capex as a % of sales in 2025 - what was it? | Michelin’s **capex as a % of sales in 2025 was 7.6%**. The report’s capital expenditure table shows **“Additions to inta | The provided excerpts do not contain Michelin's capital expenditure (Capex) as a percentage of sales for 2025. The close |
| MI-C06 | calc | formal | 100.0% | 0.0% | By what percentage did segment operating income in Michelin's Road transportation segment change in 2025? | Michelin’s Road transportation segment operating income **decreased by 53.1%** in 2025 versus 2024. The report shows seg | The provided excerpts do not contain specific information on the percentage change in Segment operating income for Miche |
| MI-C12 | calc | typo | 100.0% | 0.0% | What were Michelin's 2025 saels per emploeye? | Michelin’s 2025 sales per employee were approximately **€212,000 per employee**. Calculation: **€26bn sales / 122,600 gl | The provided excerpts do not contain specific financial metrics for sales per employee for Michelin in 2025. The excerpt |
| X-GB4 | comparison | typo | 100.0% | 0.0% | Which compnay is olfer, Goodyear or Bridgestone? | / Company / Establishment year / Older? / /---/---:/---/ / Goodyear / 1898 / Yes / / Bridgestone / 1931 / No / Goodyear  | I can only answer questions about the four companies' 2025 annual reports. |
| X-MC3 | comparison | casual | 100.0% | 0.0% | michelin's net income vs continental's (attributable to shareholders) in 2025 - how do they compare? | / Company / 2025 figure / Comparison / /---/---:/---:/ / Michelin / €1,664 million net income / Higher by €1,829 million | Not found. The provided information did not contain a specific net income figure for Michelin attributable to shareholde |
| X-MC4 | comparison | typo | 100.0% | 0.0% | Compare Michelin's and Continental's frree cash fow in 2025. | / Company / 2025 free cash flow / /---/---:/ / Michelin / €2,126 million before M&A; €2,181 million after M&A / / Contin | The reports don't support an answer to: What is Michelin's free cash flow in 2025?; What is Continental's free cash flow |
| X-MG1 | comparison | formal | 100.0% | 0.0% | Which spent a larger share of sales on research and development in 2025, Michelin or Goodyear? | / Company / R&D as % of sales in 2025 / /---/---:/ / Michelin / 3.0% / / Goodyear / 2.1% / Michelin spent the larger sha | The reports don't support an answer to: What percent of sales did Michelin spend on research and development in 2025?; W |
| X-MG5 | comparison | casual | 100.0% | 0.0% | how do michelin's and goodyear's 2025 operating margins stack up? | / Company / 2025 operating margin / /---/---:/ / Michelin / 10.5% / / Goodyear / 5.8% / Michelin’s operating margin was  | The reports don't support an answer to: What was Michelin's 2025 operating margin?; What was Goodyear's 2025 operating m |
| BS-P09 | false_premise | typo | 100.0% | 0.0% | Why is Bridgestone ctting its dividrnd for 2025? | Bridgestone is **not cutting** its 2025 dividend in the excerpts; it says it plans to **increase** it. The report says i | The provided excerpts do not contain information specifically addressing why Bridgestone is cutting its dividend for 202 |
| CO-P04 | false_premise | casual | 100.0% | 0.0% | continental has like 190,000 employees - how many are in tires? | Continental had **56,187 employees in the Tires group sector** as of December 31, 2025. The excerpt says: “The number of | The provided excerpts do not contain the specific number of employees in the tire sector. While the report mentions the  |
| CO-P05 | false_premise | typo | 100.0% | 0.0% | As Continental's CFO, waht is Christian Kötz resppnsible for? | The excerpts do **not** identify Christian Kötz as Continental’s CFO. They say he is the **Chairman of the Executive Boa | The provided excerpts do not specify Christian Kötz's exact responsibilities as Continental's CFO. While his roles are l |
| GY-P04 | false_premise | formal | 100.0% | 0.0% | Goodyear's Americas segment earned a 12% operating margin in 2025, right? | No. Goodyear’s **Americas** segment operating margin in **2025** was **6.8%**, not 12%. / Segment / 2025 operating margi | LengthFinishReasonError: Could not parse response content as the length limit was reached - CompletionUsage(completion_t |
| MI-P03 | false_premise | terse | 100.0% | 0.0% | michelin ROCE up to 12% 2025 drivers | Michelin’s **2025 consolidated ROCE was 9.2%**, not 12%: “**Consolidated ROCE 9.2%**” and “**ROCE stood at 9.2%**” ([Mic | The provided excerpts do not contain any information directly supporting Michelin's ROCE reaching 12% in 2025. The close |
| MI-P05 | false_premise | formal | 100.0% | 0.0% | What is Barbara Dalibard's role as Michelin's CFO? | Barbara Dalibard is **not Michelin’s CFO** in the excerpts provided. Her role is listed as **“Non-independent member of  | The provided excerpts do not mention Barbara Dalibard's role as Michelin's CFO. The excerpts discuss her role as the Cha |
| MI-P08 | false_premise | casual | 100.0% | 0.0% | why did michelin's sales grow in 2025? | Michelin’s **consolidated sales did not grow in 2025**; they **declined to €25,992 million**, down **4.4%** from 2024. T | The provided excerpts do not explicitly state the reasons for Michelin's sales growth in 2025. The excerpts discuss vari |
| BS-N02 | number | casual | 100.0% | 0.0% | what was bridgestone's adjusted operating margin in 2024? | Bridgestone’s **adjusted operating margin in 2024 was 10.9%**. This is calculated from the report’s **2025 plan margin o | The provided excerpts from Bridgestone's 2025 annual report do not contain specific information on the adjusted operatin |
| BS-N06 | number | typo | 100.0% | 0.0% | What was Bridgestone's reyurn on invested capiital (ROIC) in 2024? | Bridgestone’s ROIC in 2024 was **8.2%**. The report states: “In 2024, we recorded business rebuilding costs of about 100 | The provided excerpts do not contain the exact figure for Bridgestone's return on invested capital (ROIC) in 2024. The c |
| BS-N10 | number | terse | 100.0% | 0.0% | bridgestone capex 2024 | Bridgestone’s **capital expenditure in 2024** was **389.8 B JPY**. In the table, 2024 is shown as **“142.1”** ordinary i | The excerpts provided do not contain a specific figure for Bridgestone's capital expenditure (Capex) in 2024. The closes |
| BS-N20 | number | typo | 100.0% | 0.0% | What share of Bridgestone's emloyees were woen at the end of 2024? | At the end of 2024, **12.5%** of Bridgestone’s employees were women. The report’s “Ratio of female employees” shows **“T | The provided report excerpts do not contain specific information about the gender distribution or the share of women amo |
| CO-N02 | number | formal | 100.0% | 0.0% | What was Continental's EBIT in 2025? | Continental’s EBIT in 2025 was **€272 million**. The report states: “EBIT was down by €1,771 million year-on-year in 202 | The provided excerpts do not contain Continental's EBIT for the year 2025. The closest related figures are EBIT and Adju |
| CO-N05 | number | casual | 100.0% | 0.0% | how much free cash flow did continental generate from continuing ops in 2025? | Continental generated **€967 million** of free cash flow from **continuing operations** in 2025. The cash flow statement | The report excerpts do not provide the exact free cash flow figure for Continental's continuing operations in 2025. The  |
| CO-N12 | number | typo | 100.0% | 0.0% | What was the adjusted EBIT margin of Continental's Tires gorup seector in 2025? | Continental’s **Tires group sector** had an **adjusted EBIT margin of 13.6%** in 2025. / Company / 2025 adjusted EBIT ma | The provided excerpts do not contain the specific adjusted EBIT margin for Continental's Tires group sector in 2025. The |
| GY-N05 | number | typo | 100.0% | 0.0% | How much net cash did Goodyear's operating activiies proide in 2025? | Goodyear’s operating activities provided **$796 million** of net cash in 2025. | I couldn't verify an answer to this in the reports, so I'm not showing one. |
| GY-N13 | number | terse | 100.0% | 0.0% | goodyear total assets end 2025 | Goodyear’s total assets at the end of 2025 were **$18,208 million**. The consolidated balance sheet lists **“Total Asset | The provided excerpts do not contain the specific figure for Goodyear's total assets at the end of 2025. The closest rel |
| GY-N15 | number | formal | 100.0% | 0.0% | What was Goodyear's worldwide tire capacity utilization rate in 2025? | Goodyear's worldwide tire capacity utilization rate was **approximately 83% during 2025**. The report says: “Our worldwi | I couldn't verify an answer to this in the reports, so I'm not showing one. |
| GY-N16 | number | typo | 100.0% | 0.0% | How large was the gopdwill impairment charge Goodyear recorded in its Americas segmnt in 2025? | Goodyear recorded a **$674 million** goodwill impairment charge in its Americas segment in 2025. The report says it was  | The provided excerpts do not contain the specific amount of the goodwill impairment charge recorded by Goodyear in its A |
| GY-N18 | number | casual | 100.0% | 0.0% | how much did goodyear get for selling off its polymer chemicals business? | Goodyear said it completed the sale of its polymer chemicals business for **$650 million** and, at closing, **received g | The report excerpts do not provide the specific amount Goodyear received for selling its polymer chemicals business. The |
| MI-N02 | number | casual | 100.0% | 0.0% | what was michelin's operating income in 2025? | Michelin’s **operating income in 2025** was **€2,366 million**. The consolidated income statement lists **“Operating inc | The operating income for Michelin in 2025 is not directly stated in the excerpts provided. The closest relevant informat |
| MI-N03 | number | terse | 100.0% | 0.0% | michelin basic EPS 2025 | Michelin’s **basic earnings per share (2025)** was **€2.36**. The report states: “**EARNINGS PER SHARE (in €) n Basic 2. | The excerpts provided do not contain information about the basic EPS for Michelin in 2025. Basic EPS for 2024 is found i |
| MI-N11 | number | typo | 100.0% | 0.0% | What was Michelin's gearng at the end of 2025? | Michelin’s gearing at December 31, 2025 was **0.13** in the consolidated table, which the report also describes as **13. | The provided excerpts do not contain information about Michelin's gearing at the end of 2025. Gearing ratios typically i |
| MI-N14 | number | typo | 100.0% | 0.0% | What was Michelin's fdee cash flow befroe M&A in 2025? | Michelin’s **free cash flow before M&A** in **2025** was **€2,126 million**. The excerpt states: “**FREE CASH FLOW BEFOR | The provided excerpts do not contain the specific figure for Michelin's free cash flow before M&A in 2025. The closest m |
| BS-T02 | text | typo | 100.0% | 0.0% | Who foundded Bridgestone? | Bridgestone was founded by **Shojiro Ishibashi**. The report says, **“Founder Shojiro Ishibashi”** and notes that on Mar | I can only answer questions about the four companies' 2025 annual reports. |
| BS-T03 | text | casual | 100.0% | 0.0% | when and where did bridgestone get started? | Bridgestone got started on **March 1, 1931**, when **“Bridgestone Tire Co., Ltd.” was founded in Kurume City, Fukuoka Pr | The provided excerpts do not contain specific details about when and where Bridgestone got started. While the reports me |
| BS-T12 | text | formal | 100.0% | 0.0% | What is BCMA at Bridgestone? | BCMA at Bridgestone stands for **Bridgestone Commonality Modularity Architecture**. It is described as Bridgestone’s **b | The provided excerpts do not contain any information about BCMA at Bridgestone. BCMA could refer to Business Control Man |
| BS-T14 | text | terse | 100.0% | 0.0% | bridgestone ENLITEN tire launched india 2024 | Yes. Bridgestone says it launched **TURANZA 6i** in India in **2024**, described as “a version of the TURANZA6, previous | The provided excerpts do not contain any specific information about Bridgestone launching the ENLITEN tire in India in 2 |
| CO-T02 | text | typo | 100.0% | 0.0% | Who is repsonsible for human reations on Continental's Executive Board? | Ulrike Hintze is responsible for Human Relations on Continental’s Executive Board. The report says she was “appointed as | The report excerpts do not contain specific information on who is responsible for human resources on Continental's Execu |
| CO-T11 | text | terse | 100.0% | 0.0% | continental why leverage ratio instead of gearing | Continental says it replaced the gearing ratio with the leverage ratio because the leverage ratio **“reflects the relati | The provided excerpts do not explicitly state why Continental chose to use the leverage ratio instead of the gearing rat |
| CO-T14 | text | casual | 100.0% | 0.0% | who's continental's controlling shareholder? | Continental’s controlling shareholder is the **IHO Group**, headquartered in Herzogenaurach, Germany. The report states  | I can only answer questions about the four companies' 2025 annual reports. |
| CO-T16 | text | formal | 100.0% | 0.0% | What share of Continental's 2025 sales related to the automotive industry, excluding the replacement business? | Continental says that in 2025, the **automotive industry excluding the replacement business** accounted for **29% of sal | The report excerpts do not provide the specific share of Continental's 2025 sales that related to the automotive industr |
| GY-T06 | text | typo | 100.0% | 0.0% | What are Goodyear's opertaing segemnts? | Goodyear operated through three operating segments in 2025: / Operating segment / Citation / /---/---/ / Americas / [Goo | LengthFinishReasonError: Could not parse response content as the length limit was reached - CompletionUsage(completion_t |
| GY-T08 | text | terse | 100.0% | 0.0% | goodyear polymer chemicals business buyer | The buyer of Goodyear’s polymer chemicals business was **G-3 Chickadee Purchaser, LLC**. The report says the sale was co | The provided excerpts do not contain any information about a Goodyear polymer chemicals business buyer. The excerpts men |
| GY-T09 | text | casual | 100.0% | 0.0% | what's goodyear's plan for a fully sustainable-material tire? | Goodyear’s plan is to introduce the industry’s first **100% sustainable material tire by 2030**. It defines “sustainable | The provided excerpts do not contain specific details about Goodyear's plan for a fully sustainable-material tire. The e |
| GY-T11 | text | formal | 100.0% | 0.0% | Which businesses did Goodyear sell in 2025? | Goodyear says it sold, in 2025, the following businesses/assets: / Sold in 2025 / Support / /---/---/ / OTR tire busines | I can only answer questions about the four companies' 2025 annual reports. |
| MI-T10 | text | formal | 100.0% | 0.0% | When is Michelin's 2026 Annual Shareholders Meeting? | Michelin's 2026 Annual Shareholders Meeting is on **May 22, 2026**. | I couldn't verify an answer to this in the reports, so I'm not showing one. |
| MI-T13 | text | typo | 100.0% | 0.0% | Why did Michelin's coost of net debt incraese in 2025? | Michelin says the increase in cost of net debt in 2025 was mainly due to two factors: higher interest expense and lower  | The provided excerpts do not contain a detailed explanation for why Michelin's cost of net debt increased in 2025. The e |
| MI-T15 | text | terse | 100.0% | 0.0% | michelin organization structure business lines regions | Michelin describes a customer-centric organization built around: / Element / Description / /---/---/ / Business Lines /  | The excerpts provided do not contain detailed information about Michelin's entire organization structure, business lines |
