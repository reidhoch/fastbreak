"""Player Fantasy Profile Bar Graph endpoint for fantasy statistics."""

from dataclasses import dataclass
from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.player_fantasy_profile_bar_graph import (
    PlayerFantasyProfileBarGraphResponse,
)


@dataclass(frozen=True)
class PlayerFantasyProfileBarGraph(Endpoint[PlayerFantasyProfileBarGraphResponse]):
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

    player_id: str = ""
    league_id: str = "00"
    season: str = "2024-25"
    season_type: str = "Regular Season"

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {
            "PlayerID": self.player_id,
            "LeagueID": self.league_id,
            "Season": self.season,
            "SeasonType": self.season_type,
        }
