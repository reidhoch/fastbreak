"""Endpoint for fetching team estimated advanced metrics."""

from typing import ClassVar

from pydantic import Field

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.team_estimated_metrics import TeamEstimatedMetricsResponse
from fastbreak.seasons import get_season_from_date
from fastbreak.types import LeagueID, Season, SeasonType


class TeamEstimatedMetrics(Endpoint[TeamEstimatedMetricsResponse]):
    """Fetch estimated advanced metrics for all teams in the league.

    Returns estimated offensive/defensive ratings, efficiency percentages,
    pace, and league-wide rankings for all 30 teams.

    Args:
        league_id: League identifier ("00" for NBA)
        season: Season in YYYY-YY format (e.g., "2024-25")
        season_type: Type of season ("Regular Season", "Playoffs", "Pre Season")

    """

    path: ClassVar[str] = "teamestimatedmetrics"
    response_model: ClassVar[type[TeamEstimatedMetricsResponse]] = (
        TeamEstimatedMetricsResponse
    )

    league_id: LeagueID = "00"
    season: Season = Field(default_factory=get_season_from_date)
    season_type: SeasonType = "Regular Season"

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {
            "LeagueID": self.league_id,
            "Season": self.season,
            "SeasonType": self.season_type,
        }
