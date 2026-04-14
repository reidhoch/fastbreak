"""Estimated metrics analysis helpers for the NBA Stats API.

Provides async fetchers and pure-computation helpers for working with player
and team estimated advanced metrics (PlayerEstimatedMetrics,
TeamEstimatedMetrics endpoints). Estimated metrics use league-wide context
to produce reliable values even for players with limited sample sizes.

Examples::

    from fastbreak.clients import BaseClient
    from fastbreak.estimated import (
        find_player,
        find_team,
        get_player_estimated_metrics,
        rank_estimated_metrics,
    )

    async with NBAClient() as client:
        players = await get_player_estimated_metrics(client)

    top10 = rank_estimated_metrics(players, by="e_net_rating", min_gp=20)
    star  = find_player(players, player_id=1641705)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, get_args

from fastbreak.seasons import get_season_from_date

if TYPE_CHECKING:
    from fastbreak.clients.base import BaseClient
    from fastbreak.models.player_estimated_metrics import PlayerEstimatedMetric
    from fastbreak.models.team_estimated_metrics import TeamEstimatedMetric
    from fastbreak.types import Season, SeasonType


_PlayerMetricField = Literal[
    "e_off_rating",
    "e_def_rating",
    "e_net_rating",
    "e_pace",
    "e_usg_pct",
    "e_ast_ratio",
    "e_oreb_pct",
    "e_dreb_pct",
    "e_reb_pct",
    "e_tov_pct",
]

_VALID_METRIC_FIELDS: frozenset[str] = frozenset(get_args(_PlayerMetricField))


def find_player(
    players: list[PlayerEstimatedMetric],
    player_id: int,
) -> PlayerEstimatedMetric | None:
    """Return the first PlayerEstimatedMetric matching player_id, or None."""
    return next((p for p in players if p.player_id == player_id), None)


def find_team(
    teams: list[TeamEstimatedMetric],
    team_id: int,
) -> TeamEstimatedMetric | None:
    """Return the first TeamEstimatedMetric matching team_id, or None."""
    return next((t for t in teams if t.team_id == team_id), None)


def rank_estimated_metrics(
    players: list[PlayerEstimatedMetric],
    *,
    by: _PlayerMetricField = "e_net_rating",
    ascending: bool = False,
    min_gp: int = 0,
    min_minutes: float = 0.0,
) -> list[PlayerEstimatedMetric]:
    """Filter and sort players by an estimated metric field.

    Players below the minimum games played or minutes threshold are excluded.
    Players with None for the sort field are also excluded.

    Args:
        players: List of player estimated metrics.
        by: Field name to sort by. Must be one of the estimated metric fields.
            Defaults to "e_net_rating".
        ascending: If True, sort ascending (lowest first). Defaults to False
            (highest first).
        min_gp: Minimum games played (inclusive). Defaults to 0.
        min_minutes: Minimum per-game average minutes (inclusive).
            E.g. 30.0 for 30+ min/g. Defaults to 0.0.

    Returns:
        Filtered and sorted list of PlayerEstimatedMetric.

    Raises:
        ValueError: If ``by`` is not a valid metric field, or if ``min_gp``
            or ``min_minutes`` is negative.
    """
    if by not in _VALID_METRIC_FIELDS:
        msg = f"by must be one of {get_args(_PlayerMetricField)}, got {by!r}"
        raise ValueError(msg)
    if min_gp < 0:
        msg = "min_gp must be non-negative"
        raise ValueError(msg)
    if min_minutes < 0:
        msg = "min_minutes must be non-negative"
        raise ValueError(msg)
    filtered = [
        p
        for p in players
        if p.gp >= min_gp and p.minutes >= min_minutes and getattr(p, by) is not None
    ]
    return sorted(filtered, key=lambda p: getattr(p, by), reverse=not ascending)


async def get_player_estimated_metrics(
    client: BaseClient,
    *,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
) -> list[PlayerEstimatedMetric]:
    """Fetch estimated advanced metrics for all players in the league."""
    from fastbreak.endpoints import PlayerEstimatedMetrics  # noqa: PLC0415

    season = season or get_season_from_date()
    response = await client.get(
        PlayerEstimatedMetrics(season=season, season_type=season_type)
    )
    return response.players


async def get_team_estimated_metrics(
    client: BaseClient,
    *,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
) -> list[TeamEstimatedMetric]:
    """Fetch estimated advanced metrics for all teams in the league."""
    from fastbreak.endpoints import TeamEstimatedMetrics  # noqa: PLC0415

    season = season or get_season_from_date()
    response = await client.get(
        TeamEstimatedMetrics(season=season, season_type=season_type)
    )
    return response.teams


async def get_estimated_leaders(  # noqa: PLR0913
    client: BaseClient,
    *,
    metric: _PlayerMetricField = "e_net_rating",
    top_n: int = 10,
    min_gp: int = 0,
    min_minutes: float = 0.0,
    ascending: bool = False,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
) -> list[PlayerEstimatedMetric]:
    """Fetch league-wide estimated metrics and return the top players.

    Convenience wrapper: fetches all players, applies rank_estimated_metrics,
    and slices to top_n.
    """
    if top_n < 1:
        msg = "top_n must be at least 1"
        raise ValueError(msg)

    players = await get_player_estimated_metrics(
        client, season=season, season_type=season_type
    )
    ranked = rank_estimated_metrics(
        players, by=metric, ascending=ascending, min_gp=min_gp, min_minutes=min_minutes
    )
    return ranked[:top_n]
