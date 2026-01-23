"""Endpoint for fetching team player dashboard statistics."""

from dataclasses import dataclass
from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.team_player_dashboard import TeamPlayerDashboardResponse


@dataclass(frozen=True)
class TeamPlayerDashboard(Endpoint[TeamPlayerDashboardResponse]):
    """Fetch team and individual player statistics.

    Returns team aggregate statistics and per-player breakdowns
    with traditional stats, fantasy points, and league rankings.

    Args:
        team_id: NBA team ID (required)
        season: Season in YYYY-YY format (e.g., "2024-25")
        season_type: Type of season ("Regular Season", "Playoffs", etc.)
        per_mode: Stat mode ("PerGame", "Totals", "Per36", etc.)
        measure_type: Measure type ("Base", "Advanced", etc.)
        league_id: League identifier ("00" for NBA)
        month: Month filter (0 for all)
        opponent_team_id: Filter by opponent (0 for all)
        period: Period filter (0 for all)
        last_n_games: Last N games filter (0 for all)

    """

    path: ClassVar[str] = "teamplayerdashboard"
    response_model: ClassVar[type[TeamPlayerDashboardResponse]] = (
        TeamPlayerDashboardResponse
    )

    team_id: int = 0
    season: str = "2024-25"
    season_type: str = "Regular Season"
    per_mode: str = "PerGame"
    measure_type: str = "Base"
    league_id: str = "00"
    month: int = 0
    opponent_team_id: int = 0
    period: int = 0
    last_n_games: int = 0
    date_from: str = ""
    date_to: str = ""
    game_segment: str = ""
    location: str = ""
    outcome: str = ""
    pace_adjust: str = "N"
    plus_minus: str = "N"
    rank: str = "N"
    season_segment: str = ""
    shot_clock_range: str = ""
    vs_conference: str = ""
    vs_division: str = ""

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {
            "TeamID": str(self.team_id),
            "Season": self.season,
            "SeasonType": self.season_type,
            "PerMode": self.per_mode,
            "MeasureType": self.measure_type,
            "LeagueID": self.league_id,
            "Month": str(self.month),
            "OpponentTeamID": str(self.opponent_team_id),
            "Period": str(self.period),
            "LastNGames": str(self.last_n_games),
            "DateFrom": self.date_from,
            "DateTo": self.date_to,
            "GameSegment": self.game_segment,
            "Location": self.location,
            "Outcome": self.outcome,
            "PaceAdjust": self.pace_adjust,
            "PlusMinus": self.plus_minus,
            "Rank": self.rank,
            "SeasonSegment": self.season_segment,
            "ShotClockRange": self.shot_clock_range,
            "VsConference": self.vs_conference,
            "VsDivision": self.vs_division,
        }
