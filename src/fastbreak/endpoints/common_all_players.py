"""Common all players endpoint."""

from dataclasses import dataclass
from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.common_all_players import CommonAllPlayersResponse


@dataclass(frozen=True)
class CommonAllPlayers(Endpoint[CommonAllPlayersResponse]):
    """Fetch all players in the league.

    Args:
        league_id: League identifier ("00" for NBA)
        season: Season in YYYY-YY format (e.g., "2024-25")
        is_only_current_season: Whether to only include current season (1 or 0)

    """

    path: ClassVar[str] = "commonallplayers"
    response_model: ClassVar[type[CommonAllPlayersResponse]] = CommonAllPlayersResponse

    league_id: str = "00"
    season: str = "2024-25"
    is_only_current_season: int = 1

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {
            "LeagueID": self.league_id,
            "Season": self.season,
            "IsOnlyCurrentSeason": str(self.is_only_current_season),
        }
