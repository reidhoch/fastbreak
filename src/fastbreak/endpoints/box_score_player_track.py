from dataclasses import dataclass
from typing import ClassVar

from fastbreak.endpoints.base import GameIdEndpoint
from fastbreak.models import BoxScorePlayerTrackResponse


@dataclass(frozen=True)
class BoxScorePlayerTrack(GameIdEndpoint[BoxScorePlayerTrackResponse]):
    """Fetch player tracking statistics for a game.

    This endpoint provides tracking data including player speed, distance
    traveled, touches, passes, and contested/uncontested shot breakdowns.
    """

    path: ClassVar[str] = "boxscoreplayertrackv3"
    response_model: ClassVar[type[BoxScorePlayerTrackResponse]] = (
        BoxScorePlayerTrackResponse
    )
