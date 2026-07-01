"""Regularized Adjusted Plus-Minus (RAPM).

Pure solver: callers supply stints (the +1 side, the -1 side, possessions and
score margin); this module builds a sparse player x stint design matrix and
solves a possession-weighted ridge regression. See
docs/superpowers/specs/2026-06-30-rapm-design.md.
"""

import math
from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np
from scipy.sparse import csr_matrix
from sklearn.linear_model import Ridge, RidgeCV


@dataclass(frozen=True, slots=True)
class Stint:
    """One stretch of play with a constant set of on-court players.

    ``home_player_ids`` is the ``+1`` side and ``away_player_ids`` the ``-1``
    side; ``point_diff`` is the score margin of the ``+1`` side over the stint;
    ``possessions`` (> 0) weights and normalizes the stint. "home"/"away" are
    sign labels, not venue.
    """

    home_player_ids: tuple[int, ...]
    away_player_ids: tuple[int, ...]
    possessions: float
    point_diff: int


def build_design_matrix(
    stints: Sequence[Stint],
) -> tuple[csr_matrix, np.ndarray, np.ndarray, list[int]]:
    """Return ``(X, y, sample_weight, player_ids)`` for the ridge solve."""
    player_ids = sorted(
        {pid for s in stints for pid in (*s.home_player_ids, *s.away_player_ids)}
    )
    col = {pid: i for i, pid in enumerate(player_ids)}

    rows: list[int] = []
    cols: list[int] = []
    vals: list[float] = []
    y = np.empty(len(stints), dtype=float)
    w = np.empty(len(stints), dtype=float)

    for r, s in enumerate(stints):
        for pid in s.home_player_ids:
            rows.append(r)
            cols.append(col[pid])
            vals.append(1.0)
        for pid in s.away_player_ids:
            rows.append(r)
            cols.append(col[pid])
            vals.append(-1.0)
        y[r] = s.point_diff / s.possessions * 100.0
        w[r] = s.possessions

    x = csr_matrix(
        (vals, (rows, cols)),
        shape=(len(stints), len(player_ids)),
        dtype=float,
    )
    return x, y, w, player_ids


@dataclass(frozen=True, slots=True)
class RAPMRating:
    """A single player's RAPM (net points per 100 possessions)."""

    player_id: int
    rapm: float
    stint_count: int
    possessions: float


@dataclass(frozen=True, slots=True)
class RAPMResult:
    """Result of a RAPM solve."""

    ratings: tuple[RAPMRating, ...]
    alpha: float
    intercept: float
    n_stints: int
    n_players: int

    def rating_for(self, player_id: int) -> RAPMRating | None:
        for r in self.ratings:
            if r.player_id == player_id:
                return r
        return None


def _validate_stints(stints: Sequence[Stint]) -> None:
    for i, s in enumerate(stints):
        if not math.isfinite(s.possessions):
            msg = f"stint {i} has non-finite possessions ({s.possessions}); must be finite"
            raise ValueError(msg)
        if s.possessions <= 0:
            msg = (
                f"stint {i} has non-positive possessions ({s.possessions}); must be > 0"
            )
            raise ValueError(msg)
        if not math.isfinite(float(s.point_diff)):
            msg = (
                f"stint {i} has non-finite point_diff ({s.point_diff}); must be finite"
            )
            raise ValueError(msg)


def _player_accounting(
    stints: Sequence[Stint], player_ids: list[int]
) -> tuple[dict[int, int], dict[int, float]]:
    counts = dict.fromkeys(player_ids, 0)
    poss = dict.fromkeys(player_ids, 0.0)
    for s in stints:
        for pid in (*s.home_player_ids, *s.away_player_ids):
            counts[pid] += 1
            poss[pid] += s.possessions
    return counts, poss


def compute_rapm(
    stints: Sequence[Stint],
    *,
    lambda_: float = 3000.0,
    alphas: Sequence[float] | None = None,
) -> RAPMResult:
    """Estimate single-combined RAPM via possession-weighted ridge regression."""
    if not stints:
        return RAPMResult(
            ratings=(), alpha=lambda_, intercept=0.0, n_stints=0, n_players=0
        )

    _validate_stints(stints)

    # Validate lambda_ on the fixed-lambda path (alphas path uses sklearn's validation)
    if alphas is None and (not math.isfinite(lambda_) or lambda_ < 0):
        msg = f"lambda_ must be a non-negative finite number, got {lambda_}"
        raise ValueError(msg)

    x, y, w, player_ids = build_design_matrix(stints)
    counts, poss = _player_accounting(stints, player_ids)

    if alphas is not None:
        if len(alphas) == 0:
            msg = "alphas must be a non-empty sequence when provided"
            raise ValueError(msg)
        cv_model = RidgeCV(alphas=list(alphas), fit_intercept=False)
        cv_model.fit(x, y, sample_weight=w)
        alpha_used = float(np.asarray(cv_model.alpha_))
        coef = np.asarray(cv_model.coef_, dtype=float)
        intercept = float(np.asarray(cv_model.intercept_))
    else:
        model = Ridge(alpha=lambda_, fit_intercept=False)
        model.fit(x, y, sample_weight=w)
        alpha_used = lambda_
        coef = np.asarray(model.coef_, dtype=float)
        intercept = float(np.asarray(model.intercept_))

    ratings = tuple(
        sorted(
            (
                RAPMRating(
                    player_id=pid,
                    rapm=float(coef[i]),
                    stint_count=counts[pid],
                    possessions=poss[pid],
                )
                for i, pid in enumerate(player_ids)
            ),
            key=lambda r: r.rapm,
            reverse=True,
        )
    )
    return RAPMResult(
        ratings=ratings,
        alpha=float(alpha_used),
        intercept=intercept,
        n_stints=len(stints),
        n_players=len(player_ids),
    )


def rapm_leaders(
    result: RAPMResult,
    *,
    top_n: int = 10,
    min_possessions: float = 0.0,
) -> list[RAPMRating]:
    """Top-``top_n`` ratings by RAPM, filtered to ``possessions >= min_possessions``."""
    eligible = [r for r in result.ratings if r.possessions >= min_possessions]
    eligible.sort(key=lambda r: r.rapm, reverse=True)
    return eligible[: max(top_n, 0)]
