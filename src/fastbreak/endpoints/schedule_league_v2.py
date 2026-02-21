"""Endpoint for league schedule v2 data."""

from typing import ClassVar

from pydantic import Field

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.schedule_league_v2 import ScheduleLeagueV2Response
from fastbreak.types import LeagueID, Season
from fastbreak.utils import get_season_from_date


class ScheduleLeagueV2(Endpoint[ScheduleLeagueV2Response]):
    """Get the full league schedule for a season.

    This endpoint returns the complete season schedule with all games
    organized by date. Each game includes detailed information about
    teams, broadcasters, venue, and scoring leaders.

    Args:
        league_id: League identifier ("00" for NBA, "10" for WNBA, "15" for G-League)
        season: Season in YYYY-YY format (e.g., "2024-25")

    """

    path: ClassVar[str] = "scheduleleaguev2"
    response_model: ClassVar[type[ScheduleLeagueV2Response]] = ScheduleLeagueV2Response

    league_id: LeagueID = "00"
    season: Season = Field(default_factory=get_season_from_date)

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {
            "LeagueID": self.league_id,
            "Season": self.season,
        }
