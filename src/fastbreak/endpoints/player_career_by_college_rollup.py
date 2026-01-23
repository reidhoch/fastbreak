"""Player career by college rollup endpoint for NBA API."""

from dataclasses import dataclass
from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.player_career_by_college_rollup import (
    PlayerCareerByCollegeRollupResponse,
)


@dataclass(frozen=True)
class PlayerCareerByCollegeRollup(Endpoint[PlayerCareerByCollegeRollupResponse]):
    """Fetch NBA player statistics rolled up by college and NCAA tournament region.

    Returns aggregated career statistics for NBA players grouped by their
    college's NCAA tournament region (East, Midwest, South, West) and seed.

    Args:
        league_id: League identifier ("00" for NBA)
        per_mode: Stat aggregation mode ("Totals", "PerGame")
        season_type: Type of season ("Regular Season", "Playoffs")
        season: Optional season filter in YYYY-YY format (e.g., "2024-25")

    """

    path: ClassVar[str] = "playercareerbycollegerollup"
    response_model: ClassVar[type[PlayerCareerByCollegeRollupResponse]] = (
        PlayerCareerByCollegeRollupResponse
    )

    league_id: str = "00"
    per_mode: str = "PerGame"
    season_type: str = "Regular Season"
    season: str | None = None

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        result = {
            "LeagueID": self.league_id,
            "PerMode": self.per_mode,
            "SeasonType": self.season_type,
        }
        if self.season is not None:
            result["Season"] = self.season
        return result
