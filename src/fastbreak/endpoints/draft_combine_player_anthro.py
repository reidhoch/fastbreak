"""Endpoint for fetching NBA draft combine player anthropometric data."""

from dataclasses import dataclass
from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.draft_combine_player_anthro import (
    DraftCombinePlayerAnthroResponse,
)


@dataclass(frozen=True)
class DraftCombinePlayerAnthro(Endpoint[DraftCombinePlayerAnthroResponse]):
    """Fetch NBA draft combine player anthropometric measurements.

    Args:
        league_id: League identifier ("00" for NBA)
        season_year: Season year in YYYY-YY format (e.g., "2024-25")

    """

    path: ClassVar[str] = "draftcombineplayeranthro"
    response_model: ClassVar[type[DraftCombinePlayerAnthroResponse]] = (
        DraftCombinePlayerAnthroResponse
    )

    league_id: str = "00"
    season_year: str = "2024-25"

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {
            "LeagueID": self.league_id,
            "SeasonYear": self.season_year,
        }
