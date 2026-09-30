"""Explicit, validated experiment settings; no implicit cache reuse."""

from dataclasses import asdict, dataclass, field
from pathlib import Path

import yaml


@dataclass
class Config:
    protocol: str = "meps-low-spending-v1"
    raw: str = "data_raw/h251.csv"
    population: str = "adult_saq"
    burden: str = "dx10"
    missingness: str = "explicit"
    label: str = "training_weighted"
    weighted_training: bool = True
    folds: int = 5
    seeds: list[int] = field(default_factory=lambda: [42, 2026])
    blocks: list[str] = field(default_factory=lambda: ["D", "C", "B0", "B2", "B3", "B4", "B5"])
    models: list[str] = field(default_factory=lambda: ["logistic", "xgboost"])
    capacity: float = 0.30
    capacities: list[float] = field(default_factory=lambda: [0.1, 0.2, 0.3, 0.4, 0.5])
    tail_threshold: float = 20000
    refits: int = 200
    design_replicates: int = 1000
    refit_seed: int = 1842
    design_seed: int = 9142
    tie_seed: int = 7342
    xgb_estimators: int = 600
    threads: int = 2

    def validate(self) -> None:
        from .dictionary import blocks

        choices = {
            "population": ["adult_saq", "adult_core"],
            "burden": ["dx10", "legacy12"],
            "missingness": ["explicit", "legacy_zero"],
            "label": ["training_weighted", "legacy_484_4"],
        }
        for name, allowed in choices.items():
            if getattr(self, name) not in allowed:
                raise ValueError(f"Invalid {name}: {getattr(self, name)}")
        if not self.blocks or not set(self.blocks) <= set(blocks(self.population)):
            raise ValueError("Unsupported or empty feature-block selection")
        if not self.models or not set(self.models) <= {"logistic", "xgboost", "random_forest"}:
            raise ValueError("Unsupported or empty model selection")
        if self.folds < 2 or not self.seeds or len(set(self.seeds)) != len(self.seeds):
            raise ValueError("Need at least two folds and distinct seeds")
        if not 0 < self.capacity < 1 or not all(0 < q < 1 for q in self.capacities):
            raise ValueError("Research capacities must be between zero and one")
        if min(self.refits, self.design_replicates, self.xgb_estimators, self.threads) < 1:
            raise ValueError("Replicate, tree and thread counts must be positive")
        if self.tail_threshold <= 0:
            raise ValueError("Tail threshold must be positive")

    def as_dict(self) -> dict:
        return asdict(self)


def read_config(path: Path) -> Config:
    config = Config(**yaml.safe_load(path.read_text()))
    config.validate()
    return config
