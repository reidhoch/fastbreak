from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models import GravityLeadersResponse
from fastbreak.types import LeagueID, Season, SeasonType


class GravityLeaders(Endpoint[GravityLeadersResponse]):
    """Fetch gravity leaders for a given season.

    Gravity measures how much defensive attention a player draws,
    based on how close defenders stay to them.
    """

    path: ClassVar[str] = "gravityleaders"
    response_model: ClassVar[type[GravityLeadersResponse]] = GravityLeadersResponse

    season: Season = "2025-26"
    season_type: SeasonType = "Regular Season"
    league_id: LeagueID = "00"

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {
            "LeagueID": self.league_id,
            "Season": self.season,
            "SeasonType": self.season_type,
        }
