"""Endpoint for fetching league-wide shot chart data."""

from typing import ClassVar

from pydantic import Field

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.shot_chart_leaguewide import ShotChartLeaguewideResponse
from fastbreak.types import LeagueID, Season
from fastbreak.utils import get_season_from_date


class ShotChartLeaguewide(Endpoint[ShotChartLeaguewideResponse]):
    """Fetch league-wide shot chart statistics by zone.

    Args:
        league_id: League identifier ("00" for NBA)
        season: Season in YYYY-YY format (e.g., "2024-25")

    """

    path: ClassVar[str] = "shotchartleaguewide"
    response_model: ClassVar[type[ShotChartLeaguewideResponse]] = (
        ShotChartLeaguewideResponse
    )

    league_id: LeagueID = "00"
    season: Season = Field(default_factory=get_season_from_date)

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {
            "LeagueID": self.league_id,
            "Season": self.season,
        }
