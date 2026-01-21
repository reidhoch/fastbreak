from dataclasses import dataclass
from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models import BoxScoreScoringResponse


@dataclass(frozen=True)
class BoxScoreScoring(Endpoint[BoxScoreScoringResponse]):
    """Fetch scoring distribution statistics for a game.

    This endpoint provides percentage breakdowns of how points are
    generated: shot type distribution, assisted vs unassisted, and
    scoring by play type (fast break, paint, off turnovers, etc.).
    """

    path: ClassVar[str] = "boxscorescoringv3"
    response_model: ClassVar[type[BoxScoreScoringResponse]] = BoxScoreScoringResponse

    game_id: str

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {"GameID": self.game_id}
