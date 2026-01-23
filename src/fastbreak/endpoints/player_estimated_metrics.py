"""Player Estimated Metrics endpoint for estimated advanced statistics."""

from dataclasses import dataclass
from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.player_estimated_metrics import PlayerEstimatedMetricsResponse


@dataclass(frozen=True)
class PlayerEstimatedMetrics(Endpoint[PlayerEstimatedMetricsResponse]):
    """Fetch estimated advanced metrics for all players in the league.

    Returns estimated offensive/defensive ratings, efficiency percentages,
    pace, and league-wide rankings for each player.

    Args:
        league_id: League identifier ("00" for NBA)
        season: Season in YYYY-YY format (e.g., "2024-25")
        season_type: Type of season ("Regular Season", "Playoffs", "Pre Season")

    """

    path: ClassVar[str] = "playerestimatedmetrics"
    response_model: ClassVar[type[PlayerEstimatedMetricsResponse]] = (
        PlayerEstimatedMetricsResponse
    )

    league_id: str = "00"
    season: str = "2024-25"
    season_type: str = "Regular Season"

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {
            "LeagueID": self.league_id,
            "Season": self.season,
            "SeasonType": self.season_type,
        }
