"""Endpoint for fetching team game logs."""

from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.team_game_log import TeamGameLogResponse
from fastbreak.types import LeagueID, Season, SeasonType


class TeamGameLog(Endpoint[TeamGameLogResponse]):
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

    team_id: int
    season: Season = "2024-25"
    season_type: SeasonType = "Regular Season"
    league_id: LeagueID = "00"

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {
            "TeamID": str(self.team_id),
            "Season": self.season,
            "SeasonType": self.season_type,
            "LeagueID": self.league_id,
        }
