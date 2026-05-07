"""Empirical Bayes priors for fastbreak.projections.

This file is data, not logic. Regenerate via:
    uv run python scripts/compute_projection_priors.py

Do not edit by hand — changes here will be overwritten.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class StatPrior:
    """Empirical Bayes prior for one stat."""

    tau_sq: float
    sigma_sq: float
    season: str
    n_players: int
    n_games: int


STAT_PRIORS: dict[str, StatPrior] = {
    "pts": StatPrior(
        tau_sq=36.1156, sigma_sq=39.8224, season="2025-26", n_players=335, n_games=20785
    ),
    "reb": StatPrior(
        tau_sq=4.6643, sigma_sq=6.3483, season="2025-26", n_players=335, n_games=20785
    ),
    "ast": StatPrior(
        tau_sq=3.2403, sigma_sq=3.7092, season="2025-26", n_players=335, n_games=20785
    ),
    "fg3m": StatPrior(
        tau_sq=0.7310, sigma_sq=1.6802, season="2025-26", n_players=335, n_games=20785
    ),
}
