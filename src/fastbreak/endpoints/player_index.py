"""Player Index endpoint for player directory information."""

from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.player_index import PlayerIndexResponse
from fastbreak.types import LeagueID, Season


class PlayerIndex(Endpoint[PlayerIndexResponse]):
    """Fetch player directory information for a season.

    Returns biographical, team, draft, and basic stat information
    for all players in the specified season.

    Args:
        league_id: League identifier ("00" for NBA)
        season: Season in YYYY-YY format (e.g., "2024-25")

    """

    path: ClassVar[str] = "playerindex"
    response_model: ClassVar[type[PlayerIndexResponse]] = PlayerIndexResponse

    league_id: LeagueID = "00"
    season: Season = "2024-25"

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {
            "LeagueID": self.league_id,
            "Season": self.season,
        }
