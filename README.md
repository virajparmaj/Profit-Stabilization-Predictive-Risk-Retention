# Profit-Stabilization-Predictive-Risk-Retention

## Research Question

**Can low-risk health-care members be reliably identified using a reduced, behavior-oriented feature set, and what is the minimum predictive structure needed to stabilize cost-risk segmentation under uncertainty?**

This repository contains a **complete, research-to-deployment pipeline** built on MEPS (Medical Expenditure Panel Survey) data to study **low-risk member identification**, **segmentation stability**, and **uncertainty-aware pricing insights**.

The project combines:

* rigorous statistical / ML experimentation,
* a deployable production model,
* and an interactive analytics web platform that operationalizes the research findings.

---

## What This Repository Does (End-to-End)

### 1. **Data → Model Pipeline (Fully Implemented)**

* Accepts **processed MEPS person-year CSVs** (e.g., HC-251 2023).
* Enforces **strict leakage control** (label-defining cost variables excluded from predictors).
* Constructs cumulative feature blocks (B0 → B5) to identify the **minimum predictive structure**.
* Trains and evaluates multiple model families (Logistic, RF, XGBoost).
* Selects a **deployable production model** based on:

  * discrimination,
  * calibration,
  * and bootstrap stability.

> Final deployed model: **XGBoost, B3_chronic block**
> (behavior + mental health + functional status + chronic burden)

---

### 2. **Model Ladder & Stability Evidence (Fully Implemented)**

Instead of a single opaque model, the project builds a **model ladder**:

| Block  | Description               | Purpose                  |
| ------ | ------------------------- | ------------------------ |
| B0     | Behavior only             | Baseline signal          |
| B1     | + Mental health           | Early improvement        |
| B2     | + Functional limits       | Structural stability     |
| **B3** | **+ Chronic burden**      | **Minimum stable model** |
| B4     | + SES & insurance         | Incremental gain         |
| B5     | + Utilization (non-label) | Upper-bound benchmark    |

Each block is evaluated for:

* AUC / Brier score,
* calibration,
* **bootstrap variance of low-risk segment size**.

This directly answers the research question:
**B3 is the minimum predictive structure that stabilizes segmentation under uncertainty.**

---

### 3. **Production Inference API (Implemented)**

* The selected model pipeline (preprocessing + encoding + classifier) is serialized (`.joblib`).
* A FastAPI service exposes:

  * batch scoring,
  * single-member scoring,
  * schema validation via a model card.
* The API rejects inputs with missing required features (as shown in production UI).

No retraining is required at inference time.

---

### 4. **Interactive Analytics Web Platform (Implemented)**

A deployed web application operationalizes the research:

**Core capabilities**

* Upload and validate MEPS-derived datasets (2023 supported).
* Run **live backend inference** using the production model.
* Explore **member-level risk scores** and **population-level segmentation**.
* Visualize:

  * clustering structure (t-SNE),
  * low-risk profiles,
  * behavioral and chronic burden signatures.
* Quantify **uncertainty and stability** via bootstrap simulation.
* Run **fairness and compliance diagnostics**.
* Generate **research-ready reports** (PDF + CSV exports).

The UI reflects insurer-style analytics rather than a toy demo.

---

## What Is Dynamic vs Static Right Now

### ✅ Fully Dynamic

* CSV ingestion for MEPS-aligned, model-ready files.
* Backend model scoring (real predictions).
* Segmentation, clustering, and summaries.
* Bootstrap stability metrics.
* Fairness metrics computed from scored data.
* Report generation using live results.

### ⚠️ Partially Static / Placeholder

* Some UI explanations (text blocks) are descriptive rather than computed.
* Certain visual labels (e.g., segment names) are rule-based, not learned.
* Model selection UI is locked to the production model (by design).
* Multi-year (panel-to-panel) temporal validation is not yet automated in the UI.

These are **deliberate design choices**, not architectural gaps.

---

## Validity Across MEPS Years

The pipeline is **year-agnostic by construction**, provided that:

* the input file is a **single MEPS person-year**,
* variables are harmonized to the expected schema,
* labels are recomputed per year.

This allows:

* retraining on new years (e.g., 2024, 2025),
* cross-year stability testing,
* future panel-based volatility modeling.

---

## Why This Is Not Just a Dashboard

This project is not a visualization layer on top of a model.

It is:

* a **research artifact**,
* a **deployable inference system**,
* and an **auditable analytics product**.

Every chart corresponds to a model, statistic, or bootstrap procedure implemented in code and validated empirically.

---

## Future Extensions (Planned)

* Temporal validation across MEPS panels.
* SHAP-based explainability comparisons (B3 vs B5).
* Fairness audits under alternative SES definitions.
* Policy simulation (retention / pricing stress tests).
* Automated ingestion of raw MEPS releases.
* Multi-model comparison UI (unlock B4/B5 for research mode).
