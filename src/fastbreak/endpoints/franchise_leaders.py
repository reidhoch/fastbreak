"""Endpoint for fetching franchise all-time leaders."""

from dataclasses import dataclass
from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.franchise_leaders import FranchiseLeadersResponse


@dataclass(frozen=True)
class FranchiseLeaders(Endpoint[FranchiseLeadersResponse]):
    """Fetch franchise all-time leaders for a team.

    Args:
        league_id: League identifier ("00" for NBA)
        team_id: Team identifier (e.g., "1610612747" for Lakers)

    """

    path: ClassVar[str] = "franchiseleaders"
    response_model: ClassVar[type[FranchiseLeadersResponse]] = FranchiseLeadersResponse

    league_id: str = "00"
    team_id: str = "1610612747"

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {
            "LeagueID": self.league_id,
            "TeamID": self.team_id,
        }
