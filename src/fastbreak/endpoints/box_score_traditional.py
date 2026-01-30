from typing import ClassVar

from fastbreak.endpoints.base import GameIdEndpoint
from fastbreak.models import BoxScoreTraditionalResponse


class BoxScoreTraditional(GameIdEndpoint[BoxScoreTraditionalResponse]):
    """Fetch traditional box score statistics for a game.

    This endpoint provides standard box score statistics including
    field goals, three-pointers, free throws, rebounds, assists,
    steals, blocks, turnovers, fouls, points, and plus/minus.
    Also includes aggregated starters and bench statistics per team.
    """

    path: ClassVar[str] = "boxscoretraditionalv3"
    response_model: ClassVar[type[BoxScoreTraditionalResponse]] = (
        BoxScoreTraditionalResponse
    )
