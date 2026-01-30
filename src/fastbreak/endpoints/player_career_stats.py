"""Player career stats endpoint for NBA API."""

from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.player_career_stats import PlayerCareerStatsResponse
from fastbreak.types import LeagueID, PerMode


class PlayerCareerStats(Endpoint[PlayerCareerStatsResponse]):
    """Fetch comprehensive career statistics for a player.

    Returns season-by-season stats, career totals, rankings, and stat highs
    across regular season, playoffs, all-star games, college, and showcase.

    Args:
        player_id: The player's unique identifier
        league_id: League identifier ("00" for NBA)
        per_mode: Stat aggregation mode ("Totals", "PerGame", "Per36")

    """

    path: ClassVar[str] = "playercareerstats"
    response_model: ClassVar[type[PlayerCareerStatsResponse]] = (
        PlayerCareerStatsResponse
    )

    player_id: int
    league_id: LeagueID = "00"
    per_mode: PerMode = "PerGame"

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {
            "PlayerID": str(self.player_id),
            "LeagueID": self.league_id,
            "PerMode": self.per_mode,
        }
