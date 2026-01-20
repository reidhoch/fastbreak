"""League standings endpoint."""

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.league_standings import LeagueStandingsResponse


class LeagueStandings(Endpoint[LeagueStandingsResponse]):
    """Fetch NBA league standings.

    Args:
        season: Season in YYYY-YY format (e.g., "2024-25")
        season_type: Type of season ("Regular Season", "Playoffs", "Pre Season")
        league_id: League identifier ("00" for NBA)

    """

    path = "leaguestandingsv3"
    response_model = LeagueStandingsResponse

    def __init__(
        self,
        season: str = "2024-25",
        season_type: str = "Regular Season",
        league_id: str = "00",
    ) -> None:
        self.season = season
        self.season_type = season_type
        self.league_id = league_id

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {
            "LeagueID": self.league_id,
            "Season": self.season,
            "SeasonType": self.season_type,
        }
