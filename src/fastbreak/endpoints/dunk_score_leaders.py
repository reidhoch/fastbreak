"""Endpoint for fetching dunk score leaders."""

from dataclasses import dataclass
from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models import DunkScoreLeadersResponse


@dataclass(frozen=True)
class DunkScoreLeaders(Endpoint[DunkScoreLeadersResponse]):
    """Fetch dunk score data with optional filtering.

    Can filter by player, team, or game to get dunk analytics
    including scores, subscores, and biomechanical data.
    """

    path: ClassVar[str] = "dunkscoreleaders"
    response_model: ClassVar[type[DunkScoreLeadersResponse]] = DunkScoreLeadersResponse

    season: str = "2024-25"
    season_type: str = "Regular Season"
    league_id: str = "00"
    player_id: int | None = None
    team_id: int | None = None
    game_id: str | None = None

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        result = {
            "LeagueID": self.league_id,
            "SeasonYear": self.season,
            "SeasonType": self.season_type,
        }
        if self.player_id is not None:
            result["PlayerId"] = str(self.player_id)
        if self.team_id is not None:
            result["TeamId"] = str(self.team_id)
        if self.game_id is not None:
            result["GameId"] = self.game_id
        return result
