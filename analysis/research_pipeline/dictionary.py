"""Literal feature definitions from HC-251; income losses are valid values."""

DX = [
    "HIBPDX",
    "DIABDX_M18",
    "CHDDX",
    "MIDX",
    "STRKDX",
    "EMPHDX",
    "CHOLDX",
    "ARTHDX",
    "ASTHDX",
    "CANCERDX",
]
FUNCTION = ["ADLHLP31", "IADLHP31", "WLKLIM31", "COGLIM31", "WRKLIM31", "SOCLIM31"]
BEHAVIOR = ["PHYEXE53", "OFTSMK53"]
HEALTH = ["RTHLTH53", "MNHLTH53", "K6SUM42", "PHQ242"]
SES = [
    "POVCAT23",
    "FAMINC23",
    "TTLP23X",
    "INSURC23",
    "UNINS23",
    "PRVEV23",
    "MCREV23",
    "MCDEV23",
    "EMPST53",
]
UTIL = ["OBTOTV23", "OPTOTV23", "RXTOT23"]
SENTINELS = [-15, -9, -8, -7, -1]
COUNT_AUX = ["unknown", "inapplicable", "refused", "dont_know", "not_ascertained", "cannot_compute"]
INCOME = ["FAMINC23", "TTLP23X"]
CATEGORIES = {
    "SEX": [1, 2],
    "PHYEXE53": [1, 2],
    "OFTSMK53": [1, 2, 3],
    "RTHLTH53": [1, 2, 3, 4, 5],
    "MNHLTH53": [1, 2, 3, 4, 5],
    "POVCAT23": [1, 2, 3, 4, 5],
    "INSURC23": list(range(1, 9)),
    "UNINS23": [1, 2],
    "PRVEV23": [1, 2],
    "MCREV23": [1, 2],
    "MCDEV23": [1, 2],
    "EMPST53": [1, 2, 3, 4],
    "COVIDEVER53": [1, 2],
}
DOC = "https://meps.ahrq.gov/data_stats/download_data/pufs/h251/h251doc.shtml"


def count_features(prefix: str) -> list[str]:
    return [prefix] + [f"{prefix}_{suffix}" for suffix in COUNT_AUX]


def blocks(population: str = "adult_saq") -> dict[str, list[str]]:
    health = HEALTH if population == "adult_saq" else HEALTH[:2]
    b1 = BEHAVIOR + health
    b2 = b1 + count_features("LIMIT_CT")
    b3 = b2 + count_features("DX_CT")
    return {
        "D": ["AGELAST", "SEX"],
        "C": ["AGELAST", "SEX"] + count_features("LIMIT_CT") + count_features("DX_CT"),
        "B0": BEHAVIOR,
        "B1": b1,
        "B2": b2,
        "B3": b3,
        "B4": b3 + SES,
        "B5": b3 + SES + UTIL,
        "B3_INS": b3 + ["INSURC23", "UNINS23", "PRVEV23", "MCREV23", "MCDEV23"],
        "B3_SES": b3 + ["POVCAT23", "FAMINC23", "TTLP23X", "EMPST53"],
        "B3_UTIL": b3 + UTIL,
        "B3_COVID": b3 + ["COVIDEVER53"],
    }


def dictionary(population: str, burden: str = "dx10", missingness: str = "explicit") -> list[dict]:
    result = []
    for name in dict.fromkeys(f for fs in blocks(population).values() for f in fs):
        diagnoses = DX + ["ANYLMI23", "COVIDEVER53"] if burden == "legacy12" else DX
        sources = (
            diagnoses
            if name.startswith("DX_CT")
            else FUNCTION if name.startswith("LIMIT_CT") else [name]
        )
        result.append(
            {
                "feature": name,
                "source": sources,
                "kind": "categorical" if name in CATEGORIES else "numeric",
                "valid_categories": CATEGORIES.get(name),
                "missing": missing_description(name, missingness),
                "missingness": missingness,
                "burden": burden,
                "weight": "SAQWT23F" if population == "adult_saq" else "PERWT23F",
                "negative_values": "valid income losses" if name in INCOME else "reserved codes",
                "timing": (
                    "same-year; round 4/2 SAQ" if name in HEALTH[2:] else "same-year; not baseline"
                ),
                "population": population,
                "documentation": DOC,
            }
        )
        if (
            name not in CATEGORIES
            and name not in INCOME
            and not name.startswith(("DX_CT", "LIMIT_CT"))
        ):
            result.append(
                {
                    **result[-1],
                    "feature": f"{name}_code",
                    "kind": "categorical",
                    "valid_categories": [0] + SENTINELS,
                    "missing": "Original negative code; zero denotes observed value. Retained even in partial legacy_zero sensitivity.",
                }
            )
    return result


def missing_description(name: str, missingness: str) -> str:
    if name in INCOME:
        return "Negative income losses preserved; unexpected raw NaN rejected."
    if name.startswith(("DX_CT", "LIMIT_CT")):
        if missingness == "legacy_zero":
            return "Unknown source responses contribute zero; all count missingness auxiliaries forced to zero."
        return "Affirmative lower-bound count; all-unknown total is NaN imputed within training; separate counts preserve unknown and each reserved code."
    if missingness == "legacy_zero":
        return "Partial legacy sensitivity: negative values replaced by zero; numeric code indicators retained. Not exact historical notebook reproduction."
    if name in CATEGORIES:
        return "Distinct reserved categories preserved and encoded inside each fit."
    return "Negative values become NaN; training-fold median imputation plus original-code categorical indicator."
