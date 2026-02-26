"""Endpoint for international league schedule v2 data."""

from typing import ClassVar

from pydantic import Field

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.schedule_league_v2_int import ScheduleLeagueV2IntResponse
from fastbreak.seasons import get_season_from_date
from fastbreak.types import LeagueID, Season


class ScheduleLeagueV2Int(Endpoint[ScheduleLeagueV2IntResponse]):
    """Get the full league schedule for a season (international version).

    This endpoint returns the complete season schedule with all games
    organized by date, optimized for international audiences. It includes
    region-specific broadcaster information and a master broadcaster list.

    Differences from ScheduleLeagueV2:
    - Includes broadcasterList with all available broadcasters
    - Uses nationalTvBroadcasters instead of nationalBroadcasters
    - Broadcaster objects include regionId and localizationRegion fields

    Args:
        league_id: League identifier ("00" for NBA, "10" for WNBA, "15" for G-League)
        season: Season in YYYY-YY format (e.g., "2024-25")

    """

    path: ClassVar[str] = "scheduleleaguev2int"
    response_model: ClassVar[type[ScheduleLeagueV2IntResponse]] = (
        ScheduleLeagueV2IntResponse
    )

    league_id: LeagueID = "00"
    season: Season = Field(default_factory=get_season_from_date)

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {
            "LeagueID": self.league_id,
            "Season": self.season,
        }
