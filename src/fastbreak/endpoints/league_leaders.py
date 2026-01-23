"""Endpoint for fetching league leaders."""

from dataclasses import dataclass
from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.league_leaders import LeagueLeadersResponse


@dataclass(frozen=True)
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

    season: str = "2024-25"
    season_type: str = "Regular Season"
    per_mode: str = "PerGame"
    stat_category: str = "PTS"
    scope: str = "S"
    league_id: str = "00"
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
