from typing import ClassVar

from fastbreak.endpoints.base import GameIdEndpoint
from fastbreak.models import BoxScoreAdvancedResponse


class BoxScoreAdvanced(GameIdEndpoint[BoxScoreAdvancedResponse]):
    """Fetch advanced box score statistics for a game.

    Returns advanced metrics like offensive/defensive rating, pace,
    usage percentage, true shooting percentage, and PIE for each player.
    """

    path: ClassVar[str] = "boxscoreadvancedv3"
    response_model: ClassVar[type[BoxScoreAdvancedResponse]] = BoxScoreAdvancedResponse
