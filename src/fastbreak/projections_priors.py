"""Empirical Bayes priors for fastbreak.projections.

This file is data, not logic. Regenerate via:
    uv run python scripts/compute_projection_priors.py

Do not edit by hand — changes here will be overwritten.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True, slots=True)
class StatPrior:
    """Empirical Bayes prior for one stat."""

    tau_sq: float
    sigma_sq: float
    season: str
    n_players: int
    n_games: int

    def __post_init__(self) -> None:
        # Catch corruption at import time rather than at projection time:
        # NaN/inf would silently propagate through empirical_bayes_blend, and
        # zero/negative variance would degenerate the shrinkage to season_mean.
        for name, val in (("tau_sq", self.tau_sq), ("sigma_sq", self.sigma_sq)):
            if not math.isfinite(val) or val <= 0:
                msg = f"{name} must be finite and positive, got {val!r}"
                raise ValueError(msg)
        if self.n_players < 1:
            msg = f"n_players must be >= 1, got {self.n_players}"
            raise ValueError(msg)
        if self.n_games < 1:
            msg = f"n_games must be >= 1, got {self.n_games}"
            raise ValueError(msg)
        if not self.season:
            msg = "season must be a non-empty string"
            raise ValueError(msg)


STAT_PRIORS: dict[Literal["pts", "reb", "ast", "fg3m"], StatPrior] = {
    "pts": StatPrior(
        tau_sq=36.115600,
        sigma_sq=39.822400,
        season="2025-26",
        n_players=335,
        n_games=20785,
    ),
    "reb": StatPrior(
        tau_sq=4.664300,
        sigma_sq=6.348300,
        season="2025-26",
        n_players=335,
        n_games=20785,
    ),
    "ast": StatPrior(
        tau_sq=3.240300,
        sigma_sq=3.709200,
        season="2025-26",
        n_players=335,
        n_games=20785,
    ),
    "fg3m": StatPrior(
        tau_sq=0.731000,
        sigma_sq=1.680200,
        season="2025-26",
        n_players=335,
        n_games=20785,
    ),
}
