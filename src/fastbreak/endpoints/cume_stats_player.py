"""Endpoint for fetching cumulative player stats."""

from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.cume_stats_player import CumeStatsPlayerResponse
from fastbreak.types import LeagueID, SeasonType


class CumeStatsPlayer(Endpoint[CumeStatsPlayerResponse]):
    """Fetch cumulative player stats for specific games.

    Args:
        league_id: League identifier ("00" for NBA)
        season: Season in YYYY format (e.g., "2025")
        season_type: Type of season ("Regular Season", "Playoffs", "Pre Season")
        player_id: The player's unique identifier
        game_ids: Comma-separated list of game IDs to include

    """

    path: ClassVar[str] = "cumestatsplayer"
    response_model: ClassVar[type[CumeStatsPlayerResponse]] = CumeStatsPlayerResponse

    player_id: int
    league_id: LeagueID = "00"
    season: str = "2025"
    season_type: SeasonType = "Regular Season"
    game_ids: str = ""

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {
            "LeagueID": self.league_id,
            "Season": self.season,
            "SeasonType": self.season_type,
            "PlayerID": str(self.player_id),
            "GameIDs": self.game_ids,
        }
