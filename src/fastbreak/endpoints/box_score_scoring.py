from typing import ClassVar

from fastbreak.endpoints.base import GameIdEndpoint
from fastbreak.models import BoxScoreScoringResponse


class BoxScoreScoring(GameIdEndpoint[BoxScoreScoringResponse]):
    """Fetch scoring distribution statistics for a game.

    This endpoint provides percentage breakdowns of how points are
    generated: shot type distribution, assisted vs unassisted, and
    scoring by play type (fast break, paint, off turnovers, etc.).
    """

    path: ClassVar[str] = "boxscorescoringv3"
    response_model: ClassVar[type[BoxScoreScoringResponse]] = BoxScoreScoringResponse
