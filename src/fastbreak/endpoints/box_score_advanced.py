from dataclasses import dataclass
from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models import BoxScoreAdvancedResponse


@dataclass
class BoxScoreAdvanced(Endpoint[BoxScoreAdvancedResponse]):
    """Fetch advanced box score statistics for a game.

    Returns advanced metrics like offensive/defensive rating, pace,
    usage percentage, true shooting percentage, and PIE for each player.
    """

    path: ClassVar[str] = "boxscoreadvancedv3"
    response_model: ClassVar[type[BoxScoreAdvancedResponse]] = BoxScoreAdvancedResponse

    game_id: str

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {"GameID": self.game_id}
