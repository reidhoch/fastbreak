from typing import ClassVar

from fastbreak.endpoints.base import GameIdEndpoint
from fastbreak.models import BoxScoreMiscResponse


class BoxScoreMisc(GameIdEndpoint[BoxScoreMiscResponse]):
    """Fetch miscellaneous box score statistics for a game.

    This endpoint provides miscellaneous statistics including points
    in the paint, fast break points, second chance points, and points
    off turnovers for both player and team levels.
    """

    path: ClassVar[str] = "boxscoremiscv3"
    response_model: ClassVar[type[BoxScoreMiscResponse]] = BoxScoreMiscResponse
