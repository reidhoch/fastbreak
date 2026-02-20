"""Player Profile V2 endpoint for comprehensive player career statistics."""

from typing import ClassVar

from fastbreak.endpoints.base import PlayerPerModeEndpoint
from fastbreak.models.player_profile_v2 import PlayerProfileV2Response


class PlayerProfileV2(PlayerPerModeEndpoint[PlayerProfileV2Response]):
    """Fetch comprehensive career statistics for a player.

    Returns season-by-season and career totals for regular season, playoffs,
    All-Star games, college, and preseason. Also includes season rankings
    and statistical highs.

    Args:
        player_id: NBA player ID (required)
        league_id: League identifier ("00" for NBA)
        per_mode: Per mode ("PerGame", "Per36", "Totals")

    """

    path: ClassVar[str] = "playerprofilev2"
    response_model: ClassVar[type[PlayerProfileV2Response]] = PlayerProfileV2Response
