"""ScoreboardV2 endpoint for daily game scoreboard."""

from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.scoreboard_v2 import ScoreboardV2Response
from fastbreak.types import LeagueID


class ScoreboardV2(Endpoint[ScoreboardV2Response]):
    """Get the daily scoreboard for a specific date (V2 format).

    This endpoint returns all games for a given date with:
    - Game status and metadata
    - Quarter-by-quarter line scores
    - Season series standings between teams
    - Last meeting information
    - Conference standings for the date
    - Team statistical leaders (pts/reb/ast)

    Args:
        game_date: Date in YYYY-MM-DD format (e.g., "2024-12-25")
        league_id: League identifier ("00" for NBA, "10" for WNBA, "15" for G-League)
        day_offset: Offset from game_date in days (usually "0")

    Note:
        This is the V2 (tabular resultSets) format. For the newer V3 nested
        JSON format, use ScoreboardV3 instead.

    """

    path: ClassVar[str] = "scoreboardv2"
    response_model: ClassVar[type[ScoreboardV2Response]] = ScoreboardV2Response

    game_date: str = ""
    league_id: LeagueID = "00"
    day_offset: str = "0"

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {
            "GameDate": self.game_date,
            "LeagueID": self.league_id,
            "DayOffset": self.day_offset,
        }
