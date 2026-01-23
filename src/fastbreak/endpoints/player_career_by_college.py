"""Player career by college endpoint for NBA API."""

from dataclasses import dataclass
from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.player_career_by_college import PlayerCareerByCollegeResponse


@dataclass(frozen=True)
class PlayerCareerByCollege(Endpoint[PlayerCareerByCollegeResponse]):
    """Fetch career statistics for all NBA players from a specific college.

    Args:
        college: The college name (e.g., "Duke", "Kentucky")
        league_id: League identifier ("00" for NBA)
        per_mode: Stat aggregation mode ("Totals", "PerGame")
        season_type: Type of season ("Regular Season", "Playoffs")
        season: Optional season filter in YYYY-YY format (e.g., "2024-25")

    """

    path: ClassVar[str] = "playercareerbycollege"
    response_model: ClassVar[type[PlayerCareerByCollegeResponse]] = (
        PlayerCareerByCollegeResponse
    )

    college: str
    league_id: str = "00"
    per_mode: str = "Totals"
    season_type: str = "Regular Season"
    season: str | None = None

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        result = {
            "College": self.college,
            "LeagueID": self.league_id,
            "PerMode": self.per_mode,
            "SeasonType": self.season_type,
        }
        if self.season is not None:
            result["Season"] = self.season
        return result
