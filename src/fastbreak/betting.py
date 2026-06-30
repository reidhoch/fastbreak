"""Betting and odds math for the NBA Stats API toolkit.

Pure functions for converting between odds formats, removing the bookmaker
vig, sizing bets (Kelly), measuring closing-line value, and translating
between point spreads and win probabilities.  No scipy dependency — the
normal CDF reuses ``projections.normal_sf`` (stdlib ``math.erfc``) and the
inverse normal uses the Acklam rational approximation.

All functions validate at the boundary and raise ``ValueError`` on invalid
input rather than silently degrading.

Examples::

    from fastbreak.betting import american_to_prob, remove_vig, kelly_fraction

    fair = remove_vig([american_to_prob(-150), american_to_prob(130)])
    stake = kelly_fraction(win_prob=0.58, decimal_odds=1.91, fraction=0.25)
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from fastbreak.projections import normal_sf

if TYPE_CHECKING:
    from collections.abc import Sequence

_DEFAULT_SPREAD_SIGMA = 12.0
_MIN_AMERICAN_MAGNITUDE = 100
_EVEN_MONEY_DECIMAL = 2.0


def american_to_decimal(odds: int) -> float:
    """Convert American (moneyline) odds to decimal odds.

    Raises:
        ValueError: If ``abs(odds) < 100`` (American odds are never between
            -99 and +99, and 0 is invalid).
    """
    if abs(odds) < _MIN_AMERICAN_MAGNITUDE:
        msg = f"American odds must have magnitude >= 100, got {odds!r}"
        raise ValueError(msg)
    if odds > 0:
        return odds / 100.0 + 1.0
    return 100.0 / -odds + 1.0


def decimal_to_american(decimal: float) -> int:
    """Convert decimal odds to American (moneyline) odds.

    Even money (decimal 2.0) maps to +100.

    Raises:
        ValueError: If ``decimal <= 1.0`` (decimal odds always exceed 1).
    """
    if decimal <= 1.0:
        msg = f"decimal odds must be > 1.0, got {decimal!r}"
        raise ValueError(msg)
    if decimal >= _EVEN_MONEY_DECIMAL:
        return round((decimal - 1.0) * 100.0)
    return round(-100.0 / (decimal - 1.0))


def decimal_to_prob(decimal: float) -> float:
    """Implied probability from decimal odds (``1 / decimal``).

    Raises:
        ValueError: If ``decimal <= 1.0``.
    """
    if decimal <= 1.0:
        msg = f"decimal odds must be > 1.0, got {decimal!r}"
        raise ValueError(msg)
    return 1.0 / decimal


def american_to_prob(odds: int) -> float:
    """Implied probability from American (moneyline) odds.

    Raises:
        ValueError: If ``abs(odds) < 100``.
    """
    return decimal_to_prob(american_to_decimal(odds))


def remove_vig(probs: Sequence[float]) -> list[float]:
    """Strip the bookmaker margin: normalize implied probabilities to sum 1.

    Preserves the relative ratios between outcomes (the standard
    "multiplicative" no-vig method).

    Raises:
        ValueError: If ``probs`` is empty, contains a non-finite or
            out-of-[0, 1] value, or sums to a non-positive value.
    """
    if len(probs) == 0:
        msg = "remove_vig requires at least one probability"
        raise ValueError(msg)
    for i, p in enumerate(probs):
        _check_prob(p, f"probs[{i}]")
    total = math.fsum(probs)
    if total <= 0:
        msg = f"implied probabilities must sum to a positive value, got {total!r}"
        raise ValueError(msg)
    return [p / total for p in probs]


def bet_ev(*, win_prob: float, decimal_odds: float) -> float:
    """Expected value per unit staked for a bet at ``decimal_odds``.

    ``ev = win_prob * (decimal_odds - 1) - (1 - win_prob)``.  Zero means a
    fair bet; positive means +EV.

    Raises:
        ValueError: If ``win_prob`` is outside [0, 1] or ``decimal_odds <= 1``.
    """
    _check_prob(win_prob, "win_prob")
    if decimal_odds <= 1.0:
        msg = f"decimal_odds must be > 1.0, got {decimal_odds!r}"
        raise ValueError(msg)
    b = decimal_odds - 1.0
    return win_prob * b - (1.0 - win_prob)


def kelly_fraction(
    *, win_prob: float, decimal_odds: float, fraction: float = 1.0
) -> float:
    """Kelly-optimal stake as a fraction of bankroll.

    ``f* = (win_prob * b - (1 - win_prob)) / b`` where ``b = decimal_odds - 1``.
    Negative-edge bets clamp to ``0.0`` (never bet against yourself).  Pass
    ``fraction`` < 1 for fractional Kelly (e.g. 0.25 for quarter-Kelly).

    Raises:
        ValueError: If ``win_prob`` is outside [0, 1], ``decimal_odds <= 1``,
            or ``fraction`` is not in (0, 1].
    """
    _check_prob(win_prob, "win_prob")
    if decimal_odds <= 1.0:
        msg = f"decimal_odds must be > 1.0, got {decimal_odds!r}"
        raise ValueError(msg)
    if not (0.0 < fraction <= 1.0):
        msg = f"fraction must be in (0, 1], got {fraction!r}"
        raise ValueError(msg)
    b = decimal_odds - 1.0
    edge = win_prob * b - (1.0 - win_prob)
    if edge <= 0.0:
        return 0.0
    return (edge / b) * fraction


def closing_line_value(*, bet_decimal: float, closing_decimal: float) -> float:
    """Closing-line value: fractional edge of your price over the close.

    ``clv = bet_decimal / closing_decimal - 1``.  Positive means you beat
    the closing line.

    Raises:
        ValueError: If either price is <= 1.0.
    """
    if bet_decimal <= 1.0:
        msg = f"bet_decimal must be > 1.0, got {bet_decimal!r}"
        raise ValueError(msg)
    if closing_decimal <= 1.0:
        msg = f"closing_decimal must be > 1.0, got {closing_decimal!r}"
        raise ValueError(msg)
    return bet_decimal / closing_decimal - 1.0


def spread_to_win_prob(spread: float, *, sigma: float = _DEFAULT_SPREAD_SIGMA) -> float:
    """Win probability implied by a point spread.

    ``spread`` is from the team's perspective: negative = favored.  Models
    the final margin as Normal(-spread, sigma) and returns P(margin > 0).

    Raises:
        ValueError: If ``sigma`` is not a finite positive number.
    """
    if not math.isfinite(sigma) or sigma <= 0:
        msg = f"sigma must be a finite positive number, got {sigma!r}"
        raise ValueError(msg)
    # Expected margin is -spread; P(win) = P(margin > 0) = sf(0; mean=-spread).
    return normal_sf(x=0.0, mean=-spread, stdev=sigma)


def win_prob_to_spread(
    win_prob: float, *, sigma: float = _DEFAULT_SPREAD_SIGMA
) -> float:
    """Point spread implied by a win probability (inverse of spread_to_win_prob).

    Raises:
        ValueError: If ``win_prob`` is not strictly in (0, 1) or ``sigma`` is
            not a finite positive number.
    """
    if not (0.0 < win_prob < 1.0):
        msg = f"win_prob must be strictly in (0, 1), got {win_prob!r}"
        raise ValueError(msg)
    if not math.isfinite(sigma) or sigma <= 0:
        msg = f"sigma must be a finite positive number, got {sigma!r}"
        raise ValueError(msg)
    # mean margin = sigma * Φ⁻¹(win_prob); spread = -mean.
    return -sigma * _inv_norm_cdf(win_prob)


def log5(p_a: float, p_b: float) -> float:
    """Bill James log5: P(A beats B) from each team's win rate vs the league.

    ``(p_a - p_a*p_b) / (p_a + p_b - 2*p_a*p_b)``.

    Raises:
        ValueError: If either rate is outside [0, 1] or the matchup is
            degenerate (denominator zero, e.g. both 0 or both 1).
    """
    _check_prob(p_a, "p_a")
    _check_prob(p_b, "p_b")
    denom = p_a + p_b - 2.0 * p_a * p_b
    if denom == 0.0:
        msg = f"degenerate log5 matchup (denominator 0) for {p_a!r}, {p_b!r}"
        raise ValueError(msg)
    return (p_a - p_a * p_b) / denom


def _check_prob(value: float, name: str) -> None:
    if not math.isfinite(value) or not (0.0 <= value <= 1.0):
        msg = f"{name} must be a finite probability in [0, 1], got {value!r}"
        raise ValueError(msg)


# Acklam's rational approximation to the inverse normal CDF (|error| < 1.15e-9).
_ACKLAM_A = (
    -3.969683028665376e01,
    2.209460984245205e02,
    -2.759285104469687e02,
    1.383577518672690e02,
    -3.066479806614716e01,
    2.506628277459239e00,
)
_ACKLAM_B = (
    -5.447609879822406e01,
    1.615858368580409e02,
    -1.556989798598866e02,
    6.680131188771972e01,
    -1.328068155288572e01,
)
_ACKLAM_C = (
    -7.784894002430293e-03,
    -3.223964580411365e-01,
    -2.400758277161838e00,
    -2.549732539343734e00,
    4.374664141464968e00,
    2.938163982698783e00,
)
_ACKLAM_D = (
    7.784695709041462e-03,
    3.224671290700398e-01,
    2.445134137142996e00,
    3.754408661907416e00,
)
_ACKLAM_LOW = 0.02425
_ACKLAM_HIGH = 1.0 - _ACKLAM_LOW


def _inv_norm_cdf(p: float) -> float:
    """Inverse standard normal CDF Φ⁻¹(p) for p in (0, 1), no scipy."""
    if p < _ACKLAM_LOW:
        q = math.sqrt(-2.0 * math.log(p))
        return (
            (
                (
                    ((_ACKLAM_C[0] * q + _ACKLAM_C[1]) * q + _ACKLAM_C[2]) * q
                    + _ACKLAM_C[3]
                )
                * q
                + _ACKLAM_C[4]
            )
            * q
            + _ACKLAM_C[5]
        ) / (
            (((_ACKLAM_D[0] * q + _ACKLAM_D[1]) * q + _ACKLAM_D[2]) * q + _ACKLAM_D[3])
            * q
            + 1.0
        )
    if p <= _ACKLAM_HIGH:
        q = p - 0.5
        r = q * q
        return (
            (
                (
                    (
                        ((_ACKLAM_A[0] * r + _ACKLAM_A[1]) * r + _ACKLAM_A[2]) * r
                        + _ACKLAM_A[3]
                    )
                    * r
                    + _ACKLAM_A[4]
                )
                * r
                + _ACKLAM_A[5]
            )
            * q
        ) / (
            (
                (
                    ((_ACKLAM_B[0] * r + _ACKLAM_B[1]) * r + _ACKLAM_B[2]) * r
                    + _ACKLAM_B[3]
                )
                * r
                + _ACKLAM_B[4]
            )
            * r
            + 1.0
        )
    q = math.sqrt(-2.0 * math.log(1.0 - p))
    return -(
        (
            (((_ACKLAM_C[0] * q + _ACKLAM_C[1]) * q + _ACKLAM_C[2]) * q + _ACKLAM_C[3])
            * q
            + _ACKLAM_C[4]
        )
        * q
        + _ACKLAM_C[5]
    ) / (
        (((_ACKLAM_D[0] * q + _ACKLAM_D[1]) * q + _ACKLAM_D[2]) * q + _ACKLAM_D[3]) * q
        + 1.0
    )
