from typing import ClassVar

from fastbreak.endpoints.base import GameIdEndpoint
from fastbreak.models import BoxScoreMatchupsResponse


class BoxScoreMatchups(GameIdEndpoint[BoxScoreMatchupsResponse]):
    """Fetch player-vs-player defensive matchup statistics for a game.

    This endpoint provides detailed defensive matchup data showing how
    each player performed when guarding specific opponents.
    """

    path: ClassVar[str] = "boxscorematchupsv3"
    response_model: ClassVar[type[BoxScoreMatchupsResponse]] = BoxScoreMatchupsResponse
