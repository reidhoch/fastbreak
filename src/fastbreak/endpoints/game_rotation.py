"""Endpoint for fetching game rotation data."""

from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.game_rotation import GameRotationResponse
from fastbreak.types import LeagueID


class GameRotation(Endpoint[GameRotationResponse]):
    """Fetch player rotation data for a game.

    Returns substitution patterns showing when each player checked in/out
    and their stats during each stint.

    Args:
        game_id: NBA game identifier (e.g., "0022500571")
        league_id: League identifier ("00" for NBA)

    """

    path: ClassVar[str] = "gamerotation"
    response_model: ClassVar[type[GameRotationResponse]] = GameRotationResponse

    game_id: str
    league_id: LeagueID = "00"

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {
            "GameID": self.game_id,
            "LeagueID": self.league_id,
        }
