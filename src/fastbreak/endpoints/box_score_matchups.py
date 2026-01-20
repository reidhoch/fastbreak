from fastbreak.endpoints.base import GameEndpoint
from fastbreak.models import BoxScoreMatchupsResponse


class BoxScoreMatchups(GameEndpoint[BoxScoreMatchupsResponse]):
    """Fetch player-vs-player defensive matchup statistics for a game.

    This endpoint provides detailed defensive matchup data showing how
    each player performed when guarding specific opponents.
    """

    path = "boxscorematchupsv3"
    response_model = BoxScoreMatchupsResponse
