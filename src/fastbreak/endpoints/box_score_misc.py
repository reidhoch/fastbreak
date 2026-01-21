from dataclasses import dataclass
from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models import BoxScoreMiscResponse


@dataclass(frozen=True)
class BoxScoreMisc(Endpoint[BoxScoreMiscResponse]):
    """Fetch miscellaneous box score statistics for a game.

    This endpoint provides miscellaneous statistics including points
    in the paint, fast break points, second chance points, and points
    off turnovers for both player and team levels.
    """

    path: ClassVar[str] = "boxscoremiscv3"
    response_model: ClassVar[type[BoxScoreMiscResponse]] = BoxScoreMiscResponse

    game_id: str

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {"GameID": self.game_id}
