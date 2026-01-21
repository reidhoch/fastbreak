from dataclasses import dataclass
from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models import BoxScoreMatchupsResponse


@dataclass
class BoxScoreMatchups(Endpoint[BoxScoreMatchupsResponse]):
    """Fetch player-vs-player defensive matchup statistics for a game.

    This endpoint provides detailed defensive matchup data showing how
    each player performed when guarding specific opponents.
    """

    path: ClassVar[str] = "boxscorematchupsv3"
    response_model: ClassVar[type[BoxScoreMatchupsResponse]] = BoxScoreMatchupsResponse

    game_id: str

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {"GameID": self.game_id}
