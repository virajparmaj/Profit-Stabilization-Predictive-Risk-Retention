"""Replication must preserve measurements and reject overlapping annual samples."""

import pandas as pd
import pytest

from analysis.research_pipeline.config import Config
from analysis.research_pipeline.replication import ANNUAL_MAP, harmonize_2021, verify_disjoint


def sample():
    return pd.DataFrame(
        {
            **{name: [1, -7] for name in ANNUAL_MAP},
            "PANEL": [23, 26],
            "DUPERSID": ["2301", "2601"],
            "DUID": ["23", "26"],
            "K6SUM42": [3, -15],
        }
    )


def test_harmonization_preserves_values_and_input():
    raw = sample()
    before = raw.copy(deep=True)
    result = harmonize_2021(raw, Config(blocks=["B3"]))
    pd.testing.assert_frame_equal(raw, before)
    for source, alias in ANNUAL_MAP.items():
        assert result[alias].tolist() == raw[source].tolist()
    assert result.K6SUM42.tolist() == [3, -15]
    assert result.COVIDEVER53.eq(-9).all()


@pytest.mark.parametrize(
    "config", [Config(blocks=["B3_COVID"]), Config(burden="legacy12"), Config(label="legacy_484_4")]
)
def test_unsupported_replication_is_rejected(config):
    with pytest.raises(ValueError):
        harmonize_2021(sample(), config)


def test_missing_or_ambiguous_year_rejected():
    with pytest.raises(ValueError, match="Missing"):
        harmonize_2021(sample().drop(columns="TOTEXP21"), Config())
    with pytest.raises(ValueError, match="ambiguous"):
        harmonize_2021(sample().assign(TOTEXP23=1), Config())


def test_nonoverlap_checks_every_identity_level():
    primary = pd.DataFrame({"PANEL": [28], "DUPERSID": ["2801"], "DUID": ["28"]})
    assert verify_disjoint(sample(), primary)["overlapping_dupersid"] == 0
    for column in ["PANEL", "DUPERSID", "DUID"]:
        changed = primary.copy()
        changed[column] = sample()[column].iloc[0]
        with pytest.raises(ValueError, match="overlaps"):
            verify_disjoint(sample(), changed)
