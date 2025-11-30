# Profit-Stabilization-Predictive-Risk-Retention

## Research Question
**Can low-risk health-care members be reliably identified using a reduced, behavior-oriented feature set, and what is the minimum predictive structure needed to stabilize cost-risk segmentation under uncertainty?**

This repository contains the complete workflow for analyzing MEPS (Medical Expenditure Panel Survey) data to build a **minimal-feature, behavior-driven risk segmentation model**. The goal is to identify **stable low-risk members** whose health-care cost profile remains predictably low, enabling **profit stabilization**, **risk retention**, and **actuarially sound pricing design**.

---

## Objective
1. Build a **reduced feature set** focused on lifestyle, behavior, clinical burden, and utilization.
2. Determine the **minimum predictive structure** capable of reliably identifying low-risk health-care members.
3. Characterize low-risk individuals in terms of:
   - Health behaviors  
   - Chronic condition burden  
   - Functional limitations  
   - Utilization patterns  
   - Annual expenditures and catastrophic-risk avoidance
4. Provide a foundation for future **multi-year volatility modeling** and **risk-retention strategies**.

---

## Data Source
**Medical Expenditure Panel Survey (MEPS) – Household Component**  
Unit of analysis: **Adult person-year**  
Analysis type: Empirical, ML-based segmentation and predictive modeling.

---

## Feature Framework (Reduced + High-Signal Set)

### 1. **Demographics**
- `AGELAST`, `SEX`
- `RACETHX`, `HISPANX`
- `EDUCYR` or `HIDEG`
- `MARRY53X`

### 2. **Socioeconomic**
- `FAMINCxx`
- `POVCATxx`
- `TTLPxxX`
- Employment status (`EMPST53` or `EMPST22`)

### 3. **Insurance Coverage**
- `INSURCxx`
- `PRVEVxx`, `MCREVxx`, `MCDEVxx`
- `UNINSxx`

### 4. **Clinical Burden (Major Chronic Conditions)**
- Hypertension (`HIBPDX`)
- Diabetes (`DIABDX`)
- CHD / MI / Stroke (`CHDDX`, `MIDX`, `STROKDX`)
- COPD / Emphysema (`EMPHDX`)
- High cholesterol (`CHOLDX`)
- Arthritis, Asthma (`ARTHDX`, `ASTHDX`)
- Cancer indicators (`CANCERDX`)
- Mental illness flags (`ANYLMI22`)
- COVID diagnosis (`COVIDEVER53`)

### 5. **Self-Rated Health & Mental Health**
- Physical health: `RTHLTH53`
- Mental health: `MNHLTH53`
- Psychological distress: `K6SUM42`
- Depression screening: `PHQ242`

### 6. **Functioning & Limitations**
- ADL help: `ADLHLP31`
- IADL help: `IADLHP31`
- Mobility / cognitive / work limitations (`WLKLIM`, `COGLIM`, `WRKLIM`, `SOCLIM`)

### 7. **Behavioral & Lifestyle Indicators** *(Core Reduced Feature Block)*
- BMI (`ADBMI42`)
- Exercise frequency (`PHYEXE53`)
- Smoking (`OFTSMK53` or `NOSMOK42`)
- Healthy eating indicator (`EATHLT42`)
- Alcohol use (`ADOFTALC42` or `ADRNK542_M20`)

### 8. **Utilization Indicators**
- Office visits: `OBTOTVxx`
- Outpatient visits: `OPTOTVxx`
- ER visits: `ERTOTxx`
- Inpatient discharges: `IPDISxx`
- Prescription fills: `RXTOTxx`

### 9. **Expenditure Targets**
- Total annual spending: `TOTEXPxx` (Primary)
- Optional: `TOTSLFxx`, `TOTPRVxx`, `TOTMCRxx`, `TOTMCDxx`, `RXEXPxx`

---

## Approach

### **Step 1: Data Preparation**
- Import MEPS consolidated person-level file.
- Select core reduced-feature parameter blocks.
- Clean, standardize, and encode variables.
- Generate candidate labels:
  - **Low-Risk Prototype** (low expenditure, low acute care, minimal chronic burden)
  - Catastrophic-risk flags (e.g., spending > $20k)

### **Step 2: Exploratory Analysis**
- Distribution summaries for all parameter blocks.
- Correlations between behaviors, clinical factors, utilization, and total cost.
- Compare **low-risk vs non-low-risk** along:
  - Health behaviors
  - Chronic disease load
  - Functioning & limitations
  - Utilization intensity

### **Step 3: Minimal Predictive Structure Identification**
Models tested:
- Logistic regression (baseline)
- Gradient Boosted Trees (XGBoost/LightGBM)
- Random Forest
- Regularized GLMs (L1/L2)
- Small NN for feature-compressive tests

We evaluate:
- How accurately low-risk members can be predicted
- Which *smallest subset* of variables gives stable performance
- Whether behaviors alone can define a reliable low-risk segment
- Feature importance rankings and interaction structure

### **Step 4: Stability & Uncertainty Testing**
- Bootstrap uncertainty quantification  
- Sensitivity to feature removal  
- Model collapse checks under reduced structures  
- Measure variance of predictions across random seeds

### **Step 5: Interpretation**
Outputs include:
- Predictive accuracy of minimal feature models
- Identification of the “core behavioral signal”  
- Mapping of clinical and utilization add-on value  
- Characterization of low-risk profiles  
- Actuarial implications for pricing, segmentation, and retention  
