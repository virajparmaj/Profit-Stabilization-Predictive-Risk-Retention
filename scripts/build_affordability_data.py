from __future__ import annotations

import csv
import json
from bisect import bisect_right
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data_raw" / "h251.csv"
LOW_RISK_PATH = ROOT / "data_processed" / "meps_model_ready_2023_low_risk_business_proxies_v2.csv"
OUT_DIR = ROOT / "site" / "public" / "data"
PEOPLE_OUT = OUT_DIR / "people.csv"
METADATA_OUT = OUT_DIR / "metadata.json"
EXPECTED_ROWS = 18_919

VARIABLE_SHORT_LABELS = {
    "PERWT23F": "Person weight",
    "AFRDCA42": "Afford medical",
    "AFRDDN42": "Afford dental",
    "AFRDPM42": "Afford meds",
    "DLAYCA42": "Delay medical",
    "DLAYDN42": "Delay dental",
    "DLAYPM42": "Delay meds",
    "HAVEUS42": "Usual care",
    "YNOUSC42_M18": "No-USC reason",
    "TOTEXP23": "Total spend",
    "TOTSLF23": "Out-of-pocket",
    "TOTPRV23": "Private spend",
    "TOTMCR23": "Medicare spend",
    "TOTMCD23": "Medicaid spend",
    "INSCOV23": "Insurance",
    "UNINS23": "Uninsured",
    "POVCAT23": "Poverty",
    "FAMINC23": "Family income",
    "EDUCYR": "Education years",
    "EMPST53": "Employment",
    "REGION23": "Region",
    "RACETHX": "Race group",
    "OBTOTV23": "Office visits",
    "ERTOT23": "ER visits",
    "IPDIS23": "Inpatient",
    "RXTOT23": "Prescriptions",
    "FTSTU23X": "Student status",
    "LOW_RISK": "Low risk",
    "LOW_SPEND": "Low spend",
    "CATA_10K": "Catastrophic 10k",
    "CATA_20K": "Catastrophic 20k",
    "CHRONIC_CT": "Chronic count",
    "LIMIT_CT": "Limitation count",
    "CHRONIC_BURDEN_BIN": "Chronic burden",
    "LIMIT_BURDEN_BIN": "Limitation burden",
    "NONACUTE_UTIL_CT": "Non-acute count",
    "NONACUTE_UTIL_BAND": "Non-acute band",
    "ACUTE_UTIL_ANY": "Acute any",
    "SPEND_BAND_2023": "Spend band",
    "family_income_quintile": "Income quintile",
    "family_income_quintile_label": "Income quintile",
    "education_band": "Education band",
    "education_band_label": "Education band",
    "employment_band": "Employment",
    "employment_band_label": "Employment",
    "racethx_label": "Race group",
    "age_band": "Age band",
    "age_focus_17_23": "Age 17-23",
    "student_group": "Student group",
    "student_group_label": "Student group",
    "afford_any": "Afford barrier",
    "delay_any": "Cost delay",
    "can_afford_all": "No barrier",
    "cost_reason_no_usc": "Cost reason",
    "oop_share": "OOP share",
    "low_risk": "Low risk",
}

RAW_FIELDS = [
    "DUPERSID",
    "PERWT23F",
    "AGELAST",
    "AFRDCA42",
    "AFRDDN42",
    "AFRDPM42",
    "DLAYCA42",
    "DLAYDN42",
    "DLAYPM42",
    "HAVEUS42",
    "YNOUSC42_M18",
    "TOTEXP23",
    "TOTSLF23",
    "TOTPRV23",
    "TOTMCR23",
    "TOTMCD23",
    "INSCOV23",
    "UNINS23",
    "POVCAT23",
    "FAMINC23",
    "EDUCYR",
    "EMPST53",
    "REGION23",
    "RACETHX",
    "OBTOTV23",
    "ERTOT23",
    "IPDIS23",
    "RXTOT23",
    "FTSTU23X",
]

LOW_RISK_FIELDS = [
    "LOW_RISK",
    "LOW_SPEND",
    "CATA_10K",
    "CATA_20K",
    "CHRONIC_CT",
    "LIMIT_CT",
    "CHRONIC_BURDEN_BIN",
    "LIMIT_BURDEN_BIN",
    "NONACUTE_UTIL_CT",
    "NONACUTE_UTIL_BAND",
    "ACUTE_UTIL_ANY",
    "SPEND_BAND_2023",
]

OUTPUT_FIELDS = [
    "dupersid",
    "perwt23f",
    "agelast",
    "age_band",
    "age_focus_17_23",
    "afrdca42",
    "afrdca42_label",
    "afrddn42",
    "afrddn42_label",
    "afrdpm42",
    "afrdpm42_label",
    "dlayca42",
    "dlayca42_label",
    "dlaydn42",
    "dlaydn42_label",
    "dlaypm42",
    "dlaypm42_label",
    "afford_any",
    "afford_any_label",
    "delay_any",
    "delay_any_label",
    "can_afford_all",
    "can_afford_all_label",
    "haveus42",
    "haveus42_label",
    "ynousc42_m18",
    "ynousc42_m18_label",
    "cost_reason_no_usc",
    "cost_reason_no_usc_label",
    "totexp23",
    "totslf23",
    "totprv23",
    "totmcr23",
    "totmcd23",
    "oop_share",
    "inscov23",
    "inscov23_label",
    "unins23",
    "unins23_label",
    "povcat23",
    "povcat23_label",
    "faminc23",
    "family_income_quintile",
    "family_income_quintile_label",
    "educyr",
    "education_band",
    "education_band_label",
    "empst53",
    "employment_band",
    "employment_band_label",
    "region23",
    "region23_label",
    "racethx",
    "racethx_label",
    "obtotv23",
    "ertot23",
    "ipdis23",
    "rxtot23",
    "ftstu23x",
    "ftstu23x_label",
    "student_group",
    "student_group_label",
    "low_risk",
    "low_risk_label",
    "low_spend",
    "cata_10k",
    "cata_20k",
    "chronic_ct",
    "limit_ct",
    "chronic_burden_bin",
    "limit_burden_bin",
    "nonacute_util_ct",
    "nonacute_util_band",
    "acute_util_any",
    "spend_band_2023",
]

FIELD_LABELS = {
    "AFRDCA42": {
        "1": "Yes",
        "2": "No",
        "-1": "Inapplicable",
        "-7": "Refused",
        "-8": "Don't know",
    },
    "AFRDDN42": {
        "1": "Yes",
        "2": "No",
        "-1": "Inapplicable",
        "-7": "Refused",
        "-8": "Don't know",
    },
    "AFRDPM42": {
        "1": "Yes",
        "2": "No",
        "-1": "Inapplicable",
        "-7": "Refused",
        "-8": "Don't know",
    },
    "DLAYCA42": {
        "1": "Yes",
        "2": "No",
        "-1": "Inapplicable",
        "-7": "Refused",
        "-8": "Don't know",
    },
    "DLAYDN42": {
        "1": "Yes",
        "2": "No",
        "-1": "Inapplicable",
        "-7": "Refused",
        "-8": "Don't know",
    },
    "DLAYPM42": {
        "1": "Yes",
        "2": "No",
        "-1": "Inapplicable",
        "-7": "Refused",
        "-8": "Don't know",
    },
    "HAVEUS42": {
        "1": "Yes",
        "2": "No",
        "-1": "Inapplicable",
        "-7": "Refused",
        "-8": "Don't know",
        "-15": "Cannot be computed",
    },
    "YNOUSC42_M18": {
        "1": "Seldom or never sick",
        "2": "Recently moved to area",
        "3": "Just changed insurance plans",
        "4": "No health insurance, other insurance-related issue",
        "5": "Don't know where to go for care",
        "6": "Usual source of care in this area no longer available",
        "7": "Likes to go to different places for different health needs",
        "8": "Don't use doctors / treat self",
        "9": "Cost of medical care",
        "10": "No health insurance",
        "91": "Other reason",
        "-1": "Inapplicable",
        "-7": "Refused",
        "-8": "Don't know",
    },
    "INSCOV23": {
        "1": "Any private",
        "2": "Public only",
        "3": "Uninsured",
    },
    "UNINS23": {
        "1": "Uninsured all of 2023",
        "2": "Insured for all or part of 2023",
    },
    "POVCAT23": {
        "1": "Negative or poor (<100%)",
        "2": "Near poor (100% to <125%)",
        "3": "Low income (125% to <200%)",
        "4": "Middle income (200% to <400%)",
        "5": "High income (400%+)",
    },
    "REGION23": {
        "1": "Northeast",
        "2": "Midwest",
        "3": "South",
        "4": "West",
        "-1": "Inapplicable",
    },
    "RACETHX": {
        "1": "Hispanic",
        "2": "White",
        "3": "Black",
        "4": "Asian",
        "5": "Other / multi-race",
    },
    "FTSTU23X": {
        "1": "Full-time student",
        "2": "Part-time student",
        "3": "Not a student",
        "-1": "Not ages 17-23",
        "-7": "Refused",
        "-8": "Don't know",
    },
    "EMPST53": {
        "1": "Employed at interview date",
        "2": "Has a job to return to",
        "3": "Unemployed",
        "4": "Not employed during round",
        "-1": "Inapplicable",
        "-7": "Refused",
        "-8": "Don't know",
        "-15": "Cannot be computed",
    },
    "AFFORD_ANY": {
        "1": "Could not afford at least one type of care",
        "0": "No reported affordability problem across the three flags",
    },
    "DELAY_ANY": {
        "1": "Delayed at least one type of care due to cost",
        "0": "No reported delay across the three cost flags",
    },
    "CAN_AFFORD_ALL": {
        "1": "Reported no affordability problem across all three care types",
        "0": "Reported at least one affordability problem",
    },
    "COST_REASON_NO_USC": {
        "1": "Cost of medical care",
        "0": "Another or unknown reason",
    },
    "FAMILY_INCOME_QUINTILE": {
        "1": "Q1 lowest income",
        "2": "Q2 lower-middle income",
        "3": "Q3 middle income",
        "4": "Q4 upper-middle income",
        "5": "Q5 highest income",
    },
    "EDUCATION_BAND": {
        "Less than high school": "Less than high school",
        "High school": "High school or GED",
        "Some college": "Some college / associate",
        "Bachelor": "Bachelor's degree",
        "Graduate": "Graduate or professional degree",
    },
    "STUDENT_GROUP": {
        "Full-time student": "Full-time student",
        "Part-time student": "Part-time student",
        "Not a student": "Not a student",
    },
    "EMPLOYMENT_BAND": {
        "Employed at interview date": "Employed at interview date",
        "Has a job to return to": "Has a job to return to",
        "Unemployed": "Unemployed",
        "Not employed during round": "Not employed during round",
    },
    "LOW_RISK": {
        "1": "Low risk",
        "0": "Not low risk",
    },
}

SPECIAL_VALUES = {
    "-1": "Inapplicable / out of universe for that survey item",
    "-7": "Refused",
    "-8": "Don't know",
    "-15": "Cannot be computed",
}

SECTION_METADATA = [
    {
        "id": "overview",
        "title": "Overview",
        "description": "Landing summary for the affordability, delay, access, and low-risk story, with income, education, and broad race comparisons surfaced up front.",
    },
    {
        "id": "affordability",
        "title": "Could Not Afford Care",
        "description": "Direct affordability barriers paired with spending, insurance, income, education, and broad race context.",
    },
    {
        "id": "delay",
        "title": "Delayed Due To Cost",
        "description": "Cost-driven postponement of care, downstream burden patterns, and subgroup differences across the same fairness lenses.",
    },
    {
        "id": "no_usc",
        "title": "Proxy Why They Didn't Buy",
        "description": "Proxy-only section using usual source of care and the reason for not having one, clearly separated from direct affordability measures.",
    },
    {
        "id": "can_afford",
        "title": "Can Afford Cohort",
        "description": "Requested comparisons inside the cohort reporting no affordability barriers, with income and education framed as descriptive gradients rather than causal drivers.",
    },
    {
        "id": "low_risk",
        "title": "Low-Risk Subsidy Story",
        "description": "Acquisition, payer-mix, subgroup equity checks, and scenario sizing using the existing low-risk cohort.",
    },
    {
        "id": "student",
        "title": "Student Lens",
        "description": "Ages 17-23 filtered by student status, spending, delay, and low-risk signals.",
    },
]

QUESTION_METADATA = [
    {
        "id": "afford-any",
        "section": "affordability",
        "title": "What share could not afford at least one type of care?",
        "chartKind": "donut",
        "variables": ["AFRDCA42", "AFRDDN42", "AFRDPM42", "PERWT23F"],
        "howToRead": "The donut partitions valid respondents into two groups: those with at least one affordability barrier and those with none across the three care types.",
        "featured": True,
    },
    {
        "id": "afford-total-spend",
        "section": "affordability",
        "title": "Among people who could not afford care, what is annual total spend distribution?",
        "chartKind": "histogram",
        "variables": ["TOTEXP23", "AFRDCA42", "AFRDDN42", "AFRDPM42", "PERWT23F"],
        "howToRead": "Bars show the weighted distribution of annual total spending for the could-not-afford cohort. The median and upper tail reveal how concentrated spending is inside this group.",
        "featured": True,
    },
    {
        "id": "afford-oop-spend",
        "section": "affordability",
        "title": "Among people who could not afford care, what is annual out-of-pocket distribution?",
        "chartKind": "histogram",
        "variables": ["TOTSLF23", "AFRDCA42", "AFRDDN42", "AFRDPM42", "PERWT23F"],
        "howToRead": "This histogram isolates annual out-of-pocket spending for the could-not-afford cohort, so high bars in the upper ranges indicate heavier direct financial burden.",
        "featured": True,
    },
    {
        "id": "afford-sicker-or-skipping",
        "section": "affordability",
        "title": "Are “could not afford” people spending less because they skip care, or more because they are sicker?",
        "chartKind": "boxplot",
        "variables": ["TOTEXP23", "TOTSLF23", "OBTOTV23", "ERTOT23", "IPDIS23", "RXTOT23", "AFRDCA42", "AFRDDN42", "AFRDPM42", "PERWT23F"],
        "howToRead": "Use the metric selector to compare distributions for the affordability cohort versus everyone else. Wider boxes or higher medians suggest systematically heavier burden on that metric.",
    },
    {
        "id": "afford-insurance",
        "section": "affordability",
        "title": "Does inability to afford care correlate with being uninsured, public, or private?",
        "chartKind": "stackedBar",
        "variables": ["INSCOV23", "AFRDCA42", "AFRDDN42", "AFRDPM42", "PERWT23F"],
        "howToRead": "Each column is one insurance category. The stacked segments show the weighted share with at least one affordability problem versus none.",
        "featured": True,
    },
    {
        "id": "afford-poverty",
        "section": "affordability",
        "title": "Does inability to afford care vary by poverty category?",
        "chartKind": "stackedBar",
        "variables": ["POVCAT23", "AFRDCA42", "AFRDDN42", "AFRDPM42", "PERWT23F"],
        "howToRead": "Read each 100% stacked bar within a poverty band. Taller affordability segments indicate where cost barriers are more common inside that group.",
        "featured": True,
    },
    {
        "id": "afford-income-quintile",
        "section": "affordability",
        "title": "How do affordability barriers change across the family income distribution?",
        "chartKind": "orderedBar",
        "variables": ["FAMINC23", "family_income_quintile", "AFRDCA42", "AFRDDN42", "AFRDPM42", "PERWT23F"],
        "howToRead": "Bars show the weighted affordability-barrier rate by fixed family-income quintile. Read left to right as a distributional gradient from lower-income to higher-income households.",
    },
    {
        "id": "afford-education",
        "section": "affordability",
        "title": "How do affordability barriers shift across education levels?",
        "chartKind": "orderedBar",
        "variables": ["EDUCYR", "education_band", "AFRDCA42", "AFRDDN42", "AFRDPM42", "PERWT23F"],
        "howToRead": "Each bar is the weighted affordability-barrier rate for an adult education band, ordered from less than high school through graduate study to show the education gradient directly.",
        "featured": True,
    },
    {
        "id": "afford-race",
        "section": "affordability",
        "title": "How do affordability barriers vary across broad race groups?",
        "chartKind": "orderedBar",
        "variables": ["RACETHX", "racethx_label", "AFRDCA42", "AFRDDN42", "AFRDPM42", "PERWT23F"],
        "howToRead": "Each bar shows the weighted share of a broad race group reporting at least one affordability barrier. Treat this as a descriptive fairness comparison, not a causal explanation.",
        "featured": True,
    },
    {
        "id": "afford-employment",
        "section": "affordability",
        "title": "Does inability to afford care vary by employment status?",
        "chartKind": "orderedBar",
        "variables": ["EMPST53", "employment_band", "AFRDCA42", "AFRDDN42", "AFRDPM42", "PERWT23F"],
        "howToRead": "Bars compare weighted affordability-problem rates across adult employment status groups derived from the round 5/3 employment status code.",
    },
    {
        "id": "afford-age",
        "section": "affordability",
        "title": "Does inability to afford care vary by age group?",
        "chartKind": "line",
        "variables": ["AGELAST", "age_band", "AFRDCA42", "AFRDDN42", "AFRDPM42", "PERWT23F"],
        "howToRead": "The line traces the weighted rate of affordability problems by age band, making it easy to spot where the burden rises or falls across the life course.",
    },
    {
        "id": "afford-region",
        "section": "affordability",
        "title": "Does inability to afford care vary by region?",
        "chartKind": "bar",
        "variables": ["REGION23", "AFRDCA42", "AFRDDN42", "AFRDPM42", "PERWT23F"],
        "howToRead": "Each regional bar shows the weighted affordability-problem rate for that Census region; state coverage for each region appears in tooltips.",
    },
    {
        "id": "delay-med",
        "section": "delay",
        "title": "How many delayed medical care due to cost?",
        "chartKind": "bar",
        "variables": ["DLAYCA42", "PERWT23F"],
        "howToRead": "The Yes bar estimates people who postponed medical care because of cost; the No bar is the valid remainder.",
    },
    {
        "id": "delay-dental",
        "section": "delay",
        "title": "How many delayed dental care due to cost?",
        "chartKind": "bar",
        "variables": ["DLAYDN42", "PERWT23F"],
        "howToRead": "Use the two weighted bars to compare how many people delayed dental care because of cost versus those who did not.",
    },
    {
        "id": "delay-rx",
        "section": "delay",
        "title": "How many delayed prescribed medicine due to cost?",
        "chartKind": "bar",
        "variables": ["DLAYPM42", "PERWT23F"],
        "howToRead": "This bar chart focuses only on delays in getting prescribed medicine because of cost.",
    },
    {
        "id": "delay-any",
        "section": "delay",
        "title": "What share delayed at least one type due to cost?",
        "chartKind": "donut",
        "variables": ["DLAYCA42", "DLAYDN42", "DLAYPM42", "PERWT23F"],
        "howToRead": "The donut splits valid respondents into those who delayed at least one care type due to cost and those who did not report any delay.",
    },
    {
        "id": "delay-race",
        "section": "delay",
        "title": "How do delayed-care rates vary across broad race groups?",
        "chartKind": "orderedBar",
        "variables": ["RACETHX", "racethx_label", "DLAYCA42", "DLAYDN42", "DLAYPM42", "PERWT23F"],
        "howToRead": "Bars show the weighted delayed-due-to-cost rate within each broad race group. Compare the height of the bars as a descriptive access pattern, not a causal claim.",
    },
    {
        "id": "usc-reasons",
        "section": "no_usc",
        "title": "Among people without a usual source of care, what is the main reason?",
        "chartKind": "rankedBar",
        "variables": ["HAVEUS42", "YNOUSC42_M18", "PERWT23F"],
        "howToRead": "Bars are ranked from the most common to the least common reported reason among people without a usual source of care.",
        "featured": True,
    },
    {
        "id": "usc-cost-share",
        "section": "no_usc",
        "title": "What fraction reports “cost of medical care” as the reason for no usual source of care?",
        "chartKind": "donut",
        "variables": ["HAVEUS42", "YNOUSC42_M18", "PERWT23F"],
        "howToRead": "The donut narrows to the no-USC population only, then splits it between the specific cost-of-medical-care reason and every other reason.",
    },
    {
        "id": "usc-cost-insurance",
        "section": "no_usc",
        "title": "For the “cost reason” subgroup, what is the insurance mix?",
        "chartKind": "stackedBar",
        "variables": ["HAVEUS42", "YNOUSC42_M18", "INSCOV23", "PERWT23F"],
        "howToRead": "This stacked bar isolates the cost-reason subgroup and shows how it is divided across private, public-only, and uninsured coverage categories.",
    },
    {
        "id": "usc-cost-income",
        "section": "no_usc",
        "title": "For the “cost reason” subgroup, what are income and poverty levels?",
        "chartKind": "dualBar",
        "variables": ["HAVEUS42", "YNOUSC42_M18", "POVCAT23", "family_income_quintile", "PERWT23F"],
        "howToRead": "The left panel shows poverty categories and the right panel shows fixed family-income quintiles for the cost-reason subgroup.",
    },
    {
        "id": "can-afford-education-spend",
        "section": "can_afford",
        "title": "Within the can-afford cohort, how does education shape the spending profile?",
        "chartKind": "boxplot",
        "variables": ["can_afford_all", "education_band", "TOTEXP23", "PERWT23F"],
        "howToRead": "Each box compares annual total spending inside the can-afford cohort across adult education bands, showing whether lower reported barriers still coexist with different spending profiles.",
    },
    {
        "id": "can-afford-income-spend",
        "section": "can_afford",
        "title": "Within the can-afford cohort, how does income shape the spending profile?",
        "chartKind": "boxplot",
        "variables": ["can_afford_all", "POVCAT23", "family_income_quintile", "TOTEXP23", "PERWT23F"],
        "howToRead": "The boxes compare annual total spending inside the can-afford cohort across income groups, letting you see whether lower reported barriers still mask different levels of healthcare use or cost.",
    },
    {
        "id": "race-total-spend",
        "section": "can_afford",
        "title": "Across broad race groups, how does annual total spend differ?",
        "chartKind": "boxplot",
        "variables": ["RACETHX", "racethx_label", "TOTEXP23", "PERWT23F"],
        "howToRead": "Each box shows the annual total-spend distribution for one broad race group. Read differences as descriptive burden patterns within the filtered cohort, not as proof of a race effect.",
    },
    {
        "id": "race-oop-burden",
        "section": "can_afford",
        "title": "Across broad race groups, how does annual out-of-pocket burden differ?",
        "chartKind": "boxplot",
        "variables": ["RACETHX", "racethx_label", "TOTSLF23", "PERWT23F"],
        "howToRead": "Each box shows annual out-of-pocket spending for one broad race group, so larger medians or upper tails indicate heavier direct financial burden within that group.",
    },
    {
        "id": "income-oop-share",
        "section": "can_afford",
        "title": "How does out-of-pocket share change across income quintiles?",
        "chartKind": "boxplot",
        "variables": ["family_income_quintile", "oop_share", "PERWT23F"],
        "howToRead": "Each box shows the out-of-pocket share distribution within an income quintile. Lower medians indicate a smaller direct payment share even when people are already using care.",
    },
    {
        "id": "education-delay-rate",
        "section": "can_afford",
        "title": "How do delayed-due-to-cost rates shift across education levels?",
        "chartKind": "orderedBar",
        "variables": ["education_band", "delay_any", "PERWT23F"],
        "howToRead": "Bars show delayed-due-to-cost rates by education band for adults, so you can track whether delay rates fall as educational attainment rises.",
    },
    {
        "id": "income-afford-rate",
        "section": "can_afford",
        "title": "How do affordability barriers fall as income rises?",
        "chartKind": "orderedBar",
        "variables": ["POVCAT23", "afford_any", "PERWT23F"],
        "howToRead": "Read the bars from lower to higher poverty categories to see how affordability barriers taper, persist, or flatten across the income ladder.",
    },
    {
        "id": "low-risk-proxy",
        "section": "low_risk",
        "title": "What fraction of population is low-risk by utilization proxy?",
        "chartKind": "bar",
        "variables": ["LOW_RISK", "PERWT23F"],
        "howToRead": "The bars compare the weighted population share classified as low risk versus not low risk using the existing precomputed low-risk cohort.",
    },
    {
        "id": "low-risk-spend",
        "section": "low_risk",
        "title": "What is average annual spend for low-risk vs non-low-risk?",
        "chartKind": "boxplot",
        "variables": ["LOW_RISK", "TOTEXP23", "PERWT23F"],
        "howToRead": "Each box captures the annual total-spending distribution for one low-risk class; the comparison shows how separated the two cost profiles are.",
    },
    {
        "id": "low-risk-oop",
        "section": "low_risk",
        "title": "What is average out-of-pocket for low-risk vs non-low-risk?",
        "chartKind": "boxplot",
        "variables": ["LOW_RISK", "TOTSLF23", "PERWT23F"],
        "howToRead": "Use the boxes to compare direct out-of-pocket burden for low-risk versus non-low-risk people.",
    },
    {
        "id": "low-risk-uninsured",
        "section": "low_risk",
        "title": "How many uninsured people are low-risk?",
        "chartKind": "stackedBar",
        "variables": ["UNINS23", "LOW_RISK", "PERWT23F"],
        "howToRead": "This chart splits the uninsured-status columns into low-risk and not-low-risk segments so you can size the acquisition opportunity.",
    },
    {
        "id": "low-risk-targetable",
        "section": "low_risk",
        "title": "If low-risk people had lower pricing, how many would be targetable?",
        "chartKind": "funnel",
        "variables": ["LOW_RISK", "UNINS23", "PERWT23F"],
        "howToRead": "The funnel starts with the full filtered population, then narrows to low-risk people and finally to the uninsured low-risk segment as a conservative targetable cohort.",
    },
    {
        "id": "low-risk-payer-mix",
        "section": "low_risk",
        "title": "What is payer mix for the low-risk cohort?",
        "chartKind": "stackedBar",
        "variables": ["LOW_RISK", "TOTPRV23", "TOTMCR23", "TOTMCD23", "TOTSLF23", "PERWT23F"],
        "howToRead": "The stacked bar divides average spending for the low-risk cohort into private, Medicare, Medicaid, and out-of-pocket components.",
    },
    {
        "id": "low-risk-race",
        "section": "low_risk",
        "title": "How does low-risk share vary across broad race groups?",
        "chartKind": "orderedBar",
        "variables": ["RACETHX", "racethx_label", "LOW_RISK", "PERWT23F"],
        "howToRead": "Bars show the weighted share classified as low risk within each broad race group. This is a descriptive subgroup comparison to test fairness and acquisition assumptions, not a causal argument.",
    },
    {
        "id": "low-risk-covered-lives",
        "section": "low_risk",
        "title": "Would focusing only on low-risk uninsured meaningfully expand covered lives?",
        "chartKind": "bar",
        "variables": ["LOW_RISK", "UNINS23", "PERWT23F"],
        "howToRead": "The bars compare three scenario sizes: the entire filtered population, all uninsured people, and the narrower uninsured low-risk group.",
    },
    {
        "id": "student-affordability",
        "section": "student",
        "title": "For ages 17–23, what is affordability profile by student status?",
        "chartKind": "stackedBar",
        "variables": ["FTSTU23X", "AFRDCA42", "AFRDDN42", "AFRDPM42", "PERWT23F"],
        "howToRead": "Within ages 17-23 only, each student-status bar is split into the share with at least one affordability barrier versus none.",
        "featured": True,
    },
    {
        "id": "student-spend",
        "section": "student",
        "title": "For full-time students, what is annual spend and out-of-pocket distribution?",
        "chartKind": "dualBoxplot",
        "variables": ["FTSTU23X", "TOTEXP23", "TOTSLF23", "PERWT23F"],
        "howToRead": "The two box plots summarize total annual spending and out-of-pocket spending for full-time students ages 17-23.",
    },
    {
        "id": "student-insurance",
        "section": "student",
        "title": "For full-time students, what is insurance status distribution?",
        "chartKind": "bar",
        "variables": ["FTSTU23X", "INSCOV23", "PERWT23F"],
        "howToRead": "This weighted bar chart shows how full-time students split across private, public-only, and uninsured coverage.",
    },
    {
        "id": "student-delay",
        "section": "student",
        "title": "For full-time students, what share delayed care due to cost?",
        "chartKind": "bar",
        "variables": ["FTSTU23X", "delay_any", "PERWT23F"],
        "howToRead": "The bars isolate full-time students and show the weighted share that delayed at least one care type due to cost.",
    },
    {
        "id": "student-low-risk-signals",
        "section": "student",
        "title": "Are student low-risk signals stronger than non-students in the same age band?",
        "chartKind": "boxplot",
        "variables": ["FTSTU23X", "LOW_RISK", "CHRONIC_CT", "LIMIT_CT", "NONACUTE_UTIL_CT", "PERWT23F"],
        "howToRead": "Use the metric selector to compare low-risk signals for full-time students versus non-students ages 17-23.",
    },
]

OVERVIEW_METADATA = {
    "heroMetricIds": [
        "afford-med",
        "afford-dental",
        "afford-rx",
        "delay-med",
        "delay-dental",
        "delay-rx",
    ],
    "highlightQuestionIds": [
        "afford-any",
        "afford-total-spend",
        "afford-oop-spend",
        "afford-insurance",
        "afford-income-quintile",
        "afford-education",
        "afford-race",
        "usc-reasons",
        "student-affordability",
    ],
}


@dataclass
class ValidationResult:
    name: str
    value: Any
    detail: str


def parse_float(value: str) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def parse_flag(value: str) -> int | None:
    if value == "1":
        return 1
    if value == "2":
        return 0
    return None


def composite_any(values: list[str]) -> int | None:
    parsed = [parse_flag(value) for value in values]
    if any(value == 1 for value in parsed):
        return 1
    if all(value == 0 for value in parsed):
        return 0
    return None


def label_for(field: str, value: str | int | None) -> str:
    if value is None or value == "":
        return ""
    value_string = str(value)
    return FIELD_LABELS.get(field, {}).get(value_string, value_string)


def derive_age_band(age: float | None) -> str:
    if age is None:
        return ""
    if age <= 17:
        return "0-17"
    if age <= 25:
        return "18-25"
    if age <= 34:
        return "26-34"
    if age <= 44:
        return "35-44"
    if age <= 54:
        return "45-54"
    if age <= 64:
        return "55-64"
    return "65+"


def derive_education_band(age: float | None, educ_years: float | None) -> str:
    if age is None or age < 18 or educ_years is None or educ_years < 0:
        return ""
    if educ_years <= 11:
        return "Less than high school"
    if educ_years == 12:
        return "High school"
    if educ_years <= 15:
        return "Some college"
    if educ_years == 16:
        return "Bachelor"
    return "Graduate"


def derive_employment_band(age: float | None, empst: str) -> str:
    if age is None or age < 18:
        return ""
    return label_for("EMPLOYMENT_BAND", FIELD_LABELS["EMPST53"].get(empst, ""))


def derive_student_group(age: float | None, ftstu: str) -> str:
    if age is None or age < 17 or age > 23:
        return ""
    return label_for("STUDENT_GROUP", FIELD_LABELS["FTSTU23X"].get(ftstu, ""))


def derive_low_risk_label(value: str) -> str:
    if value == "":
        return ""
    return label_for("LOW_RISK", value)


def weighted_quantile_thresholds(rows: list[dict[str, str]]) -> list[float]:
    valid_rows: list[tuple[float, float]] = []
    for row in rows:
        faminc = parse_float(row["FAMINC23"])
        weight = parse_float(row["PERWT23F"])
        if faminc is None or weight is None:
            continue
        valid_rows.append((faminc, weight))
    valid_rows.sort(key=lambda item: item[0])
    total_weight = sum(weight for _, weight in valid_rows)
    targets = [total_weight * share for share in (0.2, 0.4, 0.6, 0.8)]
    thresholds: list[float] = []
    cumulative = 0.0
    target_index = 0
    for value, weight in valid_rows:
        cumulative += weight
        while target_index < len(targets) and cumulative >= targets[target_index]:
            thresholds.append(value)
            target_index += 1
    while len(thresholds) < 4:
        thresholds.append(valid_rows[-1][0])
    return thresholds


def assign_quintile(value: float | None, thresholds: list[float]) -> int | None:
    if value is None:
        return None
    return bisect_right(thresholds, value) + 1


def read_csv_subset(path: Path, fields: list[str]) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return [{field: row[field] for field in fields} for row in reader]


def read_low_risk_lookup(path: Path, fields: list[str]) -> dict[str, dict[str, str]]:
    lookup: dict[str, dict[str, str]] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            person_id = row["DUPERSID"]
            if person_id in lookup:
                raise ValueError(f"Duplicate DUPERSID in low-risk file: {person_id}")
            lookup[person_id] = {field: row[field] for field in fields}
    return lookup


def weighted_yes_share(rows: list[dict[str, Any]], field: str) -> float:
    yes_weight = 0.0
    valid_weight = 0.0
    for row in rows:
        value = row[field]
        if value in ("", None):
            continue
        weight = float(row["perwt23f"])
        valid_weight += weight
        if str(value) in ("1",):
            yes_weight += weight
    return 0.0 if valid_weight == 0 else yes_weight / valid_weight


def affordability_cost_reason_share(rows: list[dict[str, Any]]) -> float:
    subgroup_weight = 0.0
    cost_weight = 0.0
    for row in rows:
        if row["haveus42"] != "2":
            continue
        reason = row["ynousc42_m18"]
        if reason in ("", "-7", "-8"):
            continue
        weight = float(row["perwt23f"])
        subgroup_weight += weight
        if reason == "9":
            cost_weight += weight
    return 0.0 if subgroup_weight == 0 else cost_weight / subgroup_weight


def insurance_breakdown(rows: list[dict[str, Any]]) -> dict[str, float]:
    totals = {key: 0.0 for key in ("1", "2", "3")}
    total_weight = 0.0
    for row in rows:
        value = row["inscov23"]
        if value not in totals:
            continue
        weight = float(row["perwt23f"])
        totals[value] += weight
        total_weight += weight
    if total_weight == 0:
        return {label_for("INSCOV23", key): 0.0 for key in totals}
    return {
        label_for("INSCOV23", key): value / total_weight
        for key, value in totals.items()
    }


def race_breakdown(rows: list[dict[str, Any]]) -> dict[str, float]:
    totals = {key: 0.0 for key in ("1", "2", "3", "4", "5")}
    total_weight = 0.0
    for row in rows:
        value = row["racethx"]
        if value not in totals:
            continue
        weight = float(row["perwt23f"])
        totals[value] += weight
        total_weight += weight
    if total_weight == 0:
        return {label_for("RACETHX", key): 0.0 for key in totals}
    return {
        label_for("RACETHX", key): value / total_weight
        for key, value in totals.items()
    }


def race_row_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    totals = {key: 0 for key in ("1", "2", "3", "4", "5")}
    for row in rows:
        value = row["racethx"]
        if value in totals:
            totals[value] += 1
    return {label_for("RACETHX", key): value for key, value in totals.items()}


def build_rows() -> tuple[list[dict[str, Any]], list[float]]:
    raw_rows = read_csv_subset(RAW_PATH, RAW_FIELDS)
    if len(raw_rows) != EXPECTED_ROWS:
        raise ValueError(f"Expected {EXPECTED_ROWS} raw rows, found {len(raw_rows)}")

    low_risk_lookup = read_low_risk_lookup(LOW_RISK_PATH, LOW_RISK_FIELDS)
    if len(low_risk_lookup) != EXPECTED_ROWS:
        raise ValueError(
            f"Expected {EXPECTED_ROWS} low-risk rows, found {len(low_risk_lookup)}"
        )

    thresholds = weighted_quantile_thresholds(raw_rows)
    rows: list[dict[str, Any]] = []
    seen_ids: set[str] = set()

    for raw in raw_rows:
        person_id = raw["DUPERSID"]
        if person_id in seen_ids:
            raise ValueError(f"Duplicate DUPERSID in raw file: {person_id}")
        seen_ids.add(person_id)
        low_risk = low_risk_lookup.get(person_id)
        if low_risk is None:
            raise ValueError(f"Missing low-risk row for DUPERSID {person_id}")

        afford_any = composite_any([raw["AFRDCA42"], raw["AFRDDN42"], raw["AFRDPM42"]])
        delay_any = composite_any([raw["DLAYCA42"], raw["DLAYDN42"], raw["DLAYPM42"]])
        can_afford_all = None if afford_any is None else (1 if afford_any == 0 else 0)

        age = parse_float(raw["AGELAST"])
        family_income = parse_float(raw["FAMINC23"])
        education_years = parse_float(raw["EDUCYR"])
        quintile = assign_quintile(family_income, thresholds)
        total_spend = parse_float(raw["TOTEXP23"])
        out_of_pocket = parse_float(raw["TOTSLF23"])

        student_group = derive_student_group(age, raw["FTSTU23X"])
        education_band = derive_education_band(age, education_years)
        employment_band = derive_employment_band(age, raw["EMPST53"])

        row = {
            "dupersid": person_id,
            "perwt23f": raw["PERWT23F"],
            "agelast": raw["AGELAST"],
            "age_band": derive_age_band(age),
            "age_focus_17_23": "1" if age is not None and 17 <= age <= 23 else "0",
            "afrdca42": raw["AFRDCA42"],
            "afrdca42_label": label_for("AFRDCA42", raw["AFRDCA42"]),
            "afrddn42": raw["AFRDDN42"],
            "afrddn42_label": label_for("AFRDDN42", raw["AFRDDN42"]),
            "afrdpm42": raw["AFRDPM42"],
            "afrdpm42_label": label_for("AFRDPM42", raw["AFRDPM42"]),
            "dlayca42": raw["DLAYCA42"],
            "dlayca42_label": label_for("DLAYCA42", raw["DLAYCA42"]),
            "dlaydn42": raw["DLAYDN42"],
            "dlaydn42_label": label_for("DLAYDN42", raw["DLAYDN42"]),
            "dlaypm42": raw["DLAYPM42"],
            "dlaypm42_label": label_for("DLAYPM42", raw["DLAYPM42"]),
            "afford_any": "" if afford_any is None else str(afford_any),
            "afford_any_label": label_for("AFFORD_ANY", afford_any),
            "delay_any": "" if delay_any is None else str(delay_any),
            "delay_any_label": label_for("DELAY_ANY", delay_any),
            "can_afford_all": "" if can_afford_all is None else str(can_afford_all),
            "can_afford_all_label": label_for("CAN_AFFORD_ALL", can_afford_all),
            "haveus42": raw["HAVEUS42"],
            "haveus42_label": label_for("HAVEUS42", raw["HAVEUS42"]),
            "ynousc42_m18": raw["YNOUSC42_M18"],
            "ynousc42_m18_label": label_for("YNOUSC42_M18", raw["YNOUSC42_M18"]),
            "cost_reason_no_usc": (
                "1"
                if raw["HAVEUS42"] == "2" and raw["YNOUSC42_M18"] == "9"
                else ("0" if raw["HAVEUS42"] == "2" else "")
            ),
            "cost_reason_no_usc_label": (
                label_for(
                    "COST_REASON_NO_USC",
                    1 if raw["HAVEUS42"] == "2" and raw["YNOUSC42_M18"] == "9" else (
                        0 if raw["HAVEUS42"] == "2" else None
                    ),
                )
            ),
            "totexp23": raw["TOTEXP23"],
            "totslf23": raw["TOTSLF23"],
            "totprv23": raw["TOTPRV23"],
            "totmcr23": raw["TOTMCR23"],
            "totmcd23": raw["TOTMCD23"],
            "oop_share": (
                ""
                if total_spend in (None, 0.0) or out_of_pocket is None
                else f"{out_of_pocket / total_spend:.8f}"
            ),
            "inscov23": raw["INSCOV23"],
            "inscov23_label": label_for("INSCOV23", raw["INSCOV23"]),
            "unins23": raw["UNINS23"],
            "unins23_label": label_for("UNINS23", raw["UNINS23"]),
            "povcat23": raw["POVCAT23"],
            "povcat23_label": label_for("POVCAT23", raw["POVCAT23"]),
            "faminc23": raw["FAMINC23"],
            "family_income_quintile": "" if quintile is None else str(quintile),
            "family_income_quintile_label": label_for(
                "FAMILY_INCOME_QUINTILE", quintile
            ),
            "educyr": raw["EDUCYR"],
            "education_band": education_band,
            "education_band_label": label_for("EDUCATION_BAND", education_band),
            "empst53": raw["EMPST53"],
            "employment_band": employment_band,
            "employment_band_label": employment_band,
            "region23": raw["REGION23"],
            "region23_label": label_for("REGION23", raw["REGION23"]),
            "racethx": raw["RACETHX"],
            "racethx_label": label_for("RACETHX", raw["RACETHX"]),
            "obtotv23": raw["OBTOTV23"],
            "ertot23": raw["ERTOT23"],
            "ipdis23": raw["IPDIS23"],
            "rxtot23": raw["RXTOT23"],
            "ftstu23x": raw["FTSTU23X"],
            "ftstu23x_label": label_for("FTSTU23X", raw["FTSTU23X"]),
            "student_group": student_group,
            "student_group_label": student_group,
            "low_risk": low_risk["LOW_RISK"],
            "low_risk_label": derive_low_risk_label(low_risk["LOW_RISK"]),
            "low_spend": low_risk["LOW_SPEND"],
            "cata_10k": low_risk["CATA_10K"],
            "cata_20k": low_risk["CATA_20K"],
            "chronic_ct": low_risk["CHRONIC_CT"],
            "limit_ct": low_risk["LIMIT_CT"],
            "chronic_burden_bin": low_risk["CHRONIC_BURDEN_BIN"],
            "limit_burden_bin": low_risk["LIMIT_BURDEN_BIN"],
            "nonacute_util_ct": low_risk["NONACUTE_UTIL_CT"],
            "nonacute_util_band": low_risk["NONACUTE_UTIL_BAND"],
            "acute_util_any": low_risk["ACUTE_UTIL_ANY"],
            "spend_band_2023": low_risk["SPEND_BAND_2023"],
        }
        rows.append(row)

    if len(rows) != EXPECTED_ROWS:
        raise ValueError(f"Expected {EXPECTED_ROWS} joined rows, found {len(rows)}")
    return rows, thresholds


def write_people(rows: list[dict[str, Any]]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with PEOPLE_OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_metadata(rows: list[dict[str, Any]], thresholds: list[float]) -> list[ValidationResult]:
    validations = [
        ValidationResult(
            name="row_count",
            value=len(rows),
            detail="Joined row count after merging raw and low-risk data.",
        ),
        ValidationResult(
            name="weighted_share_afford_med",
            value=round(weighted_yes_share(rows, "afrdca42"), 6),
            detail="Weighted share answering Yes to AFRDCA42 among valid responses.",
        ),
        ValidationResult(
            name="weighted_share_delay_med",
            value=round(weighted_yes_share(rows, "dlayca42"), 6),
            detail="Weighted share answering Yes to DLAYCA42 among valid responses.",
        ),
        ValidationResult(
            name="inscov23_breakdown",
            value={
                key: round(value, 6) for key, value in insurance_breakdown(rows).items()
            },
            detail="Weighted insurance breakdown across valid INSCOV23 responses.",
        ),
        ValidationResult(
            name="cost_reason_share_among_no_usc",
            value=round(affordability_cost_reason_share(rows), 6),
            detail="Weighted share of the no-USC population citing cost of medical care as the reason.",
        ),
        ValidationResult(
            name="racethx_unweighted_counts",
            value=race_row_counts(rows),
            detail="Unweighted row counts for the five broad RACETHX groups.",
        ),
        ValidationResult(
            name="racethx_weighted_share",
            value={key: round(value, 6) for key, value in race_breakdown(rows).items()},
            detail="Weighted population share across the five broad RACETHX groups.",
        ),
    ]

    metadata = {
        "source": {
            "raw": str(RAW_PATH.relative_to(ROOT)),
            "lowRisk": str(LOW_RISK_PATH.relative_to(ROOT)),
            "generatedFrom": "scripts/build_affordability_data.py",
        },
        "dataset": {
            "year": 2023,
            "rowCount": len(rows),
            "quintileThresholds": thresholds,
        },
        "specialValues": SPECIAL_VALUES,
        "valueLabels": FIELD_LABELS,
        "variableLabels": VARIABLE_SHORT_LABELS,
        "sections": SECTION_METADATA,
        "questions": QUESTION_METADATA,
        "overview": OVERVIEW_METADATA,
        "assumptions": [
            "Default reporting is weighted with Person weight.",
            "Could-not-afford cohort equals any of Afford medical, Afford dental, or Afford meds coded Yes.",
            "Delayed-due-to-cost cohort equals any of Delay medical, Delay dental, or Delay meds coded Yes.",
            "Can-afford cohort equals No across Afford medical, Afford dental, and Afford meds; mixed valid-and-missing patterns remain unknown for composite cards.",
            "Broad race comparisons use Race group exactly as labeled in the MEPS documentation.",
            "This site frames low-risk and affordability findings as fairness and acquisition exploration, not causal proof.",
        ],
        "proxyNotes": {
            "no_usc": "The no-USC section is a proxy analysis. No-USC reason describes the main reason for not having a usual source of care, not a direct insurance purchase reason.",
            "low_risk": "Low risk is taken from the existing processed low-risk export and used as the primary low-risk cohort for scenario sizing.",
            "fairness": "Income, education, and Race group comparisons are descriptive subgroup views from survey data. They help surface fairness and access patterns, but they do not identify a single causal mechanism.",
        },
        "validation": [
            {"name": item.name, "value": item.value, "detail": item.detail}
            for item in validations
        ],
    }

    with METADATA_OUT.open("w", encoding="utf-8") as handle:
        json.dump(metadata, handle, indent=2)

    return validations


def main() -> None:
    rows, thresholds = build_rows()
    write_people(rows)
    validations = write_metadata(rows, thresholds)
    print(f"Wrote {PEOPLE_OUT.relative_to(ROOT)}")
    print(f"Wrote {METADATA_OUT.relative_to(ROOT)}")
    for item in validations:
        print(f"{item.name}: {item.value}")


if __name__ == "__main__":
    main()
