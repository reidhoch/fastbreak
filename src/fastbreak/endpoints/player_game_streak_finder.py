"""Player Game Streak Finder endpoint for consecutive game streaks."""

from dataclasses import dataclass
from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.player_game_streak_finder import PlayerGameStreakFinderResponse


@dataclass(frozen=True)
class PlayerGameStreakFinder(Endpoint[PlayerGameStreakFinderResponse]):
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

    player_id: str = ""
    league_id: str = "00"

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {
            "PlayerID": self.player_id,
            "LeagueID": self.league_id,
        }
