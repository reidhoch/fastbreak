"""Leverage leaders endpoint."""

from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.leverage_leaders import LeverageLeadersResponse
from fastbreak.types import LeagueID, Season, SeasonType


class LeverageLeaders(Endpoint[LeverageLeadersResponse]):
    """
    Leverage Score measures the impact each play has on a team's chance to win the game
    and distributes the credit for those plays to the offensive and defensive players
    involved using the NBA's real-time defensive matchups and expected field goal
    percentage to quantify each player's contributions.

    Args:
        league_id: League identifier ("00" for NBA)
        season_type: Type of season ("Regular Season", "Playoffs")
        season_year: Season in YYYY-YY format (e.g., "2024-25")

    """

    path: ClassVar[str] = "leverageleaders"
    response_model: ClassVar[type[LeverageLeadersResponse]] = LeverageLeadersResponse

    league_id: LeagueID = "00"
    season_type: SeasonType = "Regular Season"
    season_year: Season = "2024-25"

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {
            "LeagueID": self.league_id,
            "SeasonType": self.season_type,
            "Season": self.season_year,
        }
