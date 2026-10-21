"""HC-233 (2021) independent-panel repetition of the HC-251 research protocol.

Annual aliases adapt the fixed internal 2023 schema; they do not change measurement
year or inflate 2021 dollars. COVIDEVER53 is unavailable and never analyzed here.
"""

import argparse
import time
from pathlib import Path

import pandas as pd

from .cohort import build_cohort
from .config import Config, read_config
from .dictionary import dictionary
from .experiments import run_e1
from .inference import run_inference
from .provenance import ROOT, finish_run, sha256, start_run, write_json
from .refits import run_e2
from .survey import taylor_mean

DOCUMENTATION = "https://meps.ahrq.gov/data_stats/download_data/pufs/h233/h233doc.shtml"
DATA_URL = "https://meps.ahrq.gov/data_files/pufs/h233/h233dta.zip"
ANNUAL_MAP = {
    f"{prefix}21{suffix}": f"{prefix}23{suffix}"
    for prefix, suffix in [
        ("PERWT", "F"),
        ("SAQWT", "F"),
        ("TOTEXP", ""),
        ("ERTOT", ""),
        ("IPDIS", ""),
        ("INSCOV", ""),
        ("POVCAT", ""),
        ("FAMINC", ""),
        ("TTLP", "X"),
        ("INSURC", ""),
        ("UNINS", ""),
        ("PRVEV", ""),
        ("MCREV", ""),
        ("MCDEV", ""),
        ("OBTOTV", ""),
        ("OPTOTV", ""),
        ("RXTOT", ""),
    ]
}


def verify_disjoint(raw: pd.DataFrame, primary: pd.DataFrame) -> dict:
    """Reject overlapping panels, people, or dwellings before fitting anything."""
    evidence = {}
    for column in ["PANEL", "DUPERSID", "DUID"]:
        if raw[column].isna().any() or primary[column].isna().any():
            raise ValueError(f"Missing {column} prevents overlap check")
        left, right = set(raw[column].astype(str)), set(primary[column].astype(str))
        overlap = left & right
        evidence[f"overlapping_{column.lower()}"] = len(overlap)
        if overlap:
            raise ValueError(f"Replication overlaps primary {column}")
    evidence["replication_panels"] = sorted(int(x) for x in raw.PANEL.unique())
    evidence["primary_panels"] = sorted(int(x) for x in primary.PANEL.unique())
    return evidence


def harmonize_2021(raw: pd.DataFrame, config: Config) -> pd.DataFrame:
    """Rename audited annual fields; preserve all original values and round fields."""
    if config.population != "adult_saq" or config.burden != "dx10":
        raise ValueError("Replication supports adult_saq/dx10 only")
    if "B3_COVID" in config.blocks or config.label != "training_weighted":
        raise ValueError("Replication excludes unavailable COVID and legacy-dollar labels")
    missing = set(ANNUAL_MAP) - set(raw.columns)
    if missing:
        raise ValueError(f"Missing 2021 annual variables: {sorted(missing)}")
    if set(ANNUAL_MAP.values()) & set(raw.columns):
        raise ValueError("Input already has target aliases; refusing ambiguous year")
    if not set(raw.PANEL.unique()) <= {23, 24, 25, 26}:
        raise ValueError("Unexpected panel in HC-233 input")
    result = raw.rename(columns=ANNUAL_MAP).copy()
    # build_cohort validates every available block, including unselected COVID.
    # This sentinel is an explicitly unavailable schema placeholder, never a model input.
    result["COVIDEVER53"] = -9
    return result


def execute(config: Config, run_id: str, experiment: str, primary: Path) -> Path:
    raw = pd.read_csv(ROOT / config.raw, dtype={"DUPERSID": str, "DUID": str})
    primary_raw = pd.read_csv(
        primary, usecols=["DUPERSID", "DUID", "PANEL"], dtype={"DUPERSID": str, "DUID": str}
    )
    overlap = verify_disjoint(raw, primary_raw)
    harmonized = harmonize_2021(raw, config)
    out, manifest = start_run(run_id, config, experiment)
    manifest.update(
        pilot=False,
        data_year=2021,
        scope="Exploratory same-year HC-233 independent-panel repetition; not temporal transport validation",
        replication_primary_sha256=sha256(primary),
    )
    started = time.perf_counter()
    try:
        harmonized.to_csv(out / "harmonized_input.csv", index=False)
        frame, design, flow = build_cohort(out / "harmonized_input.csv", config)
        flow.update(data_year=2021, original_weight="SAQWT21F", dollars="2021 nominal dollars")
        frame.to_parquet(out / "cohort.parquet", index=False)
        design.to_csv(out / "design.csv", index=False)
        write_json(out / "cohort_flow.json", flow)
        entries = dictionary(config.population, config.burden, config.missingness)
        inverse = {v: k for k, v in ANNUAL_MAP.items()}
        for entry in entries:
            entry.update(documentation=DOCUMENTATION, weight="SAQWT21F", data_year=2021)
            entry["source"] = [inverse.get(source, source) for source in entry["source"]]
            if entry["feature"] == "COVIDEVER53":
                entry.update(
                    source=[],
                    available=False,
                    missing="Unavailable schema placeholder; prohibited model input",
                )
            entry["timing"] = (
                "Same calendar year; 31/42/53 include rounds 7/8/9 or 5/6/7 for extended panels"
            )
        write_json(out / "dictionary.json", entries)
        write_json(out / "survey_mean.json", taylor_mean(frame, design, "TOTEXP23"))
        write_json(
            out / "harmonization.json",
            {
                "data_year": 2021,
                "documentation": DOCUMENTATION,
                "data_url": DATA_URL,
                "annual_aliases": ANNUAL_MAP,
                "round_variables": "Names and values unchanged",
                "unavailable_placeholder": "COVIDEVER53=-9; never used by selected blocks",
                "dollars": "2021 nominal; no between-year dollar effect estimated",
                "overlap_check": overlap,
                "primary_sha256": sha256(primary),
                "interpretation": "Independent people/panels; shared survey design and pandemic context remain",
                "pandemic_caveat": "2021 extended panels and telephone response changes limit simple trend interpretations",
            },
        )
        if experiment == "E1":
            run_e1(frame, design, config, out)
            run_inference(pd.read_parquet(out / "scores.parquet"), design, config, out)
        else:
            run_e2(frame, design, config, out)
        finish_run(out, manifest, "complete", time.perf_counter() - started)
    except BaseException as error:
        finish_run(
            out,
            manifest,
            "interrupted" if isinstance(error, (KeyboardInterrupt, SystemExit)) else "failed",
            time.perf_counter() - started,
            f"{type(error).__name__}: {error}",
        )
        raise
    print(f"Completed replication: {out}", flush=True)
    return out


def main() -> None:
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument(
        "--config", type=Path, default=Path(__file__).parent / "configs/replication_2021.yaml"
    )
    cli.add_argument("--primary", type=Path, default=ROOT / "data_raw/h251.csv")
    cli.add_argument("--run-id", required=True)
    cli.add_argument("--experiment", choices=["E1", "E2"], required=True)
    args = cli.parse_args()
    execute(read_config(args.config), args.run_id, args.experiment, args.primary)


if __name__ == "__main__":
    main()
