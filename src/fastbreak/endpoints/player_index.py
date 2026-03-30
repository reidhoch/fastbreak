"""Player Index endpoint for player directory information."""

from typing import ClassVar

from pydantic import Field

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.player_index import PlayerIndexResponse
from fastbreak.seasons import get_season_from_date
from fastbreak.types import LeagueID, Season, SeasonType


class PlayerIndex(Endpoint[PlayerIndexResponse]):
    """Fetch player directory information for a season.

    Returns biographical, team, draft, and basic stat information
    for all players in the specified season.

    Args:
        league_id: League identifier ("00" for NBA)
        season: Season in YYYY-YY format (e.g., "2024-25")
        season_type: Type of season ("Regular Season", "Playoffs", etc.)
        team_id: Filter by team ID (0 for all teams)
        country: Filter by country (e.g., "USA", "France")
        draft_year: Filter by draft year (e.g., 2023)
        draft_round: Filter by draft round (e.g., "1", "2")
        draft_pick: Filter by draft pick number (e.g., "1")
        height: Filter by height (e.g., "GT 6-6", "LT 6-0")
        weight: Filter by weight (e.g., "GT 250", "LT 200")
        historical: Include historical players (1 = all, 0 = current only)

    """

    path: ClassVar[str] = "playerindex"
    response_model: ClassVar[type[PlayerIndexResponse]] = PlayerIndexResponse

    league_id: LeagueID = "00"
    season: Season = Field(default_factory=get_season_from_date)
    season_type: SeasonType = "Regular Season"
    team_id: int = 0
    historical: int = 1

    country: str | None = None
    draft_year: int | None = None
    draft_round: str | None = None
    draft_pick: str | None = None
    height: str | None = None
    weight: str | None = None

    _OPTIONAL_PARAMS: ClassVar[dict[str, str]] = {
        "country": "Country",
        "draft_year": "DraftYear",
        "draft_round": "DraftRound",
        "draft_pick": "DraftPick",
        "height": "Height",
        "weight": "Weight",
    }

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        result: dict[str, str] = {
            "LeagueID": self.league_id,
            "Season": self.season,
            "SeasonType": self.season_type,
            "TeamID": str(self.team_id),
            "Historical": str(self.historical),
        }

        for attr, param_name in self._OPTIONAL_PARAMS.items():
            value = getattr(self, attr)
            if value is not None:
                result[param_name] = str(value)

        return result
