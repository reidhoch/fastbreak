"""Player career stats endpoint for NBA API."""

from typing import ClassVar

from fastbreak.endpoints.base import PlayerPerModeEndpoint
from fastbreak.models.player_career_stats import PlayerCareerStatsResponse


class PlayerCareerStats(PlayerPerModeEndpoint[PlayerCareerStatsResponse]):
    """Fetch comprehensive career statistics for a player.

    Returns season-by-season stats, career totals, rankings, and stat highs
    across regular season, playoffs, all-star games, college, and showcase.

    Args:
        player_id: The player's unique identifier
        league_id: League identifier ("00" for NBA)
        per_mode: Stat aggregation mode ("Totals", "PerGame", "Per36", etc.)

    """

    path: ClassVar[str] = "playercareerstats"
    response_model: ClassVar[type[PlayerCareerStatsResponse]] = (
        PlayerCareerStatsResponse
    )
