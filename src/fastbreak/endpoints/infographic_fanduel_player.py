"""Infographic FanDuel player endpoint."""

from typing import ClassVar

from fastbreak.endpoints.base import GameIdEndpoint
from fastbreak.models.infographic_fanduel_player import InfographicFanDuelPlayerResponse


class InfographicFanDuelPlayer(GameIdEndpoint[InfographicFanDuelPlayerResponse]):
    """Fetch FanDuel fantasy player statistics for a specific game.

    Returns fantasy scoring (FanDuel and NBA Fantasy points) along with
    standard box score statistics for all players in the game.

    Args:
        game_id: NBA game identifier (e.g., "0022500571")

    """

    path: ClassVar[str] = "infographicfanduelplayer"
    response_model: ClassVar[type[InfographicFanDuelPlayerResponse]] = (
        InfographicFanDuelPlayerResponse
    )
