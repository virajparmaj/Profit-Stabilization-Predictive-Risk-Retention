"""Fold-local preprocessing and comparable weighted learning pipelines."""

import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBClassifier

from .config import Config
from .dictionary import CATEGORIES, SENTINELS, blocks


def make_pipeline(frame, block: str, model: str, config: Config, seed: int) -> Pipeline:
    features = blocks(config.population)[block]
    categorical = [f for f in features if f in CATEGORIES]
    numeric = [f for f in features if f not in CATEGORIES]
    codes = [f"{f}_code" for f in numeric if f"{f}_code" in frame]
    category_values = [sorted(set(CATEGORIES[f] + SENTINELS + [0])) for f in categorical]
    category_values += [sorted(SENTINELS + [0])] * len(codes)
    transforms = []
    if categorical or codes:
        transforms.append(
            (
                "categories",
                OneHotEncoder(
                    categories=category_values, handle_unknown="error", sparse_output=False
                ),
                categorical + codes,
            )
        )
    if numeric:
        transforms.append(
            (
                "numeric",
                Pipeline(
                    [
                        (
                            "impute",
                            SimpleImputer(
                                strategy="median", keep_empty_features=True, add_indicator=True
                            ),
                        ),
                        ("scale", StandardScaler()),
                    ]
                ),
                numeric,
            )
        )
    estimators = {
        "logistic": lambda: LogisticRegression(C=1.0, solver="lbfgs", max_iter=2000, tol=1e-6),
        "xgboost": lambda: XGBClassifier(
            n_estimators=config.xgb_estimators,
            max_depth=4,
            learning_rate=0.05,
            subsample=0.9,
            colsample_bytree=0.9,
            reg_lambda=1,
            n_jobs=config.threads,
            random_state=seed,
            tree_method="hist",
            eval_metric="logloss",
        ),
        "random_forest": lambda: RandomForestClassifier(
            n_estimators=400, min_samples_leaf=10, n_jobs=config.threads, random_state=seed
        ),
    }
    if model not in estimators:
        raise ValueError(f"Unknown model {model}")
    return Pipeline([("preprocess", ColumnTransformer(transforms)), ("model", estimators[model]())])


def fit_model(training, y, block: str, model: str, config: Config, seed: int):
    if set(np.unique(y)) != {0, 1}:
        raise ValueError("Training requires both outcome classes")
    pipe = make_pipeline(training, block, model, config, seed)
    w = training.weight.to_numpy(float) if config.weighted_training else np.ones(len(training))
    if not np.isfinite(w).all() or (w <= 0).any():
        raise ValueError("Fit requires finite positive weights")
    pipe.fit(training, y, model__sample_weight=w / w.mean())
    return pipe


def positive_probability(pipe, frame) -> np.ndarray:
    classes = list(pipe.classes_)
    if 1 not in classes:
        raise ValueError("Positive label class absent")
    p = pipe.predict_proba(frame)[:, classes.index(1)]
    if not np.isfinite(p).all() or ((p < 0) | (p > 1)).any():
        raise ValueError("Invalid predicted probabilities")
    return p
