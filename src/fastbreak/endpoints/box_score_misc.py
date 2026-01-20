from fastbreak.endpoints.base import GameEndpoint
from fastbreak.models import BoxScoreMiscResponse


class BoxScoreMisc(GameEndpoint[BoxScoreMiscResponse]):
    """Fetch miscellaneous box score statistics for a game.

    This endpoint provides miscellaneous statistics including points
    in the paint, fast break points, second chance points, and points
    off turnovers for both player and team levels.
    """

    path = "boxscoremiscv3"
    response_model = BoxScoreMiscResponse
