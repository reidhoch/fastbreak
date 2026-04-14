"""League-wide lineup analysis helpers for the NBA Stats API.

Provides league-wide lineup statistics (LeagueDashLineups), lineup efficiency
ratings (LeagueLineupViz), and pure-computation helpers for ranking and
filtering lineups. Complements the team-scoped get_lineup_stats() and
get_lineup_net_ratings() in fastbreak.teams.

Examples::

    from fastbreak.clients import BaseClient
    from fastbreak.lineups import get_league_lineups, get_top_lineups, lineup_net_rating

    async with NBAClient() as client:
        lineups = await get_league_lineups(client, team_id=1610612747)

    net_rtg = lineup_net_rating(off_rating=115.2, def_rating=108.4)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from fastbreak.seasons import get_season_from_date

if TYPE_CHECKING:
    from fastbreak.clients.base import BaseClient
    from fastbreak.models.league_dash_lineups import LeagueLineup
    from fastbreak.models.league_lineup_viz import LineupViz
    from fastbreak.types import MeasureType, PerMode, Season, SeasonType


def lineup_net_rating(off_rating: float, def_rating: float) -> float:
    """Net rating: offensive rating minus defensive rating.

    Positive values indicate the lineup outscores opponents; negative means
    it is outscored.
    """
    return off_rating - def_rating


def rank_lineups(
    lineups: list[LeagueLineup],
    *,
    min_minutes: float = 10.0,
    by: Literal["min", "pts", "plus_minus", "w_pct", "fg_pct"] = "plus_minus",
    ascending: bool = False,
) -> list[LeagueLineup]:
    """Filter lineups by volume and sort by a stat column.

    Lineups below min_minutes average minutes are excluded.
    Lineups with None for the sort key are excluded when the key is nullable
    (fg_pct).
    """
    filtered = [lu for lu in lineups if lu.min >= min_minutes]

    if by == "fg_pct":
        valid = [lu for lu in filtered if lu.fg_pct is not None]
        valid.sort(key=lambda lu: lu.fg_pct, reverse=not ascending)  # type: ignore[arg-type,return-value]
        return valid

    filtered.sort(key=lambda lu: getattr(lu, by), reverse=not ascending)
    return filtered


async def get_league_lineups(  # noqa: PLR0913
    client: BaseClient,
    team_id: int,
    *,
    group_quantity: int = 5,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
    per_mode: PerMode = "PerGame",
    measure_type: MeasureType = "Base",
) -> list[LeagueLineup]:
    """Lineup combination statistics for a team.

    Wraps LeagueDashLineups. A specific team_id is required — the NBA API
    does not support team_id=0 for this endpoint.
    """
    from fastbreak.endpoints import LeagueDashLineups  # noqa: PLC0415

    season = season or get_season_from_date()
    response = await client.get(
        LeagueDashLineups(
            team_id=team_id,
            group_quantity=group_quantity,
            season=season,
            season_type=season_type,
            per_mode=per_mode,
            measure_type=measure_type,
        )
    )
    return response.lineups


async def get_league_lineup_ratings(  # noqa: PLR0913
    client: BaseClient,
    *,
    team_id: int = 0,
    group_quantity: int = 5,
    minutes_min: int = 10,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
    per_mode: PerMode = "Totals",
) -> list[LineupViz]:
    """Lineup efficiency ratings across the league.

    Wraps LeagueLineupViz. Returns offensive/defensive ratings, pace, shot
    distribution, and opponent defense stats for qualifying lineups.

    Pass team_id=0 for all teams. When a non-zero team_id is provided,
    results are filtered client-side (the API ignores TeamID for this
    endpoint).
    """
    from fastbreak.endpoints import LeagueLineupViz  # noqa: PLC0415

    season = season or get_season_from_date()
    response = await client.get(
        LeagueLineupViz(
            team_id=team_id,
            group_quantity=group_quantity,
            minutes_min=minutes_min,
            season=season,
            season_type=season_type,
            per_mode=per_mode,
        )
    )
    lineups = response.lineups
    if team_id:
        lineups = [lu for lu in lineups if lu.team_id == team_id]
    return lineups


async def get_top_lineups(  # noqa: PLR0913
    client: BaseClient,
    team_id: int,
    *,
    group_quantity: int = 5,
    min_minutes: float = 10.0,
    top_n: int = 10,
    by: Literal["min", "pts", "plus_minus", "w_pct", "fg_pct"] = "plus_minus",
    ascending: bool = False,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
    per_mode: PerMode = "PerGame",
    measure_type: MeasureType = "Base",
) -> list[LeagueLineup]:
    """Top N lineups for a team by a stat, filtered by minimum minutes.

    Convenience wrapper: fetches lineups, filters, sorts, and trims
    to top_n results. Requires a specific team_id.
    """
    lineups = await get_league_lineups(
        client,
        team_id,
        group_quantity=group_quantity,
        season=season,
        season_type=season_type,
        per_mode=per_mode,
        measure_type=measure_type,
    )
    ranked = rank_lineups(lineups, min_minutes=min_minutes, by=by, ascending=ascending)
    return ranked[:top_n]


async def get_two_man_combos(  # noqa: PLR0913
    client: BaseClient,
    team_id: int,
    *,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
    per_mode: PerMode = "PerGame",
    measure_type: MeasureType = "Base",
) -> list[LeagueLineup]:
    """Two-man combination stats for a specific team.

    Convenience wrapper that sets group_quantity=2 and requires a team_id.
    """
    return await get_league_lineups(
        client,
        team_id=team_id,
        group_quantity=2,
        season=season,
        season_type=season_type,
        per_mode=per_mode,
        measure_type=measure_type,
    )


async def get_lineup_efficiency(  # noqa: PLR0913
    client: BaseClient,
    *,
    team_id: int = 0,
    group_quantity: int = 5,
    minutes_min: int = 10,
    top_n: int | None = None,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
    per_mode: PerMode = "Totals",
) -> list[LineupViz]:
    """Lineups sorted by net rating (best first).

    Wraps get_league_lineup_ratings and sorts by net_rating descending.
    Optionally caps results at top_n.
    """
    lineups = await get_league_lineup_ratings(
        client,
        team_id=team_id,
        group_quantity=group_quantity,
        minutes_min=minutes_min,
        season=season,
        season_type=season_type,
        per_mode=per_mode,
    )
    lineups.sort(key=lambda lu: lu.net_rating, reverse=True)
    if top_n is not None:
        return lineups[:top_n]
    return lineups
