"""E4: declared one-component sensitivities; all results retained, no search for winners."""

import argparse
import time
from dataclasses import replace

from .cohort import build_cohort
from .config import read_config
from .dictionary import dictionary
from .experiments import run_e1
from .provenance import ROOT, finish_run, start_run, write_json
from .survey import taylor_mean

VARIANTS = {
    "reference": {},
    "legacy_count": {"burden": "legacy12"},
    "legacy_missing": {"missingness": "legacy_zero"},
    "legacy_label": {"label": "legacy_484_4"},
    "unweighted_training": {"weighted_training": False},
    "adult_core": {"population": "adult_core"},
    "domain_additions": {"blocks": ["B3_INS", "B3_SES", "B3_UTIL"]},
}


def run_variant(name: str, changes: dict, base, prefix: str) -> None:
    config = replace(base, blocks=["B3"], seeds=[base.seeds[0]])
    config = replace(config, **changes)
    out, manifest = start_run(f"{prefix}-{name}", config, "E4")
    started = time.perf_counter()
    try:
        frame, design, flow = build_cohort(ROOT / config.raw, config)
        frame.to_parquet(out / "cohort.parquet", index=False)
        design.to_csv(out / "design.csv", index=False)
        write_json(out / "cohort_flow.json", flow)
        write_json(
            out / "dictionary.json",
            dictionary(config.population, config.burden, config.missingness),
        )
        write_json(out / "survey_mean.json", taylor_mean(frame, design, "TOTEXP23"))
        run_e1(frame, design, config, out)
        finish_run(out, manifest, "complete", time.perf_counter() - started)
    except BaseException as error:
        finish_run(
            out,
            manifest,
            "interrupted" if isinstance(error, (KeyboardInterrupt, SystemExit)) else "failed",
            time.perf_counter() - started,
            str(error),
        )
        raise


def main() -> None:
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--config", required=True)
    cli.add_argument("--prefix", required=True)
    args = cli.parse_args()
    from pathlib import Path

    config = read_config(Path(args.config))
    for name, changes in VARIANTS.items():
        run_variant(name, changes, config, args.prefix)


if __name__ == "__main__":
    main()
