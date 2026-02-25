"""Game lookup utilities for the NBA Stats API."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastbreak.clients.nba import NBAClient
    from fastbreak.types import Date, SeasonType


async def get_game_ids(  # noqa: PLR0913
    client: NBAClient,
    season: str | None = None,
    *,
    season_type: SeasonType = "Regular Season",
    team_id: int | None = None,
    date_from: Date | None = None,
    date_to: Date | None = None,
) -> list[str]:
    """Return sorted, deduplicated game IDs for a season.

    Uses LeagueGameLog (team-level) as the source. Because the log contains
    one row per team per game, game IDs are deduplicated before returning.

    The NBA API's TeamID parameter on leaguegamelog is silently ignored, so
    team filtering is applied client-side after fetching.

    Args:
        client: NBA API client
        season: Season in YYYY-YY format (defaults to current season)
        season_type: "Regular Season", "Playoffs", etc.
        team_id: Restrict to a specific team's games (None = all teams)
        date_from: Only include games on or after this date (MM/DD/YYYY)
        date_to: Only include games on or before this date (MM/DD/YYYY)

    Returns:
        Sorted list of unique game ID strings (ascending / chronological)

    Examples:
        ids = await get_game_ids(client, "2024-25")
        playoff_ids = await get_game_ids(client, "2024-25", season_type="Playoffs")
        gsw_ids = await get_game_ids(client, "2024-25", team_id=1610612744)

    """
    from fastbreak.endpoints import LeagueGameLog  # noqa: PLC0415
    from fastbreak.utils import get_season_from_date  # noqa: PLC0415

    season = season or get_season_from_date()
    endpoint = LeagueGameLog(
        season=season,
        season_type=season_type,
        player_or_team="T",
        team_id=team_id,
        date_from=date_from,
        date_to=date_to,
    )
    response = await client.get(endpoint)
    entries = response.games
    if team_id is not None:
        entries = [e for e in entries if e.team_id == team_id]
    return sorted({entry.game_id for entry in entries})
