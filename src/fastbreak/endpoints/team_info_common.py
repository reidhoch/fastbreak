"""Endpoint for fetching common team information."""

from dataclasses import dataclass
from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.team_info_common import TeamInfoCommonResponse


@dataclass(frozen=True)
class TeamInfoCommon(Endpoint[TeamInfoCommonResponse]):
    """Fetch basic team information and current season rankings.

    Returns team identity (city, name, conference, division), current
    win-loss record, season rankings for key stats, and available seasons.

    Args:
        team_id: NBA team ID (required)
        league_id: League identifier ("00" for NBA)

    """

    path: ClassVar[str] = "teaminfocommon"
    response_model: ClassVar[type[TeamInfoCommonResponse]] = TeamInfoCommonResponse

    team_id: int = 0
    league_id: str = "00"

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {
            "TeamID": str(self.team_id),
            "LeagueID": self.league_id,
        }
