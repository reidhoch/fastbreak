"""Matchups rollup endpoint for NBA API."""

from typing import ClassVar

from pydantic import Field

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.matchups_rollup import MatchupsRollupResponse
from fastbreak.seasons import get_season_from_date
from fastbreak.types import LeagueID, PerMode, Season, SeasonType


class MatchupsRollup(Endpoint[MatchupsRollupResponse]):
    """Fetch matchup statistics rolled up by defender.

    Args:
        league_id: League identifier ("00" for NBA)
        season: Season in YYYY-YY format (e.g., "2024-25")
        season_type: Type of season ("Regular Season", "Playoffs")
        per_mode: Stat aggregation mode ("PerGame", "Totals")
        off_team_id: Offensive team ID
        def_team_id: Defensive team ID
        off_player_id: Optional offensive player ID filter (0 for all)
        def_player_id: Optional defensive player ID filter (0 for all)

    """

    path: ClassVar[str] = "matchupsrollup"
    response_model: ClassVar[type[MatchupsRollupResponse]] = MatchupsRollupResponse

    league_id: LeagueID = "00"
    season: Season = Field(default_factory=get_season_from_date)
    season_type: SeasonType = "Regular Season"
    per_mode: PerMode = "PerGame"
    off_team_id: int = 0
    def_team_id: int = 0
    off_player_id: int = 0
    def_player_id: int = 0

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {
            "LeagueID": self.league_id,
            "Season": self.season,
            "SeasonType": self.season_type,
            "PerMode": self.per_mode,
            "OffTeamID": str(self.off_team_id),
            "DefTeamID": str(self.def_team_id),
            "OffPlayerID": str(self.off_player_id),
            "DefPlayerID": str(self.def_player_id),
        }
