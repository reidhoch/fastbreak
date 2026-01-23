"""Endpoint for international league schedule v2 data."""

from dataclasses import dataclass
from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.schedule_league_v2_int import ScheduleLeagueV2IntResponse


@dataclass(frozen=True)
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
        league_id: League identifier ("00" for NBA, "10" for WNBA, "20" for G-League)
        season: Season in YYYY-YY format (e.g., "2024-25")

    """

    path: ClassVar[str] = "scheduleleaguev2int"
    response_model: ClassVar[type[ScheduleLeagueV2IntResponse]] = (
        ScheduleLeagueV2IntResponse
    )

    league_id: str = "00"
    season: str = "2024-25"

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {
            "LeagueID": self.league_id,
            "Season": self.season,
        }
