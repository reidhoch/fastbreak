"""Endpoint for fetching team game logs with extended stats."""

from typing import ClassVar

from fastbreak.endpoints.base import TeamSeasonEndpoint
from fastbreak.models.team_game_logs import TeamGameLogsResponse


class TeamGameLogs(TeamSeasonEndpoint[TeamGameLogsResponse]):
    """Fetch extended game-by-game stats for a team's season.

    Returns traditional box score statistics with league-wide rankings
    for each game played. More comprehensive than TeamGameLog.

    Args:
        team_id: NBA team ID (required)
        season: Season in YYYY-YY format (e.g., "2024-25")
        season_type: Type of season ("Regular Season", "Playoffs", "Pre Season")
        league_id: League identifier ("00" for NBA)

    """

    path: ClassVar[str] = "teamgamelogs"
    response_model: ClassVar[type[TeamGameLogsResponse]] = TeamGameLogsResponse
