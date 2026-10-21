"""Regression coverage for report integrity and interrupted research workflows."""

import json
import warnings
from argparse import Namespace

import numpy as np
import pandas as pd
import pytest

from analysis.research_pipeline import experiments, provenance, reporting
from analysis.research_pipeline.aggregation import refit_statistics, weighted_metrics
from analysis.research_pipeline.cohort import build_cohort
from analysis.research_pipeline.config import Config
from analysis.research_pipeline.diagnostics import record_fit
from analysis.research_pipeline.dictionary import dictionary
from analysis.research_pipeline.export_results import export_run
from analysis.research_pipeline.selection import select_capacity, tie_keys
from analysis.tests.research_pipeline.test_provenance_and_integration import synthetic_raw


@pytest.mark.parametrize(
    "changes",
    [
        {"capacities": []},
        {"capacities": [0.3, 0.3]},
        {"capacity": 0.35},
        {"models": ["logistic", "logistic"]},
        {"blocks": ["B3", "B3"]},
        {"refits": 1},
        {"design_replicates": 1},
    ],
)
def test_ambiguous_config_rejected(changes):
    with pytest.raises(ValueError):
        Config(**changes).validate()


def test_missing_required_fold_is_undefined_not_diluted():
    group = pd.DataFrame({"auc": [0.8, np.nan], "weight_sum": [100, 100]})
    result = weighted_metrics(group, ["auc"])
    assert np.isnan(result["auc"])
    assert (result["auc_valid"], result["auc_expected"]) == (1, 2)
    assert np.isnan(weighted_metrics(group.iloc[:1], ["auc"], expected=2)["auc"])
    group.loc[1, "auc"] = 0.6
    assert weighted_metrics(group, ["auc"])["auc"] == pytest.approx(0.7)
    stats = refit_statistics(pd.Series([0.8, np.nan]), 2)
    assert stats["valid"] == 1 and stats["expected"] == 2 and np.isnan(stats["mean"])


def make_run(path, version=2):
    path.mkdir()
    config = Config().as_dict()
    provenance.write_json(path / "config.json", config)
    provenance.write_json(path / "cohort_flow.json", {"analytic_n": 30, "weight_sum": 600})
    for name in ["dictionary.json", "survey_mean.json"]:
        provenance.write_json(path / name, {})
    for name in ["cohort.parquet", "design.csv"]:
        (path / name).write_text("fixture")
    manifest = {
        "manifest_version": version,
        "status": "running",
        "experiment": "validate",
        "config": config,
        "input_sha256": "fixture",
        "elapsed_seconds": 0,
        "config_sha256": provenance.sha256(path / "config.json"),
        "pilot": True,
    }
    provenance.write_json(path / "manifest.json", manifest)
    provenance.finish_run(path, manifest, "complete", 1)
    if version == 1:
        # Faithful historical limitation: report was created after the manifest.
        manifest["outputs"].pop("REPORT.md")
        provenance.write_json(path / "manifest.json", manifest)
    return manifest


@pytest.mark.parametrize("name", ["REPORT.md", "config.json", "cohort.parquet"])
def test_new_run_detects_tampering(tmp_path, name):
    source = tmp_path / "source"
    manifest = make_run(source)
    assert reporting.verify_run(source)["outputs"]["REPORT.md"]
    with pytest.raises(ValueError, match="immutable"):
        provenance.finish_run(source, manifest, "complete", 2)
    (source / name).write_text("tampered")
    with pytest.raises(ValueError, match="changed"):
        reporting.verify_run(source)


def test_required_output_cannot_disappear_from_manifest(tmp_path):
    source = tmp_path / "source"
    manifest = make_run(source)
    del manifest["outputs"]["cohort.parquet"]
    provenance.write_json(source / "manifest.json", manifest)
    with pytest.raises(ValueError, match="required"):
        reporting.verify_run(source)


def test_report_failure_never_marks_complete(tmp_path, monkeypatch):
    source = tmp_path / "source"
    make_run(source)
    manifest = json.loads((source / "manifest.json").read_text())
    manifest["status"] = "running"
    provenance.write_json(source / "manifest.json", manifest)

    def broken(*args):
        raise RuntimeError("report failed")

    monkeypatch.setattr(reporting, "report_text", broken)
    with pytest.raises(RuntimeError):
        provenance.finish_run(source, manifest, "complete", 1)
    assert json.loads((source / "manifest.json").read_text())["status"] == "running"


def test_legacy_report_is_derived_without_copying_unhashed_text(tmp_path):
    source = tmp_path / "legacy"
    make_run(source, version=1)
    (source / "REPORT.md").write_text("UNTRUSTED OLD REPORT")
    before = {f.name: provenance.sha256(f) for f in source.iterdir()}
    output = tmp_path / "derived"
    reporting.render_report(source, output)
    report = (output / "REPORT.md").read_text()
    assert "UNTRUSTED" not in report and "Legacy manifest" in report and "PILOT" in report
    assert before == {f.name: provenance.sha256(f) for f in source.iterdir()}
    with pytest.raises(FileExistsError):
        reporting.render_report(source, output)
    with pytest.raises(ValueError, match="immutable"):
        reporting.render_report(source, source / "derived")
    export_run(source, tmp_path / "export")
    assert not (tmp_path / "export/legacy/REPORT.md").exists()
    assert (tmp_path / "export/legacy/derived/REPORT.md").exists()


def test_export_refuses_existing_target_and_excludes_person_files(tmp_path):
    source = tmp_path / "source"
    make_run(source)
    (source / "unlisted-person.csv").write_text("person_id\n123")
    output = tmp_path / "export"
    export_run(source, output)
    assert not list(output.rglob("cohort.parquet"))
    assert not list(output.rglob("unlisted-person.csv"))
    (output / "source/leftover.csv").write_text("person_id\n123")
    with pytest.raises(FileExistsError):
        export_run(source, output)


def test_replication_report_preserves_audited_year_dictionary(tmp_path):
    source = tmp_path / "source"
    manifest = make_run(source)
    entries = [{"feature": "TOTEXP23", "source": ["TOTEXP21"], "data_year": 2021}]
    provenance.write_json(source / "dictionary.json", entries)
    manifest.update(data_year=2021, scope="Same-year repetition; not temporal transport")
    manifest["outputs"]["dictionary.json"] = provenance.sha256(source / "dictionary.json")
    provenance.write_json(source / "manifest.json", manifest)
    output = tmp_path / "derived"
    reporting.render_report(source, output)
    assert json.loads((output / "dictionary.json").read_text()) == entries
    assert "Data year: 2021" in (output / "REPORT.md").read_text()


@pytest.mark.parametrize(
    "exception,status", [(RuntimeError, "failed"), (KeyboardInterrupt, "interrupted")]
)
def test_warning_before_failure_persists(tmp_path, exception, status):
    with pytest.raises(exception):
        with record_fit(tmp_path, experiment="E1", seed=42, fold=0, block="B3", model="logistic"):
            warnings.warn("warning before failure")
            raise exception("stopped")
    record = json.loads((tmp_path / "fit_log.jsonl").read_text())
    assert record["status"] == status and record["warnings"] == ["warning before failure"]
    assert record["elapsed_seconds"] >= 0


def test_e1_preserves_earlier_fit_diagnostics_on_failure(tmp_path, monkeypatch):
    raw = tmp_path / "raw.csv"
    synthetic_raw(120).to_csv(raw, index=False)
    config = Config(blocks=["B3"], models=["logistic"], seeds=[42])
    frame, design, _ = build_cohort(raw, config)
    real = experiments.fit_model
    calls = 0

    def failing(*args):
        nonlocal calls
        calls += 1
        if calls == 2:
            warnings.warn("second fit warning")
            raise RuntimeError("second fit failed")
        return real(*args)

    monkeypatch.setattr(experiments, "fit_model", failing)
    with pytest.raises(RuntimeError):
        experiments.run_e1(frame, design, config, tmp_path)
    records = [json.loads(line) for line in (tmp_path / "fit_log.jsonl").read_text().splitlines()]
    assert [r["status"] for r in records] == ["complete", "failed"]
    assert records[1]["warnings"] == ["second fit warning"]


def test_random_aggregate_matches_within_fold_selection():
    from analysis.research_pipeline.metrics import selected_spending

    config = Config(capacities=[0.3])
    frame = pd.DataFrame(
        {
            "seed": 42,
            "block": "B3",
            "model": "logistic",
            "fold": [0] * 10 + [1] * 10,
            "DUPERSID": [str(i) for i in range(20)],
            "weight": np.arange(1, 21),
            "TOTEXP23": np.arange(20) * 100,
            "score": np.linspace(0, 1, 20),
        }
    )
    selected = np.zeros(len(frame), bool)
    for _, indices in frame.groupby("fold").groups.items():
        fold = frame.loc[indices]
        scores = np.argsort(np.argsort(tie_keys(fold.DUPERSID, config.tie_seed))) / len(fold)
        selected[indices] = select_capacity(
            scores, fold.weight, fold.DUPERSID, 0.3, config.tie_seed
        )
    result = experiments.aggregate_policies(frame, config).query("model == 'random'").iloc[0]
    expected = selected_spending(frame, selected, threshold=config.tail_threshold)
    for key in ["mean", "sd", "cv", "capacity", "n"]:
        assert result[key] == pytest.approx(expected[key])


def test_dictionary_matches_population_burden_and_missingness():
    explicit = {d["feature"]: d for d in dictionary("adult_saq")}
    legacy = {d["feature"]: d for d in dictionary("adult_core", "legacy12", "legacy_zero")}
    assert "K6SUM42_code" in explicit and "K6SUM42_code" not in legacy
    assert explicit["DX_CT"]["source"] != legacy["DX_CT"]["source"]
    assert explicit["AGELAST"]["missing"] != legacy["AGELAST"]["missing"]
    assert legacy["AGELAST_code"]["kind"] == "categorical"
    assert "Partial legacy" in legacy["AGELAST"]["missing"]
    assert legacy["FAMINC23"]["negative_values"] == "valid income losses"


def test_interrupt_marks_run_incomplete(tmp_path, monkeypatch):
    from analysis.research_pipeline import __main__ as cli

    source = tmp_path / "run"
    source.mkdir()
    manifest = {"status": "running", "manifest_version": 2}
    provenance.write_json(source / "manifest.json", manifest)
    monkeypatch.setattr(cli, "read_config", lambda _: Config())
    monkeypatch.setattr(cli, "start_run", lambda *args: (source, manifest))

    def interrupt(*args):
        raise KeyboardInterrupt()

    monkeypatch.setattr(cli, "build_cohort", interrupt)
    with pytest.raises(KeyboardInterrupt):
        cli.execute(
            Namespace(config=None, pilot=False, run_id="test", experiment="E1", command="run")
        )
    assert json.loads((source / "manifest.json").read_text())["status"] == "interrupted"
    with pytest.raises(ValueError, match="complete"):
        export_run(source, tmp_path / "export")


def test_e2_base_warning_is_preserved_on_failure(tmp_path, monkeypatch):
    from analysis.research_pipeline import refits

    def broken(*args):
        warnings.warn("base fit warning")
        raise RuntimeError("base fit failed")

    monkeypatch.setattr(refits, "base_fit", broken)
    with pytest.raises(RuntimeError):
        refits.run_anchor(None, None, None, None, 0, "B3", "logistic", Config(), tmp_path)
    record = json.loads((tmp_path / "fit_log.jsonl").read_text())
    assert record["refit"] == -1 and record["status"] == "failed"
    assert record["warnings"] == ["base fit warning"]


def test_empty_selection_preserves_undefined_metric_schema():
    from analysis.research_pipeline.metrics import selected_spending

    frame = pd.DataFrame({"weight": [1, 2], "TOTEXP23": [0, 10]})
    result = selected_spending(frame, [False, False])
    assert result["capacity"] == 0 and result["status"] == "empty"
    assert result["mean"] is None and result["cv"] is None
