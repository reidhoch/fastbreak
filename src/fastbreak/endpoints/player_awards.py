"""Player awards endpoint for NBA API."""

from typing import ClassVar

from fastbreak.endpoints.base import PlayerIdEndpoint
from fastbreak.models.player_awards import PlayerAwardsResponse


class PlayerAwards(PlayerIdEndpoint[PlayerAwardsResponse]):
    """Fetch all awards for a specific player.

    Args:
        player_id: The player's unique identifier

    """

    path: ClassVar[str] = "playerawards"
    response_model: ClassVar[type[PlayerAwardsResponse]] = PlayerAwardsResponse
