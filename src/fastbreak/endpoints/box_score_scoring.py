from fastbreak.endpoints.base import GameEndpoint
from fastbreak.models import BoxScoreScoringResponse


class BoxScoreScoring(GameEndpoint[BoxScoreScoringResponse]):
    """Fetch scoring distribution statistics for a game.

    This endpoint provides percentage breakdowns of how points are
    generated: shot type distribution, assisted vs unassisted, and
    scoring by play type (fast break, paint, off turnovers, etc.).
    """

    path = "boxscorescoringv3"
    response_model = BoxScoreScoringResponse
