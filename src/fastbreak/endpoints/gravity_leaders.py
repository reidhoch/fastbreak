from dataclasses import dataclass
from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models import GravityLeadersResponse


@dataclass
class GravityLeaders(Endpoint[GravityLeadersResponse]):
    """Fetch gravity leaders for a given season.

    Gravity measures how much defensive attention a player draws,
    based on how close defenders stay to them.
    """

    path: ClassVar[str] = "gravityleaders"
    response_model: ClassVar[type[GravityLeadersResponse]] = GravityLeadersResponse

    season: str = "2024-25"
    season_type: str = "Regular Season"
    league_id: str = "00"

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {
            "LeagueID": self.league_id,
            "Season": self.season,
            "SeasonType": self.season_type,
        }
