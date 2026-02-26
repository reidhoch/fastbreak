"""Endpoint for fetching league leaders."""

from typing import ClassVar

from pydantic import Field

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.league_leaders import LeagueLeadersResponse
from fastbreak.seasons import get_season_from_date
from fastbreak.types import (
    LeagueID,
    PerMode,
    Scope,
    Season,
    SeasonType,
    StatCategoryAbbreviation,
)


class LeagueLeaders(Endpoint[LeagueLeadersResponse]):
    """Fetch league leaders for various statistical categories.

    Returns ranked player statistics for points, rebounds, assists, and other
    categories. Players can be filtered by scope (season, rookies) and status.

    Args:
        season: Season in YYYY-YY format (e.g., "2024-25")
        season_type: Type of season ("Regular Season", "Playoffs")
        per_mode: Stat aggregation mode ("PerGame", "Totals", "Per48")
        stat_category: Statistical category ("PTS", "REB", "AST", "STL", "BLK", etc.)
        scope: Player scope ("S" for season, "RS" for rookies)
        league_id: League identifier ("00" for NBA)
        active_flag: Filter for active players only

    """

    path: ClassVar[str] = "leagueleaders"
    response_model: ClassVar[type[LeagueLeadersResponse]] = LeagueLeadersResponse

    season: Season = Field(default_factory=get_season_from_date)
    season_type: SeasonType = "Regular Season"
    per_mode: PerMode = "PerGame"
    stat_category: StatCategoryAbbreviation = "PTS"
    scope: Scope = "S"
    league_id: LeagueID = "00"
    active_flag: str | None = None

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        result: dict[str, str] = {
            "Season": self.season,
            "SeasonType": self.season_type,
            "PerMode": self.per_mode,
            "StatCategory": self.stat_category,
            "Scope": self.scope,
            "LeagueID": self.league_id,
        }

        if self.active_flag is not None:
            result["ActiveFlag"] = self.active_flag

        return result
