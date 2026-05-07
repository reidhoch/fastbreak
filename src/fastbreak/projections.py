"""Player projection module.

Produces per-stat projections (pts, reb, ast, fg3m) plus P(over line)
probabilities for a player against an explicitly specified upcoming opponent.
Uses heuristic Empirical Bayes shrinkage — no ML training, no scipy dependency.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Literal, cast

from fastbreak.projections_priors import STAT_PRIORS

if TYPE_CHECKING:
    from collections.abc import Sequence
    from datetime import date

    from fastbreak.clients.nba import NBAClient
    from fastbreak.models.player_game_log import (
        PlayerGameLogEntry,
        PlayerGameLogResponse,
    )
    from fastbreak.models.team_estimated_metrics import TeamEstimatedMetricsResponse

ProjectionStat = Literal["pts", "reb", "ast", "fg3m"]
DistributionFamily = Literal["normal", "poisson"]

STATS: tuple[ProjectionStat, ...] = ("pts", "reb", "ast", "fg3m")


@dataclass(frozen=True, slots=True)
class StatProjection:
    """One stat's projected value for a single player in a single game."""

    stat: ProjectionStat
    mean: float
    stdev: float
    distribution: DistributionFamily
    rolling_n: int
    season_mean: float
    rolling_mean: float
    adjustments: dict[str, float] = field(default_factory=dict)

    def prob_over(self, line: float) -> float:
        """P(realized stat > ``line``) under ``self.distribution``."""
        if self.distribution == "normal":
            return normal_sf(x=line, mean=self.mean, stdev=self.stdev)
        if self.distribution == "poisson":
            return poisson_sf(line=line, lam=self.mean)
        msg = f"Unsupported distribution: {self.distribution!r}"
        raise ValueError(msg)


@dataclass(frozen=True, slots=True)
class PlayerProjection:
    """A complete projection for one player in one upcoming game."""

    player_id: int
    player_name: str
    opponent_team_id: int
    game_date: date
    is_home: bool
    stats: dict[ProjectionStat, StatProjection] = field(default_factory=dict)


def empirical_bayes_blend(
    rolling_mean: float,
    season_mean: float,
    *,
    n: int,
    tau_sq: float,
    sigma_sq: float,
) -> float:
    """Blend a player's rolling mean toward their season mean via James-Stein shrinkage.

    w = tau_sq / (tau_sq + sigma_sq / n)
    blended = w * rolling_mean + (1 - w) * season_mean

    Args:
        rolling_mean: Mean of the player's last ``n`` games.
        season_mean: Mean across the player's season (the prior anchor).
        n: Number of recent games the rolling mean averaged.
        tau_sq: Between-player variance of season means (the prior width).
        sigma_sq: Within-player game-to-game variance (observation noise).

    Returns:
        Blended mean in the closed interval between ``rolling_mean`` and
        ``season_mean``.
    """
    if n <= 0:
        msg = "n must be positive"
        raise ValueError(msg)
    if tau_sq < 0 or sigma_sq < 0:
        msg = "variance values must be non-negative"
        raise ValueError(msg)
    if sigma_sq == 0:
        # No observation noise: the MLE is the rolling mean.
        return rolling_mean
    if tau_sq == 0:
        # Degenerate prior (zero between-player variance = infinitely strong
        # prior at the season anchor); the weak-prior limit is tau_sq -> inf.
        return season_mean
    denom = tau_sq + sigma_sq / n
    if denom == 0:
        # Subnormal underflow (sigma_sq / n rounds to 0 while tau_sq is 0).
        # Both paths above should have caught this, but guard defensively.
        return season_mean
    weight = tau_sq / denom
    return weight * rolling_mean + (1.0 - weight) * season_mean


def normal_sf(*, x: float, mean: float, stdev: float) -> float:
    """Survival function P(X > x) for X ~ Normal(mean, stdev²).

    Uses math.erfc from stdlib; no scipy dependency.
    """
    if stdev <= 0:
        msg = "stdev must be positive"
        raise ValueError(msg)
    z = (x - mean) / (stdev * math.sqrt(2.0))
    return 0.5 * math.erfc(z)


_POISSON_TAIL_EPS = 1e-18


def poisson_sf(*, line: float, lam: float) -> float:
    """Survival function P(X > floor(line)) for X ~ Poisson(lam).

    ``line`` may be fractional (e.g. a sportsbook line of 2.5 threes);
    the result equals ``P(X >= ceil(line)) = P(X > floor(line))`` for
    non-integer lines, and the standard strict-inequality survival for
    integer lines.
    """
    if lam < 0:
        msg = "lam must be non-negative"
        raise ValueError(msg)
    if line < 0:
        return 1.0
    if lam == 0:
        # All mass at 0; P(X > k) is 0 for k >= 0.
        return 0.0
    k = math.floor(line)
    # P(X <= k) = sum_{i=0}^{k} e^{-lam} * lam^i / i!
    # Compute iteratively to avoid overflow for moderate lambda.
    # For typical NBA stat lines k is small (< ~30), so the sum is stable.
    # Past i=lam the terms shrink monotonically; break once they add no
    # more information so extreme lines (e.g. k=1000) don't iterate
    # thousands of times past the tail.
    term = math.exp(-lam)
    cdf = term
    for i in range(1, k + 1):
        term *= lam / i
        cdf += term
        if i > lam and term < _POISSON_TAIL_EPS:
            break
    return max(0.0, min(1.0, 1.0 - cdf))


_OPP_MAX_FRACTION = 0.15
_REST_B2B_FRACTION = -0.04
_REST_3PLUS_FRACTION = 0.015
_HOME_FRACTION = 0.02


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def adjust_for_opponent(
    *,
    blended_mean: float,
    stat: ProjectionStat,
    opp_def_rating: float,
    league_avg_def_rating: float,
) -> float:
    """Additive adjustment for opposing defense strength.

    Only applied to scoring stats (pts, fg3m). Rebounds and assists are
    driven primarily by pace and role, not raw defensive rating, so we
    leave them at zero for v1.

    The delta is a fraction of the blended mean, clamped at ±15%.
    """
    if stat not in ("pts", "fg3m"):
        return 0.0
    if league_avg_def_rating == 0:
        return 0.0
    # opp_def_rating HIGHER than league avg = worse defense = positive delta.
    raw_fraction = (opp_def_rating - league_avg_def_rating) / league_avg_def_rating
    fraction = _clamp(raw_fraction, -_OPP_MAX_FRACTION, _OPP_MAX_FRACTION)
    return blended_mean * fraction


def adjust_for_rest(
    *, blended_mean: float, stat: ProjectionStat, days_rest: int
) -> float:
    """Additive adjustment for days of rest before the game.

    0 days rest (back-to-back): small negative.
    1 day rest (normal): 0.
    2 days rest: 0.
    3+ days rest: small positive.
    """
    if days_rest == 0:
        fraction = _REST_B2B_FRACTION
    elif days_rest >= 3:  # noqa: PLR2004 — 3+ days rest is the recovery threshold
        fraction = _REST_3PLUS_FRACTION
    else:
        fraction = 0.0
    # Assists are least affected by fatigue; scale down.
    if stat == "ast":
        fraction *= 0.5
    return blended_mean * fraction


def adjust_for_home(
    *, blended_mean: float, stat: ProjectionStat, is_home: bool
) -> float:
    """Small additive home/away adjustment (~±2%)."""
    # `stat` is reserved for future per-stat scaling; for v1 every stat gets the same bonus.
    del stat
    sign = 1.0 if is_home else -1.0
    return blended_mean * _HOME_FRACTION * sign


_STAT_DISTRIBUTION: dict[ProjectionStat, DistributionFamily] = {
    "pts": "normal",
    "reb": "normal",
    "ast": "normal",
    "fg3m": "poisson",
}
_STDEV_FLOORS: dict[ProjectionStat, float] = {
    "pts": 3.0,
    "reb": 1.5,
    "ast": 1.5,
    "fg3m": 0.8,
}


def _mean(values: Sequence[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _variance(values: Sequence[float]) -> float:
    if len(values) < 2:  # noqa: PLR2004 — sample variance needs >= 2 observations
        return 0.0
    m = _mean(values)
    return sum((v - m) ** 2 for v in values) / (len(values) - 1)


def _build_stat_projection(  # noqa: PLR0913
    stat: ProjectionStat,
    games: Sequence[PlayerGameLogEntry],
    *,
    rolling_n: int,
    opp_def_rating: float,
    league_avg_def_rating: float,
    days_rest: int,
    is_home: bool,
) -> StatProjection:
    """Build a single-stat projection from a player's game log and context."""
    values = [float(getattr(g, stat)) for g in games]
    season_mean = _mean(values)
    # PlayerGameLog response returns games newest-first; leave in that order.
    recent = values[:rolling_n]
    rolling_mean = _mean(recent) if recent else season_mean
    prior = STAT_PRIORS[stat]
    blended = empirical_bayes_blend(
        rolling_mean=rolling_mean,
        season_mean=season_mean,
        n=max(1, len(recent)),
        tau_sq=prior.tau_sq,
        sigma_sq=prior.sigma_sq,
    )
    opp_delta = adjust_for_opponent(
        blended_mean=blended,
        stat=stat,
        opp_def_rating=opp_def_rating,
        league_avg_def_rating=league_avg_def_rating,
    )
    rest_delta = adjust_for_rest(blended_mean=blended, stat=stat, days_rest=days_rest)
    home_delta = adjust_for_home(blended_mean=blended, stat=stat, is_home=is_home)
    # Floor at 0 to avoid negative projections.
    mean = max(0.0, blended + opp_delta + rest_delta + home_delta)
    distribution = _STAT_DISTRIBUTION[stat]
    if distribution == "poisson":
        # Poisson: variance = lambda.
        stdev = math.sqrt(max(mean, 1e-6))
    else:
        # Residual variance of recent games, floored to prevent over-confidence.
        stdev = max(math.sqrt(_variance(recent)), _STDEV_FLOORS[stat])
    return StatProjection(
        stat=stat,
        mean=mean,
        stdev=stdev,
        distribution=distribution,
        rolling_n=len(recent),
        season_mean=season_mean,
        rolling_mean=rolling_mean,
        adjustments={"opponent": opp_delta, "rest": rest_delta, "home": home_delta},
    )


async def project_player(  # noqa: PLR0913
    client: NBAClient,
    *,
    player_id: int,
    player_name: str,
    opponent_team_id: int,
    is_home: bool,
    game_date: date,
    season: str,
    days_rest: int,
    rolling_n: int = 10,
    stats: Sequence[ProjectionStat] = STATS,
) -> PlayerProjection:
    """Project a player's stat line for an upcoming game against a given opponent.

    Concurrently fetches the player's season game log and league-wide team
    estimated metrics, then blends each stat's rolling form with the player's
    season mean via empirical Bayes shrinkage, and applies opponent/rest/home
    adjustments.

    Args:
        client: NBA API client.
        player_id: NBA player ID.
        player_name: Display name (pass-through to the result).
        opponent_team_id: NBA team ID of the upcoming opponent.
        is_home: True if the projected game is at home for the player.
        game_date: The date of the projected game.
        season: Season in YYYY-YY format (e.g. "2025-26").
        days_rest: Days of rest before the game (0 = back-to-back).
        rolling_n: Number of most-recent games for the rolling mean.
        stats: Stats to project (defaults to all four in ``STATS``).

    Returns:
        A ``PlayerProjection`` populated with one ``StatProjection`` per stat.

    Raises:
        ValueError: If ``rolling_n < 1``, the player has no logged games, or
            the opponent team is missing / lacks an estimated defensive rating.
    """
    if rolling_n < 1:
        msg = f"rolling_n must be >= 1, got {rolling_n}"
        raise ValueError(msg)
    from fastbreak.endpoints import PlayerGameLog, TeamEstimatedMetrics  # noqa: PLC0415

    results: list[Any] = await client.get_many(
        [
            PlayerGameLog(player_id=player_id, season=season),
            TeamEstimatedMetrics(season=season),
        ],
        max_concurrency=2,
    )
    log_resp = cast("PlayerGameLogResponse", results[0])
    team_resp = cast("TeamEstimatedMetricsResponse", results[1])
    if not log_resp.games:
        msg = f"No games found for player_id={player_id} in season {season}"
        raise ValueError(msg)
    try:
        opp = next(t for t in team_resp.teams if t.team_id == opponent_team_id)
    except StopIteration as exc:
        msg = f"Opponent team_id={opponent_team_id} not found in team estimated metrics"
        raise ValueError(msg) from exc
    if opp.e_def_rating is None:
        msg = f"Opponent team_id={opponent_team_id} is missing e_def_rating"
        raise ValueError(msg)
    league_avg_def = _mean(
        [t.e_def_rating for t in team_resp.teams if t.e_def_rating is not None]
    )
    projections: dict[ProjectionStat, StatProjection] = {
        stat: _build_stat_projection(
            stat,
            log_resp.games,
            rolling_n=rolling_n,
            opp_def_rating=opp.e_def_rating,
            league_avg_def_rating=league_avg_def,
            days_rest=days_rest,
            is_home=is_home,
        )
        for stat in stats
    }
    return PlayerProjection(
        player_id=player_id,
        player_name=player_name,
        opponent_team_id=opponent_team_id,
        game_date=game_date,
        is_home=is_home,
        stats=projections,
    )
