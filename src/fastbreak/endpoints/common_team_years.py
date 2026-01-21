"""Common team years endpoint."""

from dataclasses import dataclass
from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.common_team_years import CommonTeamYearsResponse


@dataclass(frozen=True)
class CommonTeamYears(Endpoint[CommonTeamYearsResponse]):
    """Fetch all teams and their years of existence in a league.

    Args:
        league_id: League identifier ("00" for NBA)

    """

    path: ClassVar[str] = "commonteamyears"
    response_model: ClassVar[type[CommonTeamYearsResponse]] = CommonTeamYearsResponse

    league_id: str = "00"

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {
            "LeagueID": self.league_id,
        }
