"""Source-built cohort integration and provenance failure tests."""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from analysis.research_pipeline.cohort import build_cohort
from analysis.research_pipeline.config import Config
from analysis.research_pipeline.dictionary import DX, FUNCTION, blocks
from analysis.research_pipeline.provenance import sha256, write_json
from analysis.research_pipeline.reporting import verify_run
from analysis.research_pipeline.survey import resample_training, taylor_mean


def synthetic_raw(n: int = 30) -> pd.DataFrame:
    frame = pd.DataFrame(
        {
            f: np.ones(n)
            for fs in blocks().values()
            for f in fs
            if not f.startswith(("DX_CT", "LIMIT_CT"))
        }
    )
    for name in DX + FUNCTION + ["ANYLMI23", "COVIDEVER53"]:
        frame[name] = 2
    for name, value in {
        "DUPERSID": np.arange(n) + 1000,
        "DUID": np.repeat(np.arange(n // 2), 2),
        "PANEL": 28,
        "VARSTR": 1,
        "VARPSU": np.tile([1, 2], n // 2),
        "PERWT23F": 10.0,
        "SAQWT23F": 20.0,
        "SAQELIG": 1,
        "AGE42X": 30,
        "AGELAST": 30,
        "TOTEXP23": np.arange(n) * 100,
        "ERTOT23": 0,
        "IPDIS23": 0,
        "INSCOV23": 1,
    }.items():
        frame[name] = value
    return frame


def test_build_preserves_income_and_excludes_ineligible(tmp_path):
    raw = synthetic_raw()
    raw.loc[0, "FAMINC23"] = -230
    raw.loc[0, "TTLP23X"] = -1500
    raw.loc[0, "K6SUM42"] = -15
    raw.loc[1, "SAQWT23F"] = 0
    raw.loc[2, "AGE42X"] = 17
    path = tmp_path / "raw.csv"
    raw.to_csv(path, index=False)
    f, design, flow = build_cohort(path, Config())
    assert len(f) == len(raw) - 2
    assert f.FAMINC23.iloc[0] == -230
    assert f.TTLP23X.iloc[0] == -1500
    assert np.isnan(f.K6SUM42.iloc[0])
    assert f.K6SUM42_code.iloc[0] == -15
    assert flow["weight_sum"] == (len(raw) - 2) * 20
    assert len(design) == 2


def test_duplicate_ids_and_unknown_categories_fail(tmp_path):
    raw = synthetic_raw()
    raw.loc[1, "DUPERSID"] = raw.DUPERSID.iloc[0]
    path = tmp_path / "raw.csv"
    raw.to_csv(path, index=False)
    with pytest.raises(ValueError, match="ID"):
        build_cohort(path, Config())
    raw = synthetic_raw()
    raw.loc[0, "PHYEXE53"] = 99
    raw.to_csv(path, index=False)
    with pytest.raises(ValueError, match="category"):
        build_cohort(path, Config())
    raw = synthetic_raw()
    raw.loc[0, "TOTEXP23"] = np.nan
    raw.to_csv(path, index=False)
    with pytest.raises(ValueError, match="endpoint"):
        build_cohort(path, Config())


def test_changed_artifact_or_failed_run_cannot_be_reported(tmp_path):
    data = tmp_path / "scores.txt"
    data.write_text("original")
    manifest = {"status": "complete", "outputs": {"scores.txt": sha256(data)}}
    write_json(tmp_path / "manifest.json", manifest)
    assert verify_run(tmp_path)["status"] == "complete"
    data.write_text("modified")
    with pytest.raises(ValueError, match="changed"):
        verify_run(tmp_path)
    manifest["status"] = "failed"
    write_json(tmp_path / "manifest.json", manifest)
    with pytest.raises(ValueError, match="complete"):
        verify_run(tmp_path)


def test_training_resample_preserves_psu_clusters():
    frame = pd.DataFrame(
        {
            "VARSTR": [1] * 8,
            "VARPSU": [1] * 4 + [2] * 4,
            "DUPERSID": np.arange(8),
            "weight": np.ones(8),
        }
    )
    design = frame[["VARSTR", "VARPSU"]].drop_duplicates()
    sample = resample_training(frame, design, 42)
    assert sample.VARPSU.nunique() == 1
    assert len(sample) == 4
    assert (sample.weight == 2).all()
    assert set(sample.DUPERSID) in [set(range(4)), set(range(4, 8))]


def test_refit_scores_do_not_depend_on_reference_outcomes(tmp_path):
    from analysis.research_pipeline.refits import run_e2
    from analysis.research_pipeline.splits import reference_split

    path = tmp_path / "raw.csv"
    synthetic_raw(120).to_csv(path, index=False)
    config = Config(refits=2, xgb_estimators=5, threads=1)
    frame, design, _ = build_cohort(path, config)
    first, second = tmp_path / "first", tmp_path / "second"
    first.mkdir()
    second.mkdir()
    run_e2(frame, design, config, first)
    changed = frame.copy()
    _, _, reference = reference_split(frame, config.seeds[0])
    changed.loc[reference, "TOTEXP23"] = 1e8
    run_e2(changed, design, config, second)
    for original in first.glob("*_refit_scores.parquet"):
        pd.testing.assert_frame_equal(
            pd.read_parquet(original), pd.read_parquet(second / original.name)
        )
    assert json.loads((first / "endpoint.json").read_text()) == json.loads(
        (second / "endpoint.json").read_text()
    )


def test_failed_refit_is_recorded_without_replacement(tmp_path, monkeypatch):
    from analysis.research_pipeline import refits
    from analysis.research_pipeline.splits import reference_split
    from analysis.research_pipeline.targets import cutoff

    path = tmp_path / "raw.csv"
    synthetic_raw(120).to_csv(path, index=False)
    config = Config(refits=2, xgb_estimators=5, threads=1)
    frame, design, _ = build_cohort(path, config)
    tr, ca, re = reference_split(frame, config.seeds[0])
    real = refits.resample_training

    def fail_first(training, design, seed):
        if seed == config.refit_seed:
            raise RuntimeError("deliberate failed replicate")
        return real(training, design, seed)

    monkeypatch.setattr(refits, "resample_training", fail_first)
    _, failures = refits.run_anchor(
        frame.iloc[tr],
        frame.iloc[ca],
        frame.iloc[re],
        design,
        cutoff(frame.iloc[tr], config.label),
        "B3",
        "logistic",
        config,
        tmp_path,
    )
    assert failures == [
        {"refit": 0, "type": "RuntimeError", "error": "deliberate failed replicate"}
    ]
    diagnostics = json.loads((tmp_path / "B3_logistic_diagnostics.json").read_text())
    assert diagnostics["successful_refits"] == 1
    assert diagnostics["requested_refits"] == 2


@pytest.mark.skipif(not Path("data_raw/h251.csv").exists(), reason="Local MEPS data not downloaded")
def test_official_hc251_cohort_and_r_survey_benchmark():
    frame, design, flow = build_cohort(Path("data_raw/h251.csv"), Config())
    assert flow["analytic_n"] == 9776
    assert flow["weight_sum"] == pytest.approx(258426861.976141, rel=1e-10)
    assert flow["legacy_label_n"] == 5579
    assert flow["legacy_label_threshold"] == pytest.approx(484.4)
    result = taylor_mean(frame, design, "TOTEXP23")
    # Independently regenerated by validate_survey.R using R survey 4.5.
    assert result["mean"] == pytest.approx(8947.95486093106, rel=1e-10)
    assert result["se"] == pytest.approx(275.828694889383, rel=1e-10)
