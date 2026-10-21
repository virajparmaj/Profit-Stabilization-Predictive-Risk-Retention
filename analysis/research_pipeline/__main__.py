"""Command-line entry point for source-built research, with no cache fallback."""

import argparse
import time
from pathlib import Path

from .cohort import build_cohort
from .config import read_config
from .dictionary import dictionary
from .provenance import ROOT, finish_run, start_run, write_json
from .reporting import render_report
from .survey import taylor_mean


def parser() -> argparse.ArgumentParser:
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("command", choices=["build", "validate", "run", "report"])
    cli.add_argument(
        "--config", type=Path, default=Path(__file__).parent / "configs/primary_2023.yaml"
    )
    cli.add_argument("--experiment", choices=["E1", "E2"], default="E1")
    cli.add_argument("--run-id", required=True)
    cli.add_argument("--output", type=Path, help="Fresh directory required for derived reports")
    cli.add_argument(
        "--pilot",
        action="store_true",
        help="20 E2 refits/50 evaluation replicates; never final evidence",
    )
    cli.add_argument(
        "--inference", action="store_true", help="Add paired conditional survey intervals to E1"
    )
    return cli


def execute(args) -> None:
    config = read_config(args.config)
    if args.pilot:
        config.refits = 20
        config.design_replicates = 50
    out, manifest = start_run(
        args.run_id, config, args.experiment if args.command == "run" else args.command
    )
    manifest["pilot"] = args.pilot
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
        if args.command == "run":
            run_experiment(args, frame, design, config, out)
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
    print(f"Completed: {out}", flush=True)


def run_experiment(args, frame, design, config, out) -> None:
    if args.experiment == "E1":
        import pandas as pd

        from .experiments import run_e1
        from .inference import run_inference

        run_e1(frame, design, config, out)
        if args.inference:
            run_inference(pd.read_parquet(out / "scores.parquet"), design, config, out)
    else:
        from .refits import run_e2

        run_e2(frame, design, config, out)


def main() -> None:
    args = parser().parse_args()
    if args.command == "report":
        # Validate the run ID even for read/report operations: do not permit path traversal.
        if not args.run_id or any(
            c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-"
            for c in args.run_id
        ):
            raise ValueError("Invalid run ID")
        if args.output is None:
            raise ValueError("report requires --output pointing to a new directory")
        render_report(ROOT / "analysis/research_runs" / args.run_id, args.output)
    else:
        execute(args)


if __name__ == "__main__":
    main()
