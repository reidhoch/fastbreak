from fastbreak.endpoints.base import GameEndpoint
from fastbreak.models import BoxScoreAdvancedResponse


class BoxScoreAdvanced(GameEndpoint[BoxScoreAdvancedResponse]):
    """Fetch advanced box score statistics for a game.

    Returns advanced metrics like offensive/defensive rating, pace,
    usage percentage, true shooting percentage, and PIE for each player.
    """

    path = "boxscoreadvancedv3"
    response_model = BoxScoreAdvancedResponse
