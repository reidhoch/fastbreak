"""League standings endpoint."""

from typing import ClassVar

from pydantic import Field

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.league_standings import LeagueStandingsResponse
from fastbreak.seasons import get_season_from_date
from fastbreak.types import LeagueID, Season, SeasonType


class LeagueStandings(Endpoint[LeagueStandingsResponse]):
    """Fetch NBA league standings.

    Args:
        season: Season in YYYY-YY format (e.g., "2024-25")
        season_type: Type of season ("Regular Season", "Playoffs", "Pre Season")
        league_id: League identifier ("00" for NBA)

    """

    path: ClassVar[str] = "leaguestandingsv3"
    response_model: ClassVar[type[LeagueStandingsResponse]] = LeagueStandingsResponse

    season: Season = Field(default_factory=get_season_from_date)
    season_type: SeasonType = "Regular Season"
    league_id: LeagueID = "00"

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {
            "LeagueID": self.league_id,
            "Season": self.season,
            "SeasonType": self.season_type,
        }
