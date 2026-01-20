from fastbreak.endpoints.base import GameEndpoint
from fastbreak.models import BoxScorePlayerTrackResponse


class BoxScorePlayerTrack(GameEndpoint[BoxScorePlayerTrackResponse]):
    """Fetch player tracking statistics for a game.

    This endpoint provides tracking data including player speed, distance
    traveled, touches, passes, and contested/uncontested shot breakdowns.
    """

    path = "boxscoreplayertrackv3"
    response_model = BoxScorePlayerTrackResponse
