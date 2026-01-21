from dataclasses import dataclass
from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models import BoxScorePlayerTrackResponse


@dataclass(frozen=True)
class BoxScorePlayerTrack(Endpoint[BoxScorePlayerTrackResponse]):
    """Fetch player tracking statistics for a game.

    This endpoint provides tracking data including player speed, distance
    traveled, touches, passes, and contested/uncontested shot breakdowns.
    """

    path: ClassVar[str] = "boxscoreplayertrackv3"
    response_model: ClassVar[type[BoxScorePlayerTrackResponse]] = (
        BoxScorePlayerTrackResponse
    )

    game_id: str

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {"GameID": self.game_id}
