"""Shot quality leaders endpoint."""

from dataclasses import dataclass
from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.shot_quality_leaders import ShotQualityLeadersResponse


@dataclass(frozen=True)
class ShotQualityLeaders(Endpoint[ShotQualityLeadersResponse]):
    """Fetch shot quality leaders - players ranked by shot quality metrics.

    Shot Difficulty measures the expected field goal percentage for the average NBA
    player, leveraging player tracking data to unlock new insights into how the shooter
    and the defense interact.


    Args:
        league_id: League identifier ("00" for NBA)
        season_type: Type of season ("Regular Season", "Playoffs")
        season_year: Season in YYYY-YY format (e.g., "2025-26")

    """

    path: ClassVar[str] = "shotqualityleaders"
    response_model: ClassVar[type[ShotQualityLeadersResponse]] = (
        ShotQualityLeadersResponse
    )

    league_id: str = "00"
    season_type: str = "Regular Season"
    season_year: str = "2025-26"

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {
            "LeagueID": self.league_id,
            "SeasonType": self.season_type,
            "Season": self.season_year,
        }
