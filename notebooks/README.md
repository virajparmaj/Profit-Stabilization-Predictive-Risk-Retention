# Historical analysis notebooks

These notebooks preserve the original exploratory methods. Their historical low-risk terminology and modeling choices are not validated prospective or financial claims. Use the [research pipeline](../analysis/research_pipeline/README.md) for the corrected source-built study.

Run notebooks with `notebooks/` as the kernel working directory. Obtain the public HC-251 CSV and place it at `data_raw/h251.csv` relative to the repository root. Run `eda_pre-processing.ipynb` first to create the ignored `data_processed/meps_model_ready_2023.csv`, then use that table in the modeling and visualization notebooks. Dependencies for the corrected pipeline are pinned separately; historical notebook package compatibility is not guaranteed by that lock.

Commit notebook source with outputs and execution counts cleared. Data extracts, models, report figures and executed notebook copies stay local. The site has a separate data builder and input schema; see the repository README.
