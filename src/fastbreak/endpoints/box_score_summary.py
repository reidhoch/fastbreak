from dataclasses import dataclass
from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models import BoxScoreSummaryResponse


@dataclass(frozen=True)
class BoxScoreSummary(Endpoint[BoxScoreSummaryResponse]):
    """Fetch box score summary for a game.

    Returns game metadata, team info, officials, broadcasters,
    last five meetings, and pre/postgame charts.
    """

    path: ClassVar[str] = "boxscoresummaryv3"
    response_model: ClassVar[type[BoxScoreSummaryResponse]] = BoxScoreSummaryResponse

    game_id: str

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {"GameID": self.game_id}
