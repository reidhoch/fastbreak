"""Endpoint for fetching NBA draft combine athletic drill results."""

from dataclasses import dataclass
from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.draft_combine_drill_results import (
    DraftCombineDrillResultsResponse,
)


@dataclass(frozen=True)
class DraftCombineDrillResults(Endpoint[DraftCombineDrillResultsResponse]):
    """Fetch NBA draft combine athletic drill results.

    Includes vertical leap, agility, sprint, and strength testing.

    Args:
        league_id: League identifier ("00" for NBA)
        season_year: Season year in YYYY-YY format (e.g., "2024-25")

    """

    path: ClassVar[str] = "draftcombinedrillresults"
    response_model: ClassVar[type[DraftCombineDrillResultsResponse]] = (
        DraftCombineDrillResultsResponse
    )

    league_id: str = "00"
    season_year: str = "2024-25"

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {
            "LeagueID": self.league_id,
            "SeasonYear": self.season_year,
        }
