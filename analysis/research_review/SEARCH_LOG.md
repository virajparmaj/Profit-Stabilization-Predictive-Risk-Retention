# Literature search log

**Date:** 2026-09-25. **Purpose:** identify prior art and promising minimum extensions for the supplied MEPS 2023 project. This is a targeted scoping search, not a systematic review. No exact-match absence claim is justified by this search alone.

## Sources and access

| Source requested | What was done | Limitation |
|---|---|---|
| arXiv | Topic searches plus direct abstract/full-text inspection for MEPS label bias, predictive stability, semicontinuous diagnostics and 2026 related preprints | Preprints distinguished from journal publications; no exhaustive full-corpus search |
| Google Scholar | Domain-specific searches; followed an arXiv Scholar link; attempted direct query `MEPS low cost risk segmentation stability` | Direct search/link access failed; no claim to have screened Scholar results comprehensively |
| Semantic Scholar | Domain-specific title/topic searches, indexed PDF results, arXiv bibliographic link, direct search page | Direct API/link/search interface access failed; index coverage is incomplete |
| Conference proceedings | PMLR AISTATS/ICML primary proceedings and ACM Digital Health official program | ACM paper full text inaccessible; recorded as a lead rather than a fully reviewed paper |
| Journals | Primary journal pages, PubMed abstracts, PMC indexed full text, author-hosted manuscripts where needed | Some PMC direct opens returned bot checks; readable indexed primary text was used where available |
| Benchmark / dataset documentation | AHRQ spending-concentration brief and HC-251 official technical documentation; local downloaded codebook/doc checked against raw variables | No new multi-year dataset was downloaded or analyzed |

## Query families used

- `MEPS machine learning low expenditure risk segmentation health costs stability tail risk prediction`
- `healthcare cost prediction low risk algorithm label bias uninsured spending Obermeyer 2019`
- `"MEPS" "low" "risk" "machine learning" expenditure`
- `"MEPS" "cost prediction" "2024" "2025"`
- `site.arxiv.org MEPS healthcare expenditure prediction stability`
- `"Risk Scores, Label Bias"`
- `site.scholar.google.com "MEPS" "healthcare" "prediction"`
- `site.semanticscholar.org "MEPS" "cost" prediction`
- `site.proceedings.mlr.press "Medical Expenditure Panel Survey"`
- `"prediction instability" "risk" Riley 2023 bootstrap`
- `"health care" "risk selection" "coefficient of variation"`
- `"low risk" "healthcare costs" "tail" prediction`
- `"healthcare" "risk pooling" "variance" selection prediction`
- `"MEPS" "low expenditure" prediction`
- Exact-title follow-up searches for clinical-condition prediction, residual-spending heteroscedasticity, high-risk pooling, MEPS cost prediction and OOP factor selection.

The search followed citations backward to foundational work and inspected recent 2024–2026 papers to check whether attractive extensions were already occupied. Unrelated expansions of “MEPS,” generic websites, social media and secondary summaries were not used as technical evidence. Publication year came from primary pages rather than crawler timestamps.

## Primary reading list

The main advisory contains the actual overlap/gap assessment, methods, data and results for each important source.

1. Riley & Collins, Biometrical Journal 2023. [arXiv and journal link](https://arxiv.org/abs/2211.01061). Read abstract, journal-indexed methods and results descriptions.
2. Zanger-Tishler, Nyarko & Goel, Science Advances 2024. [Full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC10980258/). Read indexed primary full text, especially healthcare simple/rich feature comparison. [Preprint](https://arxiv.org/abs/2305.12638).
3. Oskam, van Kleef & Douven, online 2023, EJHE 2024 issue. [Publisher](https://doi.org/10.1007/s10198-023-01592-9). Read primary abstract/method/result descriptions.
4. Singh & Ramamurthy, arXiv 2019. [Full text](https://arxiv.org/html/1911.01509v1). Read methods and tables on Panels 19/20, logistic prediction and mitigation.
5. Obermeyer et al., Science 2019. [Publisher](https://doi.org/10.1126/science.aax2342). Read primary abstract/indexed text; data/code release identified by the source.
6. Fleishman & Cohen, Health Services Research 2010. [Primary full-text index](https://pmc.ncbi.nlm.nih.gov/articles/PMC2838159/). Read primary methods and reported findings; direct PMC opening was intermittently blocked.
7. Hernandez-Viver & Mitchell, AHRQ 2025. [Statistical Brief 560](https://www.meps.ahrq.gov/data_files/publications/st560/stat560.shtml). Read tables and population definitions.
8. Zhang, Ding & Peng, Health Information Science and Systems 2021. [Primary text](https://pmc.ncbi.nlm.nih.gov/articles/PMC8184979/), [PubMed](https://pubmed.ncbi.nlm.nih.gov/34123374/). Read methods/outcome and reported performance.
9. Gao & Chan, Frontiers in Health Services 2026. [Publisher full text](https://www.frontiersin.org/journals/health-services/articles/10.3389/frhs.2026.1742807/full). Read methods/results; release year of illustrative MEPS data not clearly specified in inspected methods.
10. Kresin et al., arXiv 2026. [Full text](https://arxiv.org/html/2607.15446v1). Read outcome, models, performance table and temporal-testing description.
11. Yang, arXiv/Biometrics 2024. [Abstract and publication link](https://arxiv.org/abs/2401.06347). Abstract-level review; no invented numerical performance claim.
12. Wang et al., AISTATS 2023. [Proceedings](https://proceedings.mlr.press/v206/wang23n.html). Read primary abstract and indexed PDF dataset section; not treated as a `TOTEXP23`-matched benchmark.
13. Zaffran et al., ICML 2023. [Proceedings](https://proceedings.mlr.press/v202/zaffran23a.html). Abstract/theory-scope review; its mention of MEPS in references does not establish a MEPS application.
14. Oskam, van Kleef & van Vliet, Journal of Risk and Insurance 2025 issue. [Publisher full text](https://onlinelibrary.wiley.com/doi/full/10.1111/jori.12500). Read abstract/method context and principal reported results; online date November 2024.
15. Matijevic & Yau, arXiv 2026. [Abstract](https://arxiv.org/abs/2602.11360). Abstract-level review of datasets and reported instability measures.
16. Sushmita et al., ACM Digital Health 2015. [Official program](https://wp.cs.ucl.ac.uk/acm-digitalhealth-2015/detailed-programme/), [author list](https://faculty.washington.edu/ankurt/publications.html). Bibliographic lead; primary paper not accessed. DOI 10.1145/2750511.2750521.
17. AHRQ, HC-251 2023 consolidated file documentation, released August 2025. [Technical documentation](https://meps.ahrq.gov/data_stats/download_data/pufs/h251/h251doc.shtml). Read coding, limitations, instrument eligibility, survey weights and variance estimation guidance, alongside the local copy.

## Remaining search work before submission

Use working Scholar/Semantic Scholar interfaces for forward citations to R1–R4 and the 2015 ACM paper; inspect the full texts of abstract-only adjacent papers if the final claim overlaps them. Search the final exact hypothesis again after results determine the paper's scope. Save screened references, exclusion reasons and versions in a bibliography. A study that changes its claim after the next experiments may have a different closest competitor.
