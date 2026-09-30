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


def dictionary(population: str, burden: str = "dx10") -> list[dict]:
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
                "missing": "distinct reserved codes; training-fold numeric median plus code indicator",
                "negative_values": "valid income losses" if name in INCOME else "reserved codes",
                "timing": (
                    "same-year; round 4/2 SAQ" if name in HEALTH[2:] else "same-year; not baseline"
                ),
                "population": population,
                "documentation": DOC,
            }
        )
    return result
