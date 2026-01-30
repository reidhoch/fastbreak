"""Player Game Logs endpoint for extended game statistics with rankings."""

from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.player_game_logs import PlayerGameLogsResponse
from fastbreak.types import LeagueID, Season, SeasonType


class PlayerGameLogs(Endpoint[PlayerGameLogsResponse]):
    """Fetch extended game-by-game statistics for a player.

    Returns traditional box score stats plus rankings and fantasy points
    for each game played in a season.

    Args:
        player_id: NBA player ID (required)
        league_id: League identifier ("00" for NBA)
        season: Season in YYYY-YY format (e.g., "2024-25")
        season_type: Type of season ("Regular Season", "Playoffs", "Pre Season")

    """

    path: ClassVar[str] = "playergamelogs"
    response_model: ClassVar[type[PlayerGameLogsResponse]] = PlayerGameLogsResponse

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
