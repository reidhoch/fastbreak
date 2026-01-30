"""Endpoint for fetching NBA franchise history."""

from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.franchise_history import FranchiseHistoryResponse
from fastbreak.types import LeagueID


class FranchiseHistory(Endpoint[FranchiseHistoryResponse]):
    """Fetch franchise history including active and defunct teams.

    Args:
        league_id: League identifier ("00" for NBA)

    """

    path: ClassVar[str] = "franchisehistory"
    response_model: ClassVar[type[FranchiseHistoryResponse]] = FranchiseHistoryResponse

    league_id: LeagueID = "00"

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {
            "LeagueID": self.league_id,
        }
