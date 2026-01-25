from dataclasses import dataclass
from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.play_by_play import PlayByPlayResponse


@dataclass(frozen=True)
class PlayByPlay(Endpoint[PlayByPlayResponse]):
    """Fetch play-by-play data for a game.

    Returns all actions/events that occurred during the game,
    including shots, turnovers, fouls, substitutions, and more.
    """

    path: ClassVar[str] = "playbyplayv3"
    response_model: ClassVar[type[PlayByPlayResponse]] = PlayByPlayResponse

    game_id: str
    end_period: int = 0
    start_period: int = 0

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {
            "GameID": self.game_id,
            "EndPeriod": str(self.end_period),
            "StartPeriod": str(self.start_period),
        }
