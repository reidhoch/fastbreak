"""Leverage leaders endpoint."""

from dataclasses import dataclass
from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.leverage_leaders import LeverageLeadersResponse


@dataclass(frozen=True)
class LeverageLeaders(Endpoint[LeverageLeadersResponse]):
    """
    Leverage Score measures the impact each play has on a team's chance to win the game
    and distributes the credit for those plays to the offensive and defensive players
    involved using the NBA's real-time defensive matchups and expected field goal
    percentage to quantify each player's contributions.

    Args:
        league_id: League identifier ("00" for NBA)
        season_type: Type of season ("Regular Season", "Playoffs")
        season_year: Season in YYYY-YY format (e.g., "2025-26")

    """

    path: ClassVar[str] = "leverageleaders"
    response_model: ClassVar[type[LeverageLeadersResponse]] = LeverageLeadersResponse

    league_id: str = "00"
    season_type: str = "Regular Season"
    season_year: str = "2025-26"

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {
            "LeagueID": self.league_id,
            "SeasonType": self.season_type,
            "Season": self.season_year,
        }
