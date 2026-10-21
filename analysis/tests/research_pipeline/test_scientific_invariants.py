"""Tests target scientific failure modes, not implementation-shaped snapshots."""

import numpy as np
import pandas as pd
import pytest

from analysis.research_pipeline.cohort import add_count
from analysis.research_pipeline.config import Config
from analysis.research_pipeline.dictionary import DX
from analysis.research_pipeline.metrics import classification, membership, spending
from analysis.research_pipeline.models import fit_model, positive_probability
from analysis.research_pipeline.selection import select_capacity, weighted_quantile
from analysis.research_pipeline.splits import outer_folds, reference_split
from analysis.research_pipeline.survey import multipliers, replicate_design, taylor_mean
from analysis.research_pipeline.targets import cutoff, labels


def test_high_score_direction_and_exact_boundaries():
    assert select_capacity([0.9, 0.6, 0.2], [1, 1, 1], ["a", "b", "c"], 1 / 3).tolist() == [
        True,
        False,
        False,
    ]
    assert not select_capacity([0.2, 0.8], [1, 1], ["a", "b"], 0).any()
    assert select_capacity([0.2, 0.8], [1, 1], ["a", "b"], 1).all()


def test_weighted_capacity_ties_are_permutation_invariant():
    ids = np.array(["a", "b", "c", "d"])
    w = np.array([7.0, 2.0, 3.0, 1.0])
    order = np.array([2, 0, 3, 1])
    a = select_capacity(np.ones(4), w, ids, 0.3)
    b = select_capacity(np.ones(4), w[order], ids[order], 0.3)
    assert set(ids[a]) == set(ids[order][b])
    assert np.array_equal(a, select_capacity(np.ones(4), w * 100, ids, 0.3))
    with pytest.raises(ValueError):
        select_capacity([0.1, 0.9], [1, 1], ["a", "a"], 0.3)


@pytest.mark.parametrize("x,w", [([np.nan], [1]), ([1], [-1]), ([1], [0]), ([], [])])
def test_invalid_selection_inputs(x, w):
    with pytest.raises(ValueError):
        select_capacity(x, w, list(range(len(x))), 0.3)


def test_endpoint_boundary_and_training_only_cutoff():
    train = pd.DataFrame({"TOTEXP23": [0, 100, 200, 300], "weight": [1] * 4})
    threshold = cutoff(train, "training_weighted")
    test = pd.DataFrame(
        {
            "TOTEXP23": [threshold, threshold + 1, 0, 0],
            "ERTOT23": [0, 0, 1, 0],
            "IPDIS23": [0, 0, 0, 1],
        }
    )
    assert labels(test, threshold).tolist() == [1, 0, 0, 0]
    test.TOTEXP23 = 1e9
    assert cutoff(train, "training_weighted") == threshold
    assert weighted_quantile([0, 10], [0, 1], 0) == 10


def test_corrected_count_preserves_missing_and_excludes_construct_overlap():
    frame = pd.DataFrame({f: [2, -8, 2] for f in DX})
    frame["ANYLMI23"] = 1
    frame["COVIDEVER53"] = 1
    frame.loc[2, DX[0]] = 1
    add_count(frame, DX, "DX_CT", False)
    assert frame.DX_CT.iloc[0] == 0
    assert np.isnan(frame.DX_CT.iloc[1])
    assert frame.DX_CT_unknown.iloc[1] == 10
    assert frame.DX_CT_dont_know.iloc[1] == 10
    assert frame.DX_CT.iloc[2] == 1


def test_mixture_identity_scaling_and_tail_definition():
    costs, weights = np.array([0.0, 0.0, 10000.0, 20000.0, 40000.0]), np.array(
        [1.0, 2.0, 1.0, 3.0, 1.0]
    )
    result = spending(costs, weights)
    p = 1 - result["zero_share"]
    assert result["cv"] ** 2 == pytest.approx((result["positive_cv"] ** 2 + 1 - p) / p)
    scaled = spending(costs * 10, weights * 30, threshold=200000)
    assert scaled["mean"] == pytest.approx(result["mean"] * 10)
    assert scaled["sd"] == pytest.approx(result["sd"] * 10)
    assert scaled["cv"] == pytest.approx(result["cv"])
    assert result["tail_count"] == 2
    assert result["mean_excess"] == 2500
    assert spending([0, 0], [1, 1])["cv"] is None
    assert spending([2, 2], [1, 1])["cv"] == 0


def test_membership_is_not_headcount():
    a, b = [1, 1, 0, 0], [0, 0, 1, 1]
    assert sum(a) == sum(b)
    assert membership(a, b, [1] * 4) == {
        "jaccard": 0.0,
        "population_disagreement": 1.0,
        "baseline_member_loss": 1.0,
    }
    assert membership(a, a, [1] * 4)["jaccard"] == 1
    assert membership([0, 0], [0, 0], [1, 1])["jaccard"] is None


def test_random_fixed_size_control():
    rng = np.random.default_rng(42)
    n, q = 20000, 0.3
    a = np.zeros(n, bool)
    b = a.copy()
    a[rng.choice(n, int(n * q), replace=False)] = True
    b[rng.choice(n, int(n * q), replace=False)] = True
    assert membership(a, b, np.ones(n))["jaccard"] == pytest.approx(q / (2 - q), abs=0.012)


def test_group_partitions_have_no_household_leakage():
    frame = pd.DataFrame({"DUID": np.repeat(np.arange(50), 3)})
    covered = []
    for _, train, test in outer_folds(frame, 5, 42):
        assert not set(frame.iloc[train].DUID) & set(frame.iloc[test].DUID)
        covered.extend(test)
    assert sorted(covered) == list(range(len(frame)))
    parts = reference_split(frame, 42)
    assert len(np.unique(np.concatenate(parts))) == len(frame)
    for i, a in enumerate(parts):
        for b in parts[i + 1 :]:
            assert not set(frame.iloc[a].DUID) & set(frame.iloc[b].DUID)


def test_pipeline_imputation_and_positive_class_lookup():
    config = Config(blocks=["D"], models=["logistic"])
    frame = pd.DataFrame(
        {
            "AGELAST": [20.0, 30.0, np.nan, 50.0, 60.0, 70.0],
            "SEX": [1, 2, 1, 2, 1, 2],
            "weight": np.ones(6),
        }
    )
    pipe = fit_model(frame, np.array([0, 0, 0, 1, 1, 1]), "D", "logistic", config, 42)
    before = (
        pipe.named_steps["preprocess"].named_transformers_["numeric"]["impute"].statistics_.copy()
    )
    heldout = frame.copy()
    heldout.AGELAST = 1e9
    positive_probability(pipe, heldout)
    np.testing.assert_array_equal(
        before, pipe.named_steps["preprocess"].named_transformers_["numeric"]["impute"].statistics_
    )

    class Reversed:
        classes_ = np.array([1, 0])

        def predict_proba(self, frame):
            return np.tile([0.8, 0.2], (len(frame), 1))

    assert (positive_probability(Reversed(), frame) == 0.8).all()


def test_single_outcome_auc_is_undefined():
    assert classification([1, 1], [0.7, 0.9], [1, 1])["auc"] is None


def test_survey_design_and_domain_linearization():
    design = pd.DataFrame({"VARSTR": [1, 1, 2, 2], "VARPSU": [1, 2, 1, 2]})
    reps = replicate_design(design, 10000, 42)
    assert np.isin(reps.iloc[:, 2:], [0, 2]).all()
    assert np.all(reps.iloc[:2, 2:].sum(axis=0) == 2)
    frame = design.copy()
    frame["weight"], frame["cost"] = [1.0, 1.0, 1.0, 1.0], [0.0, 2.0, 4.0, 6.0]
    assert taylor_mean(frame, design, "cost")["mean"] == 3
    assert taylor_mean(frame, design, "cost")["variance"] == pytest.approx(0.5)
    factors = multipliers(frame, reps)
    means = (frame.cost.to_numpy()[:, None] * factors).sum(axis=0) / factors.sum(axis=0)
    assert np.mean((means - 3) ** 2) == pytest.approx(0.5, abs=0.02)
    # A domain omitting a whole PSU retains a zero linearized PSU contribution.
    domain = frame.iloc[[0, 2, 3]]
    assert taylor_mean(domain, design, "cost")["se"] > 0
    with pytest.raises(ValueError, match="Singleton"):
        replicate_design(design.iloc[:1], 3, 42)


def test_config_rejects_unavailable_saq_blocks():
    with pytest.raises(ValueError):
        Config(population="unknown").validate()
    with pytest.raises(ValueError):
        Config(blocks=["NOT_A_BLOCK"]).validate()
