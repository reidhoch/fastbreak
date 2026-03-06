"""Shot quality leaders endpoint."""

from typing import ClassVar

from pydantic import Field

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.shot_quality_leaders import ShotQualityLeadersResponse
from fastbreak.seasons import get_season_from_date
from fastbreak.types import LeagueID, Season, SeasonType


class ShotQualityLeaders(Endpoint[ShotQualityLeadersResponse]):
    """Fetch shot quality leaders - players ranked by shot quality metrics.

    Shot Difficulty measures the expected field goal percentage for the average NBA
    player, leveraging player tracking data to unlock new insights into how the shooter
    and the defense interact.


    Args:
        league_id: League identifier ("00" for NBA)
        season_type: Type of season ("Regular Season", "Playoffs")
        season_year: Season in YYYY-YY format (e.g., "2024-25")

    """

    path: ClassVar[str] = "shotqualityleaders"
    response_model: ClassVar[type[ShotQualityLeadersResponse]] = (
        ShotQualityLeadersResponse
    )

    league_id: LeagueID = "00"
    season_type: SeasonType = "Regular Season"
    season_year: Season = Field(default_factory=get_season_from_date)

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {
            "LeagueID": self.league_id,
            "SeasonType": self.season_type,
            "Season": self.season_year,
        }
