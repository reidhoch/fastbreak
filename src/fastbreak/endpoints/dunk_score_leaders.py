"""Endpoint for fetching dunk score leaders."""

from typing import ClassVar

from pydantic import Field

from fastbreak.endpoints.base import Endpoint
from fastbreak.models import DunkScoreLeadersResponse
from fastbreak.seasons import get_season_from_date
from fastbreak.types import LeagueID, Season, SeasonType


class DunkScoreLeaders(Endpoint[DunkScoreLeadersResponse]):
    """Fetch dunk score data with optional filtering.

    Can filter by player, team, or game to get dunk analytics
    including scores, subscores, and biomechanical data.
    """

    path: ClassVar[str] = "dunkscoreleaders"
    response_model: ClassVar[type[DunkScoreLeadersResponse]] = DunkScoreLeadersResponse

    season: Season = Field(default_factory=get_season_from_date)
    season_type: SeasonType = "Regular Season"
    league_id: LeagueID = "00"
    player_id: int | None = None
    team_id: int | None = None
    game_id: str | None = None

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        result = {
            "LeagueID": self.league_id,
            "Season": self.season,
            "SeasonType": self.season_type,
        }
        if self.player_id is not None:
            result["PlayerId"] = str(self.player_id)
        if self.team_id is not None:
            result["TeamId"] = str(self.team_id)
        if self.game_id is not None:
            result["GameId"] = self.game_id
        return result
