"""Player Game Log endpoint for individual player game statistics."""

from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.player_game_log import PlayerGameLogResponse
from fastbreak.types import LeagueID, Season, SeasonType


class PlayerGameLog(Endpoint[PlayerGameLogResponse]):
    """Fetch game-by-game statistics for a player.

    Returns traditional box score stats for each game played in a season.

    Args:
        player_id: NBA player ID (required)
        league_id: League identifier ("00" for NBA)
        season: Season in YYYY-YY format (e.g., "2024-25")
        season_type: Type of season ("Regular Season", "Playoffs", "Pre Season")

    """

    path: ClassVar[str] = "playergamelog"
    response_model: ClassVar[type[PlayerGameLogResponse]] = PlayerGameLogResponse

    player_id: str
    league_id: LeagueID = "00"
    season: Season = "2024-25"
    season_type: SeasonType = "Regular Season"

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {
            "PlayerID": self.player_id,
            "LeagueID": self.league_id,
            "Season": self.season,
            "SeasonType": self.season_type,
        }
