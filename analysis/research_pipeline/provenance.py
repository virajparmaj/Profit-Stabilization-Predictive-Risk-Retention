"""Immutable run directories with code/data/config/environment fingerprints."""

import hashlib
import importlib.metadata
import json
import platform
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value) -> None:
    def default(item):
        if isinstance(item, np.generic):
            return item.item()
        raise TypeError(type(item).__name__)

    path.write_text(json.dumps(value, indent=2, default=default, allow_nan=False) + "\n")


def git_output(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def start_run(name: str, config, experiment: str) -> tuple[Path, dict]:
    if not name or any(
        c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-" for c in name
    ):
        raise ValueError("Run ID must contain only letters, digits, underscores and hyphens")
    config.validate()
    out = ROOT / "analysis/research_runs" / name
    out.mkdir(parents=True, exist_ok=False)
    cfg = config.as_dict()
    write_json(out / "config.json", cfg)
    packages = ["numpy", "pandas", "scipy", "scikit-learn", "xgboost", "pyarrow", "PyYAML"]
    source_files = sorted(Path(__file__).parent.rglob("*.py"))
    snapshot = out / "source"
    snapshot.mkdir()
    for source in source_files:
        relative = source.relative_to(Path(__file__).parent)
        (snapshot / relative).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, snapshot / relative)
    manifest = {
        "run_id": name,
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "experiment": experiment,
        "status": "running",
        "config": cfg,
        "config_sha256": sha256(out / "config.json"),
        "input_sha256": sha256(ROOT / config.raw),
        "dependency_lock_sha256": sha256(Path(__file__).with_name("requirements-lock.txt")),
        "git_revision": git_output("rev-parse", "HEAD"),
        "git_status": git_output("status", "--short"),
        "source_hashes": {str(p.relative_to(ROOT)): sha256(p) for p in source_files},
        "versions": {p: importlib.metadata.version(p) for p in packages},
        "python": platform.python_version(),
        "platform": platform.platform(),
        "uncertainty": "Survey evaluation conditional on fixed predictions; E2 learning variability separate",
        "scope": "Exploratory same-year HC-251, not prospective or causal",
    }
    write_json(out / "manifest.json", manifest)
    return out, manifest


def finish_run(
    out: Path, manifest: dict, status: str, elapsed: float, error: str | None = None
) -> None:
    manifest.update(status=status, elapsed_seconds=elapsed, error=error)
    manifest["outputs"] = {
        str(p.relative_to(out)): sha256(p)
        for p in sorted(out.rglob("*"))
        if p.is_file() and p.name != "manifest.json"
    }
    write_json(out / "manifest.json", manifest)
