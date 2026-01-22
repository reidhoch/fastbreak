"""Endpoint for fetching NBA draft combine non-stationary shooting results."""

from dataclasses import dataclass
from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.draft_combine_nonstationary_shooting import (
    DraftCombineNonstationaryShootingResponse,
)


@dataclass(frozen=True)
class DraftCombineNonstationaryShooting(
    Endpoint[DraftCombineNonstationaryShootingResponse]
):
    """Fetch NBA draft combine non-stationary shooting results.

    Includes off-dribble and on-the-move shooting drill results.

    Args:
        league_id: League identifier ("00" for NBA)
        season_year: Season year in YYYY-YY format (e.g., "2024-25")

    """

    path: ClassVar[str] = "draftcombinenonstationaryshooting"
    response_model: ClassVar[type[DraftCombineNonstationaryShootingResponse]] = (
        DraftCombineNonstationaryShootingResponse
    )

    league_id: str = "00"
    season_year: str = "2024-25"

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {
            "LeagueID": self.league_id,
            "SeasonYear": self.season_year,
        }
