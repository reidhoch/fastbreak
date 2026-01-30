"""Endpoint for fetching team details and background information."""

from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.team_details import TeamDetailsResponse


class TeamDetails(Endpoint[TeamDetailsResponse]):
    """Fetch comprehensive team details and background information.

    Returns team background info (arena, coach, GM, owner), franchise history,
    social media links, championships, conference/division titles, Hall of Fame
    players, and retired jerseys.

    Args:
        team_id: NBA team ID (required)

    """

    path: ClassVar[str] = "teamdetails"
    response_model: ClassVar[type[TeamDetailsResponse]] = TeamDetailsResponse

    team_id: int

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {
            "TeamID": str(self.team_id),
        }
