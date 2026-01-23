"""Player awards endpoint for NBA API."""

from dataclasses import dataclass
from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.player_awards import PlayerAwardsResponse


@dataclass(frozen=True)
class PlayerAwards(Endpoint[PlayerAwardsResponse]):
    """Fetch all awards for a specific player.

    Args:
        player_id: The player's unique identifier

    """

    path: ClassVar[str] = "playerawards"
    response_model: ClassVar[type[PlayerAwardsResponse]] = PlayerAwardsResponse

    player_id: int

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {
            "PlayerID": str(self.player_id),
        }
