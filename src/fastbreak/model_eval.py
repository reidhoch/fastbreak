"""Probabilistic forecast scoring and calibration for the betting pipeline.

Pure functions for evaluating win-probability / prop predictions against
realized outcomes: Brier score, log loss, realized ROI, and a reliability
(calibration) curve.  These take prediction/outcome arrays rather than
box-score inputs, so they live apart from ``metrics`` and ``betting``.

All functions validate at the boundary and raise ``ValueError`` on invalid
input rather than silently degrading.

Examples::

    from fastbreak.model_eval import brier_score, log_loss, roi

    bs = brier_score(model_probs, outcomes)
    ll = log_loss(model_probs, outcomes)
    realized = roi(stakes=stakes, profits=profits)
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

_LOG_LOSS_EPS = 1e-15
_LOG_LOSS_MAX_EPS = 0.5


@dataclass(frozen=True, slots=True)
class CalibrationBin:
    """One bucket of a reliability curve.

    Attributes:
        lower: Inclusive lower edge of the predicted-probability bin.
        upper: Upper edge of the bin (inclusive only for the final bin).
        mean_pred: Mean predicted probability of points in the bin.
        mean_outcome: Observed hit rate (mean outcome) of points in the bin.
        count: Number of predictions that fell in the bin.
    """

    lower: float
    upper: float
    mean_pred: float
    mean_outcome: float
    count: int


def _validate_pairs(probs: Sequence[float], outcomes: Sequence[int]) -> None:
    if len(probs) != len(outcomes):
        msg = f"probs and outcomes must have equal length, got {len(probs)} and {len(outcomes)}"
        raise ValueError(msg)
    if len(probs) == 0:
        msg = "probs and outcomes must not be empty"
        raise ValueError(msg)
    for p in probs:
        if not math.isfinite(p) or not (0.0 <= p <= 1.0):
            msg = f"probabilities must be finite values in [0, 1], got {p!r}"
            raise ValueError(msg)
    for y in outcomes:
        if y not in (0, 1):
            msg = f"outcomes must be 0 or 1, got {y!r}"
            raise ValueError(msg)


def brier_score(probs: Sequence[float], outcomes: Sequence[int]) -> float:
    """Mean squared error between predicted probabilities and outcomes.

    ``mean((p_i - y_i)²)``.  Ranges [0, 1]; lower is better.  A constant 0.5
    forecaster scores 0.25.

    Raises:
        ValueError: On length mismatch, empty input, probabilities outside
            [0, 1], or outcomes not in {0, 1}.
    """
    _validate_pairs(probs, outcomes)
    return math.fsum((p - y) ** 2 for p, y in zip(probs, outcomes, strict=True)) / len(
        probs
    )


def log_loss(
    probs: Sequence[float], outcomes: Sequence[int], *, eps: float = _LOG_LOSS_EPS
) -> float:
    """Mean binary cross-entropy (negative log likelihood).

    ``-mean(y*ln p + (1-y)*ln(1-p))``.  Predictions are clipped to
    ``[eps, 1-eps]`` so a confidently-wrong p=0/1 yields a large finite loss
    rather than infinity.  Lower is better.

    Raises:
        ValueError: On length mismatch, empty input, probabilities outside
            [0, 1], outcomes not in {0, 1}, or ``eps`` outside (0, 0.5).
    """
    if not math.isfinite(eps) or not (0.0 < eps < _LOG_LOSS_MAX_EPS):
        msg = f"eps must be a finite value in (0, {_LOG_LOSS_MAX_EPS}), got {eps!r}"
        raise ValueError(msg)
    _validate_pairs(probs, outcomes)
    total = 0.0
    for p, y in zip(probs, outcomes, strict=True):
        clipped = min(max(p, eps), 1.0 - eps)
        total += -(y * math.log(clipped) + (1 - y) * math.log(1.0 - clipped))
    return total / len(probs)


def roi(*, stakes: Sequence[float], profits: Sequence[float]) -> float:
    """Realized return on investment: total profit divided by total staked.

    ``sum(profits) / sum(stakes)``.  ``profits`` are net (positive for a win,
    negative for a loss), in the same units as ``stakes``.

    Raises:
        ValueError: On length mismatch or non-positive total stake.
    """
    if len(stakes) != len(profits):
        msg = f"stakes and profits must have equal length, got {len(stakes)} and {len(profits)}"
        raise ValueError(msg)
    total_stake = math.fsum(stakes)
    if total_stake <= 0:
        msg = f"total stake must be positive, got {total_stake!r}"
        raise ValueError(msg)
    return math.fsum(profits) / total_stake


def calibration_curve(
    probs: Sequence[float], outcomes: Sequence[int], *, n_bins: int = 10
) -> list[CalibrationBin]:
    """Bucket predictions into ``n_bins`` equal-width bins over [0, 1].

    Returns one CalibrationBin per populated bin (empty bins are omitted),
    ordered from lowest to highest probability.  Compare ``mean_pred`` to
    ``mean_outcome`` per bin to assess calibration.

    Raises:
        ValueError: On length mismatch, empty input, probabilities outside
            [0, 1], outcomes not in {0, 1}, or ``n_bins < 1``.
    """
    _validate_pairs(probs, outcomes)
    if n_bins < 1:
        msg = f"n_bins must be >= 1, got {n_bins!r}"
        raise ValueError(msg)

    width = 1.0 / n_bins
    sum_pred = [0.0] * n_bins
    sum_outcome = [0.0] * n_bins
    counts = [0] * n_bins

    for p, y in zip(probs, outcomes, strict=True):
        # p == 1.0 maps to the final bin (idx n_bins) without this clamp.
        idx = min(int(p / width), n_bins - 1)
        sum_pred[idx] += p
        sum_outcome[idx] += y
        counts[idx] += 1

    bins: list[CalibrationBin] = []
    for i in range(n_bins):
        if counts[i] == 0:
            continue
        bins.append(
            CalibrationBin(
                lower=i * width,
                upper=(i + 1) * width,
                mean_pred=sum_pred[i] / counts[i],
                mean_outcome=sum_outcome[i] / counts[i],
                count=counts[i],
            )
        )
    return bins
