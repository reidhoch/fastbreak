"""League dashboard team stats endpoint."""

from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.league_dash_team_stats import LeagueDashTeamStatsResponse
from fastbreak.types import LeagueID, MeasureType, PerMode, Season, SeasonType


class LeagueDashTeamStats(Endpoint[LeagueDashTeamStatsResponse]):
    """Fetch league-wide team statistics dashboard.

    Returns comprehensive statistics for all teams across the league,
    with options for different stat types, time periods, and filters.

    Args:
        season: Season in YYYY-YY format (e.g., "2024-25")
        season_type: Type of season ("Regular Season", "Playoffs", etc.)
        per_mode: Stat aggregation mode ("PerGame", "Totals", "Per36", etc.)
        measure_type: Type of stats ("Base", "Advanced", "Misc", etc.)
        league_id: League identifier ("00" for NBA)

    """

    path: ClassVar[str] = "leaguedashteamstats"
    response_model: ClassVar[type[LeagueDashTeamStatsResponse]] = (
        LeagueDashTeamStatsResponse
    )

    season: Season = "2024-25"
    season_type: SeasonType = "Regular Season"
    per_mode: PerMode = "PerGame"
    measure_type: MeasureType = "Base"
    league_id: LeagueID = "00"
    last_n_games: int = 0
    month: int = 0
    opponent_team_id: int = 0
    pace_adjust: str = "N"
    period: int = 0
    plus_minus: str = "N"
    rank: str = "N"

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {
            "Season": self.season,
            "SeasonType": self.season_type,
            "PerMode": self.per_mode,
            "MeasureType": self.measure_type,
            "LeagueID": self.league_id,
            "LastNGames": str(self.last_n_games),
            "Month": str(self.month),
            "OpponentTeamID": str(self.opponent_team_id),
            "PaceAdjust": self.pace_adjust,
            "Period": str(self.period),
            "PlusMinus": self.plus_minus,
            "Rank": self.rank,
        }
