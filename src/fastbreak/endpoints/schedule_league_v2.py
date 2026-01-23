"""Endpoint for league schedule v2 data."""

from dataclasses import dataclass
from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.schedule_league_v2 import ScheduleLeagueV2Response


@dataclass(frozen=True)
class ScheduleLeagueV2(Endpoint[ScheduleLeagueV2Response]):
    """Get the full league schedule for a season.

    This endpoint returns the complete season schedule with all games
    organized by date. Each game includes detailed information about
    teams, broadcasters, venue, and scoring leaders.

    Args:
        league_id: League identifier ("00" for NBA, "10" for WNBA, "20" for G-League)
        season: Season in YYYY-YY format (e.g., "2024-25")

    """

    path: ClassVar[str] = "scheduleleaguev2"
    response_model: ClassVar[type[ScheduleLeagueV2Response]] = ScheduleLeagueV2Response

    league_id: str = "00"
    season: str = "2024-25"

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {
            "LeagueID": self.league_id,
            "Season": self.season,
        }
