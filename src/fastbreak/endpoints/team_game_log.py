"""Endpoint for fetching team game logs."""

from typing import ClassVar

from fastbreak.endpoints.base import TeamSeasonEndpoint
from fastbreak.models.team_game_log import TeamGameLogResponse


class TeamGameLog(TeamSeasonEndpoint[TeamGameLogResponse]):
    """Fetch game-by-game stats for a team's season.

    Returns traditional box score statistics for each game played,
    along with running win-loss record.

    Args:
        team_id: NBA team ID (required)
        season: Season in YYYY-YY format (e.g., "2024-25")
        season_type: Type of season ("Regular Season", "Playoffs", "Pre Season")
        league_id: League identifier ("00" for NBA)

    """

    path: ClassVar[str] = "teamgamelog"
    response_model: ClassVar[type[TeamGameLogResponse]] = TeamGameLogResponse
