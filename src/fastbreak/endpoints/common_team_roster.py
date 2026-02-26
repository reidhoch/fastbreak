"""Common team roster endpoint."""

from typing import ClassVar

from pydantic import Field

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.common_team_roster import CommonTeamRosterResponse
from fastbreak.seasons import get_season_from_date
from fastbreak.types import LeagueID, Season


class CommonTeamRoster(Endpoint[CommonTeamRosterResponse]):
    """Fetch team roster and coaching staff for a season.

    Args:
        team_id: Team identifier
        league_id: League identifier ("00" for NBA)
        season: Season in YYYY-YY format (e.g., "2024-25")

    """

    path: ClassVar[str] = "commonteamroster"
    response_model: ClassVar[type[CommonTeamRosterResponse]] = CommonTeamRosterResponse

    team_id: int
    league_id: LeagueID = "00"
    season: Season = Field(default_factory=get_season_from_date)

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {
            "TeamID": str(self.team_id),
            "LeagueID": self.league_id,
            "Season": self.season,
        }
