"""All-time leaders grids endpoint."""

from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.all_time_leaders import AllTimeLeadersResponse
from fastbreak.types import LeagueID, PerMode, SeasonType


class AllTimeLeadersGrids(Endpoint[AllTimeLeadersResponse]):
    """Fetch all-time NBA statistical leaders.

    Args:
        league_id: League identifier ("00" for NBA)
        season_type: Type of season ("Regular Season", "Playoffs")
        per_mode: Stat aggregation mode ("PerGame", "Totals")
        top_x: Number of leaders to return per category

    """

    path: ClassVar[str] = "alltimeleadersgrids"
    response_model: ClassVar[type[AllTimeLeadersResponse]] = AllTimeLeadersResponse

    league_id: LeagueID = "00"
    season_type: SeasonType = "Regular Season"
    per_mode: PerMode = "PerGame"
    top_x: int = 10

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {
            "LeagueID": self.league_id,
            "SeasonType": self.season_type,
            "PerMode": self.per_mode,
            "TopX": str(self.top_x),
        }
