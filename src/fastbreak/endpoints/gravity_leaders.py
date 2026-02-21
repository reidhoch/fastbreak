from typing import ClassVar

from pydantic import Field

from fastbreak.endpoints.base import Endpoint
from fastbreak.models import GravityLeadersResponse
from fastbreak.types import LeagueID, Season, SeasonType
from fastbreak.utils import get_season_from_date


class GravityLeaders(Endpoint[GravityLeadersResponse]):
    """Fetch gravity leaders for a given season.

    Gravity measures how much defensive attention a player draws,
    based on how close defenders stay to them.

    Args:
        season: Season in YYYY-YY format (e.g., "2024-25")
        season_type: Type of season ("Regular Season", "Playoffs", etc.)
        league_id: League identifier ("00" for NBA)

    """

    path: ClassVar[str] = "gravityleaders"
    response_model: ClassVar[type[GravityLeadersResponse]] = GravityLeadersResponse

    season: Season = Field(default_factory=get_season_from_date)
    season_type: SeasonType = "Regular Season"
    league_id: LeagueID = "00"

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {
            "LeagueID": self.league_id,
            "Season": self.season,
            "SeasonType": self.season_type,
        }
