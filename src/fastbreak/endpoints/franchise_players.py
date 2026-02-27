"""Endpoint for fetching franchise player statistics."""

from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.franchise_players import FranchisePlayersResponse
from fastbreak.types import LeagueID, PerMode, SeasonType


class FranchisePlayers(Endpoint[FranchisePlayersResponse]):
    """Fetch all players who have played for a franchise with their stats.

    Args:
        league_id: League identifier ("00" for NBA)
        team_id: Team identifier (e.g., "1610612745" for Rockets)
        season_type: Type of season ("Regular Season", "Playoffs")
        per_mode: Stat aggregation mode ("PerGame", "Totals")

    """

    path: ClassVar[str] = "franchiseplayers"
    response_model: ClassVar[type[FranchisePlayersResponse]] = FranchisePlayersResponse

    team_id: int
    league_id: LeagueID = "00"
    season_type: SeasonType = "Regular Season"
    per_mode: PerMode = "PerGame"

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {
            "LeagueID": self.league_id,
            "TeamID": str(self.team_id),
            "SeasonType": self.season_type,
            "PerMode": self.per_mode,
        }
