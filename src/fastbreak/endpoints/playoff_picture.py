"""Endpoint for playoff picture data."""

from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.playoff_picture import PlayoffPictureResponse
from fastbreak.types import LeagueID


class PlayoffPicture(Endpoint[PlayoffPictureResponse]):
    """Get playoff picture including matchups, standings, and remaining games.

    This endpoint provides a complete view of the playoff race for both
    conferences, including current matchups, standings with clinch status,
    and remaining games.

    Args:
        league_id: League identifier ("00" for NBA)
        season_id: Season identifier in format "2YYYY" where YYYY is the
            starting year (e.g., "22023" for 2023-24 season)

    """

    path: ClassVar[str] = "playoffpicture"
    response_model: ClassVar[type[PlayoffPictureResponse]] = PlayoffPictureResponse

    league_id: LeagueID = "00"
    season_id: str = "22024"

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {
            "LeagueID": self.league_id,
            "SeasonID": self.season_id,
        }
