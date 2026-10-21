"""Tests for the direct-cost comparator and conditional ensemble summaries."""

import numpy as np
import pandas as pd
import pytest

from analysis.research_pipeline.cohort import build_cohort
from analysis.research_pipeline.config import Config
from analysis.research_pipeline.paper_extensions import TwoPartCost, ranking
from analysis.research_pipeline.selection import select_capacity
from analysis.tests.research_pipeline.test_provenance_and_integration import synthetic_raw


def test_cost_baseline_uses_training_outcomes_only(tmp_path):
    raw = synthetic_raw(120)
    raw.loc[::4, "TOTEXP23"] = 0
    raw.loc[:, "K6SUM42"] = np.arange(120) % 20
    path = tmp_path / "raw.csv"
    raw.to_csv(path, index=False)
    frame, _, _ = build_cohort(path, Config())
    model = TwoPartCost().fit(frame.iloc[:80], Config(), 42)
    reference = frame.iloc[80:].copy()
    before = model.predict(reference)
    reference["TOTEXP23"] = 1e9
    reference["ERTOT23"] = 20
    reference["IPDIS23"] = 30
    np.testing.assert_array_equal(before, model.predict(reference))
    assert np.isfinite(before).all() and (before >= 0).all()
    assert model.scale == pytest.approx(np.average(frame.iloc[:80].query("TOTEXP23 > 0").TOTEXP23))


def test_cost_ranking_selects_lowest_cost_and_is_scale_invariant():
    weights = [1, 2, 1, 2]
    ids = ["a", "b", "c", "d"]
    cost = np.array([100, 200, 0, 900])
    selected = select_capacity(ranking(cost), weights, ids, 0.3)
    assert selected.tolist() == [True, False, True, False]
    np.testing.assert_array_equal(selected, select_capacity(ranking(cost * 100), weights, ids, 0.3))


def test_cost_model_all_positive_and_all_zero(tmp_path):
    raw = synthetic_raw(120)
    raw["TOTEXP23"] += 100
    path = tmp_path / "raw.csv"
    raw.to_csv(path, index=False)
    frame, _, _ = build_cohort(path, Config())
    model = TwoPartCost().fit(frame, Config(), 42)
    assert model.occurrence is None and (model.predict(frame) > 0).all()
    frame["TOTEXP23"] = 0
    with pytest.raises(ValueError, match="No positive"):
        TwoPartCost().fit(frame, Config(), 42)


def test_conditional_reference_matches_person_average_and_r_benchmark(tmp_path):
    import json

    from analysis.research_pipeline.paper_extensions import conditional_reference
    from analysis.research_pipeline.provenance import sha256, write_json

    ref = pd.DataFrame(
        {
            "DUPERSID": ["a", "b", "c", "d"],
            "VARSTR": [1, 1, 2, 2],
            "VARPSU": [1, 2, 1, 2],
            "weight": [1.0, 2.0, 3.0, 4.0],
        }
    )
    source = tmp_path / "source"
    source.mkdir()
    ref.to_parquet(source / "reference.parquet", index=False)
    ref[["VARSTR", "VARPSU"]].to_csv(source / "design.csv", index=False)
    for model, selected in [
        ("logistic", [[1, 0, 0, 1], [1, 1, 0, 0]]),
        ("xgboost", [[0, 1, 1, 0], [0, 0, 1, 1]]),
    ]:
        pd.DataFrame({"DUPERSID": ref.DUPERSID, "selected": [1, 0, 0, 1]}).to_parquet(
            source / f"B3_{model}_base.parquet"
        )
        pd.concat(
            [
                pd.DataFrame({"DUPERSID": ref.DUPERSID, "refit": b, "selected": a})
                for b, a in enumerate(selected)
            ]
        ).to_parquet(source / f"B3_{model}_refit_scores.parquet")
    write_json(
        source / "manifest.json",
        {
            "status": "complete",
            "config": {"refits": 2},
            "outputs": {f.name: sha256(f) for f in source.iterdir()},
        },
    )
    output = tmp_path / "result.json"
    conditional_reference(source, output, 1000)
    result = json.loads(output.read_text())
    # Logistic disagreement [0,.5,0,.5]; boosted [1,.5,1,.5].
    assert result["estimate"] == pytest.approx(-0.4)
    assert result["taylor"]["mean"] == pytest.approx(-0.4)
    assert "not joint" in result["interpretation"]
    with pytest.raises(FileExistsError):
        conditional_reference(source, output)
