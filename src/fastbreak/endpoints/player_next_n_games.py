"""Player Next N Games endpoint for upcoming game schedule."""

from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.player_next_n_games import PlayerNextNGamesResponse
from fastbreak.types import LeagueID, Season, SeasonType


class PlayerNextNGames(Endpoint[PlayerNextNGamesResponse]):
    """Fetch upcoming games for a player.

    Returns schedule information for the next N games including
    both teams and game times.

    Args:
        player_id: NBA player ID (required)
        league_id: League identifier ("00" for NBA)
        season: Season in YYYY-YY format (e.g., "2024-25")
        season_type: Type of season ("Regular Season", "Playoffs", "Pre Season")
        number_of_games: Number of upcoming games to return

    """

    path: ClassVar[str] = "playernextngames"
    response_model: ClassVar[type[PlayerNextNGamesResponse]] = PlayerNextNGamesResponse

    player_id: str
    league_id: LeagueID = "00"
    season: Season = "2024-25"
    season_type: SeasonType = "Regular Season"
    number_of_games: str = "10"

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {
            "PlayerID": self.player_id,
            "LeagueID": self.league_id,
            "Season": self.season,
            "SeasonType": self.season_type,
            "NumberOfGames": self.number_of_games,
        }
