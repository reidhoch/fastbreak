"""Common player info endpoint."""

from typing import ClassVar

from fastbreak.endpoints.base import SimplePlayerEndpoint
from fastbreak.models.common_player_info import CommonPlayerInfoResponse


class CommonPlayerInfo(SimplePlayerEndpoint[CommonPlayerInfoResponse]):
    """Fetch detailed information for a specific player.

    Args:
        player_id: The NBA player ID
        league_id: League identifier ("00" for NBA)

    """

    path: ClassVar[str] = "commonplayerinfo"
    response_model: ClassVar[type[CommonPlayerInfoResponse]] = CommonPlayerInfoResponse
