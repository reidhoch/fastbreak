"""Common player info endpoint."""

from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.common_player_info import CommonPlayerInfoResponse
from fastbreak.types import LeagueID


class CommonPlayerInfo(Endpoint[CommonPlayerInfoResponse]):
    """Fetch detailed information for a specific player.

    Args:
        player_id: The NBA player ID
        league_id: League identifier ("00" for NBA)

    """

    path: ClassVar[str] = "commonplayerinfo"
    response_model: ClassVar[type[CommonPlayerInfoResponse]] = CommonPlayerInfoResponse

    player_id: int
    league_id: LeagueID = "00"

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {
            "PlayerID": str(self.player_id),
            "LeagueID": self.league_id,
        }
