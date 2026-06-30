"""Tests for fastbreak.model_eval — probabilistic forecast scoring."""

from __future__ import annotations

import math

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

# ---------- brier_score ----------


class TestBrierScore:
    def test_perfect_predictions_score_zero(self) -> None:
        from fastbreak.model_eval import brier_score

        assert brier_score([1.0, 0.0, 1.0], [1, 0, 1]) == pytest.approx(0.0)

    def test_worst_predictions_score_one(self) -> None:
        from fastbreak.model_eval import brier_score

        assert brier_score([0.0, 1.0], [1, 0]) == pytest.approx(1.0)

    def test_constant_half_scores_quarter(self) -> None:
        from fastbreak.model_eval import brier_score

        assert brier_score([0.5, 0.5, 0.5, 0.5], [1, 0, 1, 0]) == pytest.approx(0.25)

    def test_rejects_length_mismatch(self) -> None:
        from fastbreak.model_eval import brier_score

        with pytest.raises(ValueError, match="length"):
            brier_score([0.5, 0.5], [1])

    def test_rejects_empty(self) -> None:
        from fastbreak.model_eval import brier_score

        with pytest.raises(ValueError, match="empty"):
            brier_score([], [])

    def test_rejects_prob_out_of_range(self) -> None:
        from fastbreak.model_eval import brier_score

        with pytest.raises(ValueError, match="probabilit"):
            brier_score([1.5], [1])

    def test_rejects_non_binary_outcome(self) -> None:
        from fastbreak.model_eval import brier_score

        with pytest.raises(ValueError, match="outcome"):
            brier_score([0.5], [2])


@given(
    data=st.lists(
        st.tuples(
            st.floats(min_value=0.0, max_value=1.0),
            st.integers(min_value=0, max_value=1),
        ),
        min_size=1,
        max_size=50,
    )
)
@settings(max_examples=300)
def test_brier_in_unit_interval(data: list[tuple[float, int]]) -> None:
    from fastbreak.model_eval import brier_score

    probs = [p for p, _ in data]
    outcomes = [y for _, y in data]
    assert 0.0 <= brier_score(probs, outcomes) <= 1.0


# ---------- log_loss ----------


class TestLogLoss:
    def test_confident_correct_is_near_zero(self) -> None:
        from fastbreak.model_eval import log_loss

        assert log_loss([0.999999, 1e-6], [1, 0]) == pytest.approx(0.0, abs=1e-5)

    def test_constant_half_is_ln_two(self) -> None:
        from fastbreak.model_eval import log_loss

        assert log_loss([0.5, 0.5], [1, 0]) == pytest.approx(math.log(2.0))

    def test_clips_confident_wrong_no_inf(self) -> None:
        from fastbreak.model_eval import log_loss

        # p=0 but outcome=1 would be -log(0)=inf without clipping.
        result = log_loss([0.0], [1])
        assert math.isfinite(result)
        assert result > 0.0

    def test_rejects_length_mismatch(self) -> None:
        from fastbreak.model_eval import log_loss

        with pytest.raises(ValueError, match="length"):
            log_loss([0.5], [1, 0])

    def test_rejects_empty(self) -> None:
        from fastbreak.model_eval import log_loss

        with pytest.raises(ValueError, match="empty"):
            log_loss([], [])

    def test_rejects_nonpositive_eps(self) -> None:
        from fastbreak.model_eval import log_loss

        # eps <= 0 makes the clip ineffective: log(0) for a confident-wrong p.
        with pytest.raises(ValueError, match="eps"):
            log_loss([0.0], [1], eps=0.0)

    def test_rejects_eps_at_or_above_half(self) -> None:
        from fastbreak.model_eval import log_loss

        # eps >= 0.5 inverts the clip window (min(max(p, eps), 1-eps)).
        with pytest.raises(ValueError, match="eps"):
            log_loss([0.5], [1], eps=0.5)


@given(
    data=st.lists(
        st.tuples(
            st.floats(min_value=0.0, max_value=1.0),
            st.integers(min_value=0, max_value=1),
        ),
        min_size=1,
        max_size=50,
    )
)
@settings(max_examples=300)
def test_log_loss_nonnegative_and_finite(data: list[tuple[float, int]]) -> None:
    from fastbreak.model_eval import log_loss

    probs = [p for p, _ in data]
    outcomes = [y for _, y in data]
    result = log_loss(probs, outcomes)
    assert math.isfinite(result)
    assert result >= 0.0


# ---------- roi ----------


class TestRoi:
    def test_breakeven_is_zero(self) -> None:
        from fastbreak.model_eval import roi

        # Staked 2 units total, got 2 back in profit-neutral terms.
        assert roi(stakes=[1.0, 1.0], profits=[1.0, -1.0]) == pytest.approx(0.0)

    def test_all_winners(self) -> None:
        from fastbreak.model_eval import roi

        # Stake 1 unit each, win 1 unit profit each -> 100% ROI.
        assert roi(stakes=[1.0, 1.0], profits=[1.0, 1.0]) == pytest.approx(1.0)

    def test_all_losers(self) -> None:
        from fastbreak.model_eval import roi

        assert roi(stakes=[1.0, 1.0], profits=[-1.0, -1.0]) == pytest.approx(-1.0)

    def test_rejects_length_mismatch(self) -> None:
        from fastbreak.model_eval import roi

        with pytest.raises(ValueError, match="length"):
            roi(stakes=[1.0], profits=[1.0, 1.0])

    def test_rejects_zero_total_stake(self) -> None:
        from fastbreak.model_eval import roi

        with pytest.raises(ValueError, match="stake"):
            roi(stakes=[0.0, 0.0], profits=[0.0, 0.0])

    def test_rejects_negative_stake(self) -> None:
        from fastbreak.model_eval import roi

        # A negative stake is nonsensical and can mask a real total via netting.
        with pytest.raises(ValueError, match="stake"):
            roi(stakes=[-1.0, 5.0], profits=[0.0, 1.0])

    def test_rejects_nan_profit(self) -> None:
        from fastbreak.model_eval import roi

        # NaN profit would propagate to a NaN ROI instead of raising.
        with pytest.raises(ValueError, match="finite"):
            roi(stakes=[1.0, 1.0], profits=[math.nan, 0.5])

    def test_rejects_infinite_stake(self) -> None:
        from fastbreak.model_eval import roi

        with pytest.raises(ValueError, match="finite"):
            roi(stakes=[math.inf, 1.0], profits=[0.5, 0.5])


# ---------- calibration_curve ----------


class TestCalibrationCurve:
    def test_bins_partition_inputs(self) -> None:
        from fastbreak.model_eval import calibration_curve

        probs = [0.05, 0.15, 0.95, 0.96]
        outcomes = [0, 0, 1, 1]
        bins = calibration_curve(probs, outcomes, n_bins=10)
        # Total count across populated bins equals the number of inputs.
        assert sum(b.count for b in bins) == len(probs)

    def test_perfect_calibration(self) -> None:
        from fastbreak.model_eval import calibration_curve

        # All preds at 1.0 with all-positive outcomes -> mean_outcome 1.0.
        bins = calibration_curve([0.95, 0.96, 0.99], [1, 1, 1], n_bins=10)
        populated = [b for b in bins if b.count > 0]
        assert len(populated) == 1
        assert populated[0].mean_outcome == pytest.approx(1.0)

    def test_rejects_bad_n_bins(self) -> None:
        from fastbreak.model_eval import calibration_curve

        with pytest.raises(ValueError, match="n_bins"):
            calibration_curve([0.5], [1], n_bins=0)

    def test_rejects_length_mismatch(self) -> None:
        from fastbreak.model_eval import calibration_curve

        with pytest.raises(ValueError, match="length"):
            calibration_curve([0.5, 0.5], [1], n_bins=10)

    def test_bin_is_frozen(self) -> None:
        from dataclasses import FrozenInstanceError

        from fastbreak.model_eval import calibration_curve

        bins = calibration_curve([0.5], [1], n_bins=10)
        populated = next(b for b in bins if b.count > 0)
        with pytest.raises(FrozenInstanceError):
            populated.count = 99  # type: ignore[misc]


@given(
    data=st.lists(
        st.tuples(
            st.floats(min_value=0.0, max_value=1.0),
            st.integers(min_value=0, max_value=1),
        ),
        min_size=1,
        max_size=80,
    ),
    n_bins=st.integers(min_value=1, max_value=20),
)
@settings(max_examples=300)
def test_calibration_counts_sum_to_input_length(
    data: list[tuple[float, int]], n_bins: int
) -> None:
    """Every input point lands in exactly one bin."""
    from fastbreak.model_eval import calibration_curve

    probs = [p for p, _ in data]
    outcomes = [y for _, y in data]
    bins = calibration_curve(probs, outcomes, n_bins=n_bins)
    assert sum(b.count for b in bins) == len(probs)
