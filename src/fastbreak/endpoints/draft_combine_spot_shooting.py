"""Endpoint for fetching NBA draft combine spot shooting results."""

from dataclasses import dataclass
from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.draft_combine_spot_shooting import (
    DraftCombineSpotShootingResponse,
)


@dataclass(frozen=True)
class DraftCombineSpotShooting(Endpoint[DraftCombineSpotShootingResponse]):
    """Fetch NBA draft combine spot shooting results.

    Args:
        league_id: League identifier ("00" for NBA)
        season_year: Season year in YYYY-YY format (e.g., "2024-25")

    """

    path: ClassVar[str] = "draftcombinespotshooting"
    response_model: ClassVar[type[DraftCombineSpotShootingResponse]] = (
        DraftCombineSpotShootingResponse
    )

    league_id: str = "00"
    season_year: str = "2024-25"

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {
            "LeagueID": self.league_id,
            "SeasonYear": self.season_year,
        }
