"""Endpoint for fetching league-wide shot chart data."""

from dataclasses import dataclass
from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.shot_chart_leaguewide import ShotChartLeaguewideResponse


@dataclass(frozen=True)
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

    league_id: str = "00"
    season: str = "2024-25"

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {
            "LeagueID": self.league_id,
            "Season": self.season,
        }
