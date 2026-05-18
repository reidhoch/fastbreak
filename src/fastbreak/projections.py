"""Player projection module.

Produces per-stat projections (pts, reb, ast, fg3m) plus P(over line)
probabilities for a player against an explicitly specified upcoming opponent.
Uses heuristic Empirical Bayes shrinkage — no ML training, no scipy dependency.
"""

from __future__ import annotations

import math
import statistics
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import TYPE_CHECKING, Any, Final, Literal, cast

from fastbreak.projections_priors import STAT_PRIORS, StatPrior
from fastbreak.seasons import get_season_from_date

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence
    from datetime import date

    from fastbreak.clients.nba import NBAClient
    from fastbreak.models.player_game_log import (
        PlayerGameLogEntry,
        PlayerGameLogResponse,
    )
    from fastbreak.models.team_estimated_metrics import TeamEstimatedMetricsResponse
    from fastbreak.types import Season

ProjectionStat = Literal["pts", "reb", "ast", "fg3m"]
DistributionFamily = Literal["normal", "poisson"]

STATS: Final[tuple[ProjectionStat, ...]] = ("pts", "reb", "ast", "fg3m")


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

    def __post_init__(self) -> None:
        # Reject non-finite numerics at construction so prob_over and
        # downstream consumers never see NaN-poisoned values.
        for name, val in (
            ("mean", self.mean),
            ("season_mean", self.season_mean),
            ("rolling_mean", self.rolling_mean),
        ):
            if not math.isfinite(val):
                msg = f"{name} must be finite, got {val!r}"
                raise ValueError(msg)
        if not math.isfinite(self.stdev) or self.stdev <= 0:
            msg = f"stdev must be a finite positive number, got {self.stdev!r}"
            raise ValueError(msg)
        if self.rolling_n < 0:
            msg = f"rolling_n must be >= 0, got {self.rolling_n}"
            raise ValueError(msg)

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

    def __post_init__(self) -> None:
        if self.player_id < 1:
            msg = f"player_id must be >= 1, got {self.player_id}"
            raise ValueError(msg)
        if self.opponent_team_id < 1:
            msg = f"opponent_team_id must be >= 1, got {self.opponent_team_id}"
            raise ValueError(msg)
        if not self.player_name:
            msg = "player_name must be non-empty"
            raise ValueError(msg)
        for key, sp in self.stats.items():
            if key not in STATS:
                msg = f"unsupported stat key: {key!r}; supported = {list(STATS)}"
                raise ValueError(msg)
            if sp.stat != key:
                # The stats dict is keyed by stat name; mismatched entries
                # (e.g. {"pts": StatProjection(stat="reb", ...)}) would let
                # downstream code lookup "pts" and silently use rebound math.
                msg = f"stats[{key!r}].stat must equal {key!r}, got {sp.stat!r}"
                raise ValueError(msg)


def empirical_bayes_blend(
    rolling_mean: float,
    season_mean: float,
    *,
    n: int,
    tau_sq: float,
    sigma_sq: float,
) -> float:
    """Blend a player's rolling mean toward their season mean via Empirical Bayes shrinkage.

    Implemented as the normal-normal posterior mean (precision-weighted
    average). Inspired by James-Stein shrinkage but distinct: classic JS
    is a minimax estimator on a multivariate mean vector with a different
    closed form; here we compute a scalar posterior mean per stat.

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

    Raises:
        ValueError: If ``n <= 0``; if any of ``rolling_mean``, ``season_mean``,
            ``tau_sq``, ``sigma_sq`` is non-finite (NaN/inf); or if either
            variance is negative.
    """
    # NaN slips past `< 0` and `== 0` comparisons in CPython, so naive guards
    # would silently propagate NaN through the blend. Validate finite first.
    for name, val in (
        ("rolling_mean", rolling_mean),
        ("season_mean", season_mean),
        ("tau_sq", tau_sq),
        ("sigma_sq", sigma_sq),
    ):
        if not math.isfinite(val):
            msg = f"{name} must be finite, got {val!r}"
            raise ValueError(msg)
    if n <= 0:
        msg = "n must be positive"
        raise ValueError(msg)
    if tau_sq < 0 or sigma_sq < 0:
        msg = "variance values must be non-negative"
        raise ValueError(msg)
    if tau_sq == 0:
        # Degenerate prior (zero between-player variance = infinitely strong
        # prior at the season anchor); dominates sigma_sq == 0 when both
        # are zero. The weak-prior limit is tau_sq -> inf.
        return season_mean
    if sigma_sq == 0:
        # No observation noise: the MLE is the rolling mean.
        return rolling_mean
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

    Raises:
        ValueError: If ``stdev`` is not a finite positive number, if
            ``mean`` is non-finite (NaN or ±inf), or if ``x`` is NaN.
            ``x = ±inf`` is allowed and returns the asymptotic limit
            (P=0 for +inf, P=1 for -inf) — useful for sportsbook-style
            tail probabilities at extreme lines.
    """
    # `not (stdev > 0)` rejects NaN (NaN comparisons are False) as well as
    # zero/negative; the explicit isfinite guard also rejects +inf.
    if not math.isfinite(stdev) or stdev <= 0:
        msg = f"stdev must be a finite positive number, got {stdev!r}"
        raise ValueError(msg)
    # mean must be finite: a normal distribution centered at ±inf is
    # nonsensical, and erfc would propagate inf into the z-score.
    if not math.isfinite(mean):
        msg = f"mean must be finite, got {mean!r}"
        raise ValueError(msg)
    # x is allowed to be ±inf (legitimate asymptote for prob_over queries
    # at extreme lines); only NaN is rejected.
    if math.isnan(x):
        msg = f"x must not be NaN, got {x!r}"
        raise ValueError(msg)
    z = (x - mean) / (stdev * math.sqrt(2.0))
    return 0.5 * math.erfc(z)


_POISSON_TAIL_EPS: Final = 1e-18


def poisson_sf(*, line: float, lam: float) -> float:
    """Survival function P(X > floor(line)) for X ~ Poisson(lam).

    ``line`` may be fractional (e.g. a sportsbook line of 2.5 threes);
    the result equals ``P(X >= ceil(line)) = P(X > floor(line))`` for
    non-integer lines, and the standard strict-inequality survival for
    integer lines.

    Raises:
        ValueError: If ``lam`` is not finite (NaN/inf) or is negative,
            or if ``line`` is NaN.
    """
    # `not (lam >= 0)` rejects NaN; the isfinite guard also rejects +inf.
    # CPython treats `lam < 0` as False for NaN, so the obvious check
    # would silently let NaN propagate to a confident-looking 1.0 output.
    if not math.isfinite(lam) or lam < 0:
        msg = f"lam must be a finite non-negative number, got {lam!r}"
        raise ValueError(msg)
    if math.isnan(line):
        msg = f"line must not be NaN, got {line!r}"
        raise ValueError(msg)
    if line < 0:
        return 1.0
    if math.isinf(line):
        # +inf line: P(X > inf) = 0 for any finite Poisson.
        return 0.0
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


_OPP_MAX_FRACTION: Final = 0.15
_REST_B2B_FRACTION: Final = -0.04
_REST_3PLUS_FRACTION: Final = 0.015
_HOME_FRACTION: Final = 0.02


def _clamp(value: float, lo: float, hi: float) -> float:
    # Reject NaN/inf explicitly: CPython's min/max do not preserve NaN
    # (e.g. min(0.15, NaN) returns 0.15), so a naive clamp would silently
    # produce a plausible-looking number from a non-finite input.
    if not math.isfinite(value):
        msg = f"value must be finite, got {value!r}"
        raise ValueError(msg)
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

    Raises:
        ValueError: If ``opp_def_rating`` or ``league_avg_def_rating`` is
            non-finite (NaN/inf).
    """
    if stat not in ("pts", "fg3m"):
        return 0.0
    if not math.isfinite(opp_def_rating):
        msg = f"opp_def_rating must be finite, got {opp_def_rating!r}"
        raise ValueError(msg)
    if not math.isfinite(league_avg_def_rating):
        msg = f"league_avg_def_rating must be finite, got {league_avg_def_rating!r}"
        raise ValueError(msg)
    if league_avg_def_rating == 0:
        return 0.0
    # opp_def_rating HIGHER than league avg = worse defense = positive delta.
    raw_fraction = (opp_def_rating - league_avg_def_rating) / league_avg_def_rating
    fraction = _clamp(raw_fraction, -_OPP_MAX_FRACTION, _OPP_MAX_FRACTION)
    return blended_mean * fraction


def adjust_for_rest(
    *, blended_mean: float, stat: ProjectionStat, days_rest: int | None
) -> float:
    """Additive adjustment for days of rest before the game.

    0 days rest (back-to-back): small negative.
    1 day rest (normal): 0.
    2 days rest: 0.
    3+ days rest: small positive.
    ``None`` (unknown rest, e.g. first game of season): 0.

    Raises:
        ValueError: If ``days_rest`` is negative.
    """
    if days_rest is None:
        return 0.0
    if days_rest < 0:
        msg = f"days_rest must be >= 0 or None, got {days_rest}"
        raise ValueError(msg)
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


_STAT_DISTRIBUTION: Final[Mapping[ProjectionStat, DistributionFamily]] = (
    MappingProxyType(
        {
            "pts": "normal",
            "reb": "normal",
            "ast": "normal",
            "fg3m": "poisson",
        }
    )
)
_STDEV_FLOORS: Final[Mapping[ProjectionStat, float]] = MappingProxyType(
    {
        "pts": 3.0,
        "reb": 1.5,
        "ast": 1.5,
        "fg3m": 0.8,
    }
)


def _mean(values: Sequence[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _variance(values: Sequence[float]) -> float:
    if len(values) < 2:  # noqa: PLR2004 — sample variance needs >= 2 observations
        return 0.0
    m = _mean(values)
    return sum((v - m) ** 2 for v in values) / (len(values) - 1)


def _compute_priors_from_logs(
    logs: Mapping[int, Sequence[PlayerGameLogEntry]],
    *,
    season: str,
) -> Mapping[ProjectionStat, StatPrior]:
    """Pure function: derive Empirical Bayes priors from per-player game logs.

    Separated from ``compute_priors_for_season`` so the script and tests can
    exercise the math without making real API calls.

    Raises:
        ValueError: If any stat's qualifying-player pool has fewer than 10
            entries (variance estimates would be too noisy).
    """
    result: dict[ProjectionStat, StatPrior] = {}
    for stat in STATS:
        per_player_means: list[float] = []
        per_player_variances: list[float] = []
        total_games = 0
        for games in logs.values():
            if len(games) < 2:  # noqa: PLR2004 — sample variance needs >= 2
                continue
            values = [float(getattr(g, stat)) for g in games]
            per_player_means.append(statistics.fmean(values))
            per_player_variances.append(statistics.variance(values))
            total_games += len(values)
        if len(per_player_means) < 10:  # noqa: PLR2004 — pool floor
            msg = (
                f"insufficient pool for {stat!r}: "
                f"{len(per_player_means)} players (need >= 10)"
            )
            raise ValueError(msg)
        # StatPrior.__post_init__ validates finite/positive variance and
        # non-empty season; let it raise rather than duplicating the check.
        result[stat] = StatPrior(
            tau_sq=statistics.variance(per_player_means),
            sigma_sq=statistics.fmean(per_player_variances),
            season=season,
            n_players=len(per_player_means),
            n_games=total_games,
        )
    return MappingProxyType(result)


async def compute_priors_for_season(
    client: NBAClient,
    *,
    season: Season | None = None,
    min_games: int = 30,
    min_minutes: float = 15.0,
    max_concurrency: int = 3,
) -> Mapping[ProjectionStat, StatPrior]:
    """Compute Empirical Bayes priors from live NBA Stats data.

    Identifies qualifying players from ``LeagueDashPlayerStats`` (filtered
    by ``min_games`` and ``min_minutes``), then concurrently fetches each
    player's ``PlayerGameLog`` to compute per-stat between-player and
    within-player variances.

    Long-running (~1-3 min for ~300 players); intended for callers that
    need fresh priors mid-season without re-running the regeneration
    script. For the common case, the baked ``STAT_PRIORS`` from
    ``fastbreak.projections_priors`` is faster and identical in shape.

    Args:
        client: NBA API client.
        season: Season in ``YYYY-YY`` format (e.g. ``"2025-26"``).
            Defaults to the current season via ``get_season_from_date``.
        min_games: Minimum games played for a player to qualify.
        min_minutes: Minimum per-game minutes for a player to qualify.
        max_concurrency: Concurrent in-flight requests for the per-player
            game-log fetch. Lower values are more rate-limit-friendly.

    Returns:
        An immutable ``Mapping[ProjectionStat, StatPrior]`` with one
        entry per stat in ``STATS``.

    Raises:
        ValueError: If ``min_games < 1``, ``min_minutes < 0``, or
            ``max_concurrency < 1``; if fewer than 10 players qualify;
            if any stat's pool is too small; or if the computed priors
            fail ``StatPrior``'s validation.
    """
    if min_games < 1:
        msg = f"min_games must be >= 1, got {min_games}"
        raise ValueError(msg)
    if min_minutes < 0:
        msg = f"min_minutes must be >= 0, got {min_minutes}"
        raise ValueError(msg)
    if max_concurrency < 1:
        # `client.get_many` does `concurrency = max_concurrency or 3`, so
        # passing 0 silently falls back to 3 instead of erroring.
        msg = f"max_concurrency must be >= 1, got {max_concurrency}"
        raise ValueError(msg)
    from fastbreak.endpoints import (  # noqa: PLC0415
        LeagueDashPlayerStats,
        PlayerGameLog,
    )

    season = season or get_season_from_date(league=client.league)
    league_resp = await client.get(LeagueDashPlayerStats(season=season))
    eligible = [
        p.player_id
        for p in league_resp.players
        if p.gp >= min_games and p.min >= min_minutes
    ]
    if len(eligible) < 10:  # noqa: PLR2004 — same floor as the inner pool check
        msg = (
            f"insufficient eligible players for season {season}: "
            f"{len(eligible)} (need >= 10 with gp>={min_games}, min>={min_minutes})"
        )
        raise ValueError(msg)
    log_endpoints = [PlayerGameLog(player_id=pid, season=season) for pid in eligible]
    log_responses = await client.get_many(
        log_endpoints, max_concurrency=max_concurrency
    )
    logs = {pid: resp.games for pid, resp in zip(eligible, log_responses, strict=True)}
    return _compute_priors_from_logs(logs, season=season)


def _build_stat_projection(  # noqa: PLR0913
    stat: ProjectionStat,
    games: Sequence[PlayerGameLogEntry],
    *,
    rolling_n: int,
    opp_def_rating: float,
    league_avg_def_rating: float,
    days_rest: int | None,
    is_home: bool,
    priors: Mapping[ProjectionStat, StatPrior],
) -> StatProjection:
    """Build a single-stat projection from a player's game log and context.

    Caller (``project_player``) guarantees ``games`` is non-empty,
    ``rolling_n >= 1``, and ``priors`` contains every key in ``STATS``,
    so ``recent`` always has at least one element and ``priors[stat]``
    is always present.
    """
    values = [float(getattr(g, stat)) for g in games]
    season_mean = _mean(values)
    # PlayerGameLog response returns games newest-first; leave in that order.
    recent = values[:rolling_n]
    rolling_mean = _mean(recent)
    prior = priors[stat]
    blended = empirical_bayes_blend(
        rolling_mean=rolling_mean,
        season_mean=season_mean,
        n=len(recent),
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
    days_rest: int | None,
    season: Season | None = None,
    rolling_n: int = 10,
    stats: Sequence[ProjectionStat] = STATS,
    priors: Mapping[ProjectionStat, StatPrior] | None = None,
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
        days_rest: Days of rest before the game (0 = back-to-back). Pass
            ``None`` to indicate unknown rest (e.g. first game of season),
            in which case the rest adjustment is 0. Must be ``>= 0``.
        season: Season in YYYY-YY format (e.g. "2025-26"). Defaults to
            the season containing ``game_date`` via ``get_season_from_date``,
            so historical backtests and future-schedule projections resolve
            to the correct season without an explicit override.
        rolling_n: Number of most-recent games for the rolling mean.
        stats: Stats to project (defaults to all four in ``STATS``).
        priors: Optional mapping of per-stat priors. When ``None`` (the
            default), the baked ``STAT_PRIORS`` from
            ``fastbreak.projections_priors`` is used. When provided, the
            mapping must contain every key in ``STATS`` — partial dicts
            are rejected to avoid mixing baked and custom priors silently.
            Use ``compute_priors_for_season`` to build a fresh mapping.

    Returns:
        A ``PlayerProjection`` populated with one ``StatProjection`` per stat.

    Raises:
        ValueError: If ``rolling_n < 1``, ``days_rest`` is negative,
            ``stats`` contains an unsupported stat, ``priors`` is provided
            but missing one of the required keys, the player has no
            logged games, or the opponent team is missing / has an invalid
            estimated defensive rating (None or non-finite).
    """
    if rolling_n < 1:
        msg = f"rolling_n must be >= 1, got {rolling_n}"
        raise ValueError(msg)
    if days_rest is not None and days_rest < 0:
        msg = f"days_rest must be >= 0 or None, got {days_rest}"
        raise ValueError(msg)
    bad_stats = [s for s in stats if s not in STATS]
    if bad_stats:
        msg = f"unsupported stats: {bad_stats!r}; supported = {list(STATS)}"
        raise ValueError(msg)
    if priors is not None:
        missing = set(STATS) - priors.keys()
        if missing:
            msg = f"priors must contain all of {list(STATS)}; missing {sorted(missing)}"
            raise ValueError(msg)
    effective_priors: Mapping[ProjectionStat, StatPrior] = (
        priors if priors is not None else STAT_PRIORS
    )
    from fastbreak.endpoints import PlayerGameLog, TeamEstimatedMetrics  # noqa: PLC0415

    season = season or get_season_from_date(game_date, league=client.league)
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
    if opp.e_def_rating is None or not math.isfinite(opp.e_def_rating):
        msg = (
            f"Opponent team_id={opponent_team_id} has invalid e_def_rating: "
            f"{opp.e_def_rating!r}"
        )
        raise ValueError(msg)
    # Filter both None and non-finite values: a single NaN/inf in the list
    # would poison _mean and silently feed adjust_for_opponent with garbage.
    league_avg_def = _mean(
        [
            t.e_def_rating
            for t in team_resp.teams
            if t.e_def_rating is not None and math.isfinite(t.e_def_rating)
        ]
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
            priors=effective_priors,
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
