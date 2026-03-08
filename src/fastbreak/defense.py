"""Defensive analysis helpers for the NBA Stats API.

Provides zone-based aggregate defensive stats (LeagueDashPtTeamDefend),
opponent shooting stats (LeagueDashOppPtShot), and defensive box scores
(BoxScoreDefensive). The pure helper `defensive_shot_quality_vs_league`
mirrors `shot_quality_vs_league()` from shots.py.

Note: true per-shot defensive coordinate data (x/y) is not available from the
NBA Stats API — `ShotChartDetail` has no defense context measure. This module
provides zone-based aggregate data instead.

Examples::

    from fastbreak.clients import NBAClient
    from fastbreak.defense import (
        get_team_defense_zones,
        get_team_opponent_stats,
        defensive_shot_quality_vs_league,
    )

    async with NBAClient() as client:
        zones = await get_team_defense_zones(client)

    deltas = defensive_shot_quality_vs_league(zones, team_id=1610612738)
    for abbr, delta in deltas.items():
        print(f"{abbr}: {delta:+.3f} vs league avg (negative = better defense)")
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastbreak.seasons import get_season_from_date
from fastbreak.tracking import (
    get_player_shot_defense as get_player_shot_defense,  # noqa: PLC0414
)

if TYPE_CHECKING:
    from fastbreak.clients.nba import NBAClient
    from fastbreak.endpoints.league_dash_pt_team_defend import DefenseCategory
    from fastbreak.models.box_score_defensive import BoxScoreDefensiveResponse
    from fastbreak.models.league_dash_opp_pt_shot import OppPtShotStats
    from fastbreak.models.league_dash_pt_team_defend import TeamDefendStats
    from fastbreak.types import Season, SeasonType


def defensive_shot_quality_vs_league(
    zones: list[TeamDefendStats],
    team_id: int,
) -> dict[str, float]:
    """FG% delta that a team ALLOWS vs. league average.

    Extracts pct_plusminus from TeamDefendStats rows for the given team.
    Negative = better than average (team holds opponents below league FG%).
    Mirrors shot_quality_vs_league() from shots.py.

    Args:
        zones: All teams' defend stats from get_team_defense_zones().
        team_id: NBA team ID to extract stats for.

    Returns:
        Dict mapping team_abbreviation to pct_plusminus.
        Returns empty dict if team_id is not found in zones.

        Note: assumes one row per team in zones (i.e., zones comes from a single
        get_team_defense_zones() call using the default defense_category="Overall").
        Multiple rows with the same team_id would produce only the last entry.
    """
    return {
        stats.team_abbreviation: stats.pct_plusminus
        for stats in zones
        if stats.team_id == team_id
    }


async def get_team_defense_zones(
    client: NBAClient,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
    defense_category: DefenseCategory = "Overall",
) -> list[TeamDefendStats]:
    """Defensive breakdown for all 30 teams by shot category.

    Wraps LeagueDashPtTeamDefend.
    Returns opponent FGA frequency and FG% allowed vs league average per team.

    Args:
        client: NBA API client.
        season: Season in YYYY-YY format (defaults to current season).
        season_type: "Regular Season", "Playoffs", or "Pre Season".
        defense_category: Shot category to analyze ("Overall", "3 Pointers",
            "2 Pointers", "Less Than 6Ft", "Less Than 10Ft",
            "Greater Than 15Ft"). Defaults to "Overall".

    Returns:
        list[TeamDefendStats] with one entry per team (all 30 teams).
        Caller filters by team_id.
    """
    from fastbreak.endpoints import LeagueDashPtTeamDefend  # noqa: PLC0415

    season = season or get_season_from_date()
    response = await client.get(
        LeagueDashPtTeamDefend(
            season=season,
            season_type=season_type,
            defense_category=defense_category,
        )
    )
    return response.teams


async def get_team_opponent_stats(
    client: NBAClient,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
) -> list[OppPtShotStats]:
    """League-wide opponent shooting stats for all 30 teams.

    Wraps LeagueDashOppPtShot.
    Returns FGA frequency, FG%, eFG% allowed broken down by 2PT and 3PT.

    Args:
        client: NBA API client.
        season: Season in YYYY-YY format (defaults to current season).
        season_type: "Regular Season", "Playoffs", or "Pre Season".

    Returns:
        list[OppPtShotStats] with one entry per team (all 30 teams).
        Caller filters by team_id.
    """
    from fastbreak.endpoints import LeagueDashOppPtShot  # noqa: PLC0415

    season = season or get_season_from_date()
    response = await client.get(
        LeagueDashOppPtShot(season=season, season_type=season_type)
    )
    return response.teams


async def get_box_scores_defensive(
    client: NBAClient,
    game_ids: list[str],
    max_concurrency: int = 5,
) -> dict[str, BoxScoreDefensiveResponse]:
    """Fetch defensive box scores for multiple games concurrently.

    Mirrors get_box_scores_advanced() — returns {game_id: response}.
    Wraps BoxScoreDefensive via get_many().

    Args:
        client: NBA API client.
        game_ids: List of NBA game IDs (e.g., ["0022500001", "0022500002"]).
        max_concurrency: Maximum concurrent requests (default 5).

    Returns:
        Dict mapping game_id to BoxScoreDefensiveResponse, in input order.
        Raises ExceptionGroup if any request fails (all in-flight cancelled).
    """
    from fastbreak.endpoints import BoxScoreDefensive  # noqa: PLC0415

    if not game_ids:
        return {}
    endpoints = [BoxScoreDefensive(game_id=gid) for gid in game_ids]
    responses = await client.get_many(endpoints, max_concurrency=max_concurrency)
    return dict(zip(game_ids, responses, strict=True))
