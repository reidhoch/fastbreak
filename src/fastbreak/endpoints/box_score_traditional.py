from dataclasses import dataclass
from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models import BoxScoreTraditionalResponse


@dataclass
class BoxScoreTraditional(Endpoint[BoxScoreTraditionalResponse]):
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

    game_id: str

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {"GameID": self.game_id}
