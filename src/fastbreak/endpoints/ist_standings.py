"""IST (In-Season Tournament) standings endpoint."""

from dataclasses import dataclass
from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.ist_standings import IstStandingsResponse


@dataclass(frozen=True)
class IstStandings(Endpoint[IstStandingsResponse]):
    """Fetch In-Season Tournament (NBA Cup) standings.

    Returns group standings, clinch status, and game results for all teams
    participating in the In-Season Tournament.

    Args:
        league_id: League identifier ("00" for NBA)
        season: Season in YYYY-YY format (e.g., "2024-25")
        section: Standings section to retrieve (e.g., "group")

    """

    path: ClassVar[str] = "iststandings"
    response_model: ClassVar[type[IstStandingsResponse]] = IstStandingsResponse

    league_id: str = "00"
    season: str = "2024-25"
    section: str = "group"

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {
            "LeagueID": self.league_id,
            "Season": self.season,
            "Section": self.section,
        }
