"""Endpoint for scoreboard v3 data."""

from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.scoreboard_v3 import ScoreboardV3Response
from fastbreak.types import LeagueID


class ScoreboardV3(Endpoint[ScoreboardV3Response]):
    """Get the daily scoreboard for a specific date.

    This endpoint returns all games for a given date with live scores,
    period breakdowns, game leaders, team season leaders, and broadcaster
    information.

    Args:
        league_id: League identifier ("00" for NBA, "10" for WNBA, "20" for G-League)
        game_date: Date in YYYY-MM-DD format (e.g., "2024-12-25")

    """

    path: ClassVar[str] = "scoreboardv3"
    response_model: ClassVar[type[ScoreboardV3Response]] = ScoreboardV3Response

    league_id: LeagueID = "00"
    game_date: str = ""

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {
            "LeagueID": self.league_id,
            "GameDate": self.game_date,
        }
