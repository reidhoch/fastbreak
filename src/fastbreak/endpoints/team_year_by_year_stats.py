"""Endpoint for fetching team historical year-by-year statistics."""

from dataclasses import dataclass
from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.team_year_by_year_stats import TeamYearByYearStatsResponse


@dataclass(frozen=True)
class TeamYearByYearStats(Endpoint[TeamYearByYearStatsResponse]):
    """Fetch historical season-by-season statistics for a franchise.

    Returns year-by-year stats including win-loss records, playoff results,
    conference/division rankings, and traditional statistics.

    Args:
        team_id: NBA team ID (required)
        season_type: Type of season ("Regular Season", "Playoffs", etc.)
        per_mode: Stat mode ("PerGame", "Totals")
        league_id: League identifier ("00" for NBA)

    """

    path: ClassVar[str] = "teamyearbyyearstats"
    response_model: ClassVar[type[TeamYearByYearStatsResponse]] = (
        TeamYearByYearStatsResponse
    )

    team_id: int = 0
    season_type: str = "Regular Season"
    per_mode: str = "PerGame"
    league_id: str = "00"

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {
            "TeamID": str(self.team_id),
            "SeasonType": self.season_type,
            "PerMode": self.per_mode,
            "LeagueID": self.league_id,
        }
