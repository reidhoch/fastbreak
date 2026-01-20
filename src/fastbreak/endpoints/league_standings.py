"""League standings endpoint."""

from dataclasses import dataclass

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.league_standings import LeagueStandingsResponse


@dataclass
class LeagueStandings(Endpoint[LeagueStandingsResponse]):
    """Fetch NBA league standings.

    Args:
        season_year: Season in YYYY-YY format (e.g., "2024-25")
        season_type: Type of season ("Regular Season", "Playoffs", "Pre Season")
        league_id: League identifier ("00" for NBA)

    """

    path: str = "leaguestandingsv3"
    response_model = LeagueStandingsResponse

    season: str = "2025-26"
    season_type: str = "Regular Season"
    league_id: str = "00"

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {
            "LeagueID": self.league_id,
            "Season": self.season,
            "SeasonType": self.season_type,
        }
