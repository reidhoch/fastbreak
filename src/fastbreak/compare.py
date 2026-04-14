"""Player comparison helpers for the NBA Stats API.

Provides a composite comparison of two NBA players across box score stats,
derived efficiency metrics, and estimated advanced metrics. Follows the same
pattern as :mod:`fastbreak.clutch`: frozen dataclasses for results, pure
standalone functions for computation, and a thin async wrapper for API calls.

Examples::

    from fastbreak.clients import BaseClient
    from fastbreak.compare import get_player_comparison

    async with NBAClient() as client:
        result = await get_player_comparison(client, player_a_id=2544, player_b_id=203999)
        a, b = result.player_a, result.player_b
        print(f"{a.name}: {a.pts} pts")
        print(f"{b.name}: {b.pts} pts")
        print(f"Edge: {result.edges.a_leads}-{result.edges.b_leads}-{result.edges.ties}")
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Protocol

from fastbreak.estimated import find_player
from fastbreak.logging import logger
from fastbreak.metrics import (
    ast_to_tov,
    effective_fg_pct,
    free_throw_rate,
    game_score,
    stat_delta,
    three_point_rate,
    true_shooting,
)
from fastbreak.seasons import get_season_from_date

if TYPE_CHECKING:
    from fastbreak.clients.base import BaseClient
    from fastbreak.models.player_estimated_metrics import PlayerEstimatedMetric
    from fastbreak.types import PerMode, Season, SeasonType


# ---------------------------------------------------------------------------
# Protocol
# ---------------------------------------------------------------------------


class _CompareStatsLike(Protocol):
    """Structural protocol for stats objects accepted by build_compared_player."""

    description: str
    min: float
    pts: float
    reb: float
    oreb: float
    dreb: float
    ast: float
    stl: float
    blk: float
    tov: float
    pf: float
    plus_minus: float
    fgm: float
    fga: float
    fg_pct: float
    fg3m: float
    fg3a: float
    fg3_pct: float
    ftm: float
    fta: float
    ft_pct: float


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

COMPARISON_METRICS: tuple[str, ...] = (
    "pts",
    "reb",
    "ast",
    "stl",
    "blk",
    "tov",
    "fgm",
    "fga",
    "fg_pct",
    "fg3m",
    "fg3a",
    "fg3_pct",
    "ftm",
    "fta",
    "ft_pct",
    "oreb",
    "dreb",
    "pf",
    "min",
    "plus_minus",
    "ts_pct",
    "efg_pct",
    "ast_tov",
    "game_score",
    "ft_rate",
    "three_pt_rate",
    "e_off_rating",
    "e_def_rating",
    "e_net_rating",
    "e_usg_pct",
    "e_pace",
)

HIGHER_IS_WORSE: frozenset[str] = frozenset({"tov", "pf", "e_def_rating"})

# NBA stats have ~3 decimal places of precision; 1e-9 absorbs only IEEE 754
# rounding noise, not real stat differences.
_TOLERANCE: float = 1e-9


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ComparedPlayer:
    """Complete stats for one player in a comparison."""

    player_id: int
    name: str
    # Box score
    min: float
    pts: float
    reb: float
    oreb: float
    dreb: float
    ast: float
    stl: float
    blk: float
    tov: float
    pf: float
    plus_minus: float
    fgm: float
    fga: float
    fg_pct: float
    fg3m: float
    fg3a: float
    fg3_pct: float
    ftm: float
    fta: float
    ft_pct: float
    # Derived
    ts_pct: float | None
    efg_pct: float | None
    ast_tov: float | None
    game_score: float
    ft_rate: float | None
    three_pt_rate: float | None
    # Estimated advanced
    e_off_rating: float | None
    e_def_rating: float | None
    e_net_rating: float | None
    e_usg_pct: float | None
    e_pace: float | None


@dataclass(frozen=True)
class EdgeSummary:
    """Lead/trail/tie counts across comparison metrics."""

    a_leads: int
    b_leads: int
    ties: int
    unavailable: int
    total: int

    def __post_init__(self) -> None:
        expected = self.a_leads + self.b_leads + self.ties + self.unavailable
        if self.total != expected:
            msg = f"total ({self.total}) != a_leads + b_leads + ties + unavailable ({expected})"
            raise ValueError(msg)


@dataclass(frozen=True)
class ComparisonResult:
    """Complete comparison between two players."""

    player_a: ComparedPlayer
    player_b: ComparedPlayer
    deltas: dict[str, float | None]
    edges: EdgeSummary


# ---------------------------------------------------------------------------
# Pure functions
# ---------------------------------------------------------------------------


def build_compared_player(
    player_id: int,
    stats: _CompareStatsLike,
    estimated: PlayerEstimatedMetric | None = None,
) -> ComparedPlayer:
    """Build a ComparedPlayer from raw endpoint data and optional estimated metrics.

    Computes derived metrics (TS%, eFG%, A/TO, game score, FT rate, 3P rate)
    from the box score stats. Extracts estimated advanced metrics from the
    ``PlayerEstimatedMetric`` if provided.

    Args:
        player_id: NBA player ID.
        stats: Object satisfying ``_CompareStatsLike`` (e.g. ``PlayerCompareStats``).
        estimated: Optional estimated metrics for this player.

    Returns:
        ComparedPlayer with all fields populated.
    """
    return ComparedPlayer(
        player_id=player_id,
        name=stats.description,
        min=stats.min,
        pts=stats.pts,
        reb=stats.reb,
        oreb=stats.oreb,
        dreb=stats.dreb,
        ast=stats.ast,
        stl=stats.stl,
        blk=stats.blk,
        tov=stats.tov,
        pf=stats.pf,
        plus_minus=stats.plus_minus,
        fgm=stats.fgm,
        fga=stats.fga,
        fg_pct=stats.fg_pct,
        fg3m=stats.fg3m,
        fg3a=stats.fg3a,
        fg3_pct=stats.fg3_pct,
        ftm=stats.ftm,
        fta=stats.fta,
        ft_pct=stats.ft_pct,
        ts_pct=true_shooting(pts=stats.pts, fga=stats.fga, fta=stats.fta),
        efg_pct=effective_fg_pct(fgm=stats.fgm, fg3m=stats.fg3m, fga=stats.fga),
        ast_tov=ast_to_tov(ast=stats.ast, tov=stats.tov),
        game_score=game_score(
            pts=stats.pts,
            fgm=stats.fgm,
            fga=stats.fga,
            ftm=stats.ftm,
            fta=stats.fta,
            oreb=stats.oreb,
            dreb=stats.dreb,
            stl=stats.stl,
            ast=stats.ast,
            blk=stats.blk,
            pf=stats.pf,
            tov=stats.tov,
        ),
        ft_rate=free_throw_rate(fta=stats.fta, fga=stats.fga),
        three_pt_rate=three_point_rate(fg3a=stats.fg3a, fga=stats.fga),
        e_off_rating=estimated.e_off_rating if estimated is not None else None,
        e_def_rating=estimated.e_def_rating if estimated is not None else None,
        e_net_rating=estimated.e_net_rating if estimated is not None else None,
        e_usg_pct=estimated.e_usg_pct if estimated is not None else None,
        e_pace=estimated.e_pace if estimated is not None else None,
    )


def comparison_deltas(
    a: ComparedPlayer,
    b: ComparedPlayer,
) -> dict[str, float | None]:
    """Compute stat deltas (a - b) for every comparison metric.

    Args:
        a: First player.
        b: Second player.

    Returns:
        Dict mapping metric name to delta value. ``None`` if either value is
        ``None`` or the computed delta is non-finite (inf/nan).
    """
    result: dict[str, float | None] = {}
    for metric in COMPARISON_METRICS:
        a_val = getattr(a, metric)
        b_val = getattr(b, metric)
        if a_val is None or b_val is None:
            result[metric] = None
        else:
            d = stat_delta(a_val, b_val)
            if d is None or not math.isfinite(d):
                result[metric] = None
            else:
                result[metric] = d
    return result


def comparison_edges(
    deltas: dict[str, float | None],
    *,
    higher_is_worse: frozenset[str] = HIGHER_IS_WORSE,
) -> EdgeSummary:
    """Count how many metrics each player leads in.

    For metrics in ``higher_is_worse`` (e.g. turnovers, fouls, defensive
    rating), a positive delta means player A has *more*, which is bad — so
    player B leads. Metrics with ``None`` deltas (missing data for one or
    both players) are counted as ``unavailable``, not as ties.

    Args:
        deltas: Metric deltas from ``comparison_deltas``.
        higher_is_worse: Metrics where lower is better.

    Returns:
        EdgeSummary with counts.
    """
    a_leads = 0
    b_leads = 0
    ties = 0
    unavailable = 0
    for metric, val in deltas.items():
        if val is None:
            unavailable += 1
            continue
        if abs(val) < _TOLERANCE:
            ties += 1
            continue
        effective = -val if metric in higher_is_worse else val
        if effective > 0:
            a_leads += 1
        else:
            b_leads += 1
    return EdgeSummary(
        a_leads=a_leads,
        b_leads=b_leads,
        ties=ties,
        unavailable=unavailable,
        total=a_leads + b_leads + ties + unavailable,
    )


def stat_leader(
    a: ComparedPlayer,
    b: ComparedPlayer,
    metric: str,
    *,
    higher_is_worse: bool = False,
) -> int | None:
    """Return the player_id of whichever player leads in a metric.

    Args:
        a: First player.
        b: Second player.
        metric: Attribute name on ComparedPlayer to compare.
        higher_is_worse: If True, the player with the *lower* value leads.

    Returns:
        ``player_id`` of the leader, or ``None`` if tied, non-finite, or
        either value is ``None``.
    """
    a_val = getattr(a, metric)
    b_val = getattr(b, metric)
    if a_val is None or b_val is None:
        return None
    delta = stat_delta(a_val, b_val)
    if delta is None or not math.isfinite(delta) or abs(delta) < _TOLERANCE:
        return None
    effective = -delta if higher_is_worse else delta
    return a.player_id if effective > 0 else b.player_id


def compare_players(  # noqa: PLR0913
    player_a_id: int,
    player_a_stats: _CompareStatsLike,
    player_b_id: int,
    player_b_stats: _CompareStatsLike,
    *,
    estimated_a: PlayerEstimatedMetric | None = None,
    estimated_b: PlayerEstimatedMetric | None = None,
) -> ComparisonResult:
    """Build a full comparison between two players from raw stats.

    Pure orchestrator — calls ``build_compared_player``, ``comparison_deltas``,
    and ``comparison_edges`` in sequence.

    Args:
        player_a_id: NBA player ID for player A.
        player_a_stats: Box score stats for player A.
        player_b_id: NBA player ID for player B.
        player_b_stats: Box score stats for player B.
        estimated_a: Optional estimated metrics for player A.
        estimated_b: Optional estimated metrics for player B.

    Returns:
        ComparisonResult with both players, deltas, and edge summary.
    """
    pa = build_compared_player(player_a_id, player_a_stats, estimated=estimated_a)
    pb = build_compared_player(player_b_id, player_b_stats, estimated=estimated_b)
    deltas = comparison_deltas(pa, pb)
    edges = comparison_edges(deltas)
    return ComparisonResult(player_a=pa, player_b=pb, deltas=deltas, edges=edges)


# ---------------------------------------------------------------------------
# Async wrapper
# ---------------------------------------------------------------------------


async def get_player_comparison(  # noqa: PLR0913
    client: BaseClient,
    player_a_id: int,
    player_b_id: int,
    *,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
    per_mode: PerMode = "PerGame",
) -> ComparisonResult:
    """Fetch and build a full comparison between two players.

    Makes two concurrent API calls:

    1. ``PlayerCompare`` — box score stats for both players
    2. ``PlayerEstimatedMetrics`` — league-wide estimated advanced metrics

    Args:
        client: NBA API client.
        player_a_id: NBA player ID for the first player.
        player_b_id: NBA player ID for the second player.
        season: Season in YYYY-YY format (defaults to current season).
        season_type: ``"Regular Season"``, ``"Playoffs"``, etc.
        per_mode: ``"PerGame"``, ``"Totals"``, ``"Per36"``, etc.

    Returns:
        ComparisonResult with both players, deltas, and edge summary.

    Raises:
        ValueError: If the PlayerCompare endpoint returns fewer than 2 individual rows.
    """
    from fastbreak.endpoints import (  # noqa: PLC0415
        PlayerCompare,
        PlayerEstimatedMetrics,
    )

    season = season or get_season_from_date(league=client.league)

    results: list[Any] = await client.get_many(
        [
            PlayerCompare(
                player_id_list=str(player_a_id),
                vs_player_id_list=str(player_b_id),
                season=season,
                season_type=season_type,
                per_mode=per_mode,
                league_id=client.league_id,
            ),
            PlayerEstimatedMetrics(
                season=season, season_type=season_type, league_id=client.league_id
            ),
        ]
    )

    compare_resp = results[0]  # PlayerCompareResponse
    estimated_resp = results[1]  # PlayerEstimatedMetricsResponse

    if len(compare_resp.individual) < 2:  # noqa: PLR2004
        msg = (
            f"PlayerCompare returned {len(compare_resp.individual)} individual rows "
            f"(expected 2) for player IDs {player_a_id} and {player_b_id}"
        )
        raise ValueError(msg)

    # NBA API returns individual rows in request order (player_id_list first,
    # vs_player_id_list second). Cross-reference with estimated metrics names
    # when available to detect unexpected row order changes.
    row_a_stats = compare_resp.individual[0]
    row_b_stats = compare_resp.individual[1]

    estimated_a = find_player(estimated_resp.players, player_a_id)
    if estimated_a is None:
        logger.debug("estimated_metrics_not_found", player_id=player_a_id)
    estimated_b = find_player(estimated_resp.players, player_b_id)
    if estimated_b is None:
        logger.debug("estimated_metrics_not_found", player_id=player_b_id)

    if estimated_a is not None and row_a_stats.description != estimated_a.player_name:
        logger.warning(
            "compare_row_order_mismatch",
            expected_player=estimated_a.player_name,
            got_description=row_a_stats.description,
            player_id=player_a_id,
            hint="PlayerCompare row order may have changed",
        )
    if estimated_b is not None and row_b_stats.description != estimated_b.player_name:
        logger.warning(
            "compare_row_order_mismatch",
            expected_player=estimated_b.player_name,
            got_description=row_b_stats.description,
            player_id=player_b_id,
            hint="PlayerCompare row order may have changed",
        )

    return compare_players(
        player_a_id=player_a_id,
        player_a_stats=row_a_stats,
        player_b_id=player_b_id,
        player_b_stats=row_b_stats,
        estimated_a=estimated_a,
        estimated_b=estimated_b,
    )
