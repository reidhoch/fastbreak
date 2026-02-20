"""Player Game Streak Finder endpoint for consecutive game streaks."""

from typing import ClassVar

from fastbreak.endpoints.base import SimplePlayerEndpoint
from fastbreak.models.player_game_streak_finder import PlayerGameStreakFinderResponse


class PlayerGameStreakFinder(SimplePlayerEndpoint[PlayerGameStreakFinderResponse]):
    """Fetch consecutive game streak information for a player.

    Returns details about game streaks including start/end dates,
    number of games, and whether the streak is still active.

    Args:
        player_id: NBA player ID (required)
        league_id: League identifier ("00" for NBA)

    """

    path: ClassVar[str] = "playergamestreakfinder"
    response_model: ClassVar[type[PlayerGameStreakFinderResponse]] = (
        PlayerGameStreakFinderResponse
    )
