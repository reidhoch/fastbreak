"""Player Fantasy Profile Bar Graph endpoint for fantasy statistics."""

from typing import ClassVar

from fastbreak.endpoints.base import PlayerSeasonEndpoint
from fastbreak.models.player_fantasy_profile_bar_graph import (
    PlayerFantasyProfileBarGraphResponse,
)


class PlayerFantasyProfileBarGraph(
    PlayerSeasonEndpoint[PlayerFantasyProfileBarGraphResponse]
):
    """Fetch fantasy statistics for a player.

    Returns season averages and last 5 games averages for fantasy points
    (FanDuel and NBA Fantasy) and underlying stats.

    Args:
        player_id: NBA player ID (required)
        league_id: League identifier ("00" for NBA)
        season: Season in YYYY-YY format (e.g., "2024-25")
        season_type: Type of season ("Regular Season", "Playoffs", "Pre Season")

    """

    path: ClassVar[str] = "playerfantasyprofilebargraph"
    response_model: ClassVar[type[PlayerFantasyProfileBarGraphResponse]] = (
        PlayerFantasyProfileBarGraphResponse
    )
