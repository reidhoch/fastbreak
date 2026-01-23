"""Player Dashboard by Year Over Year endpoint for comparing stats across seasons."""

from dataclasses import dataclass
from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.player_dashboard_by_year_over_year import (
    PlayerDashboardByYearOverYearResponse,
)


@dataclass(frozen=True)
class PlayerDashboardByYearOverYear(Endpoint[PlayerDashboardByYearOverYearResponse]):
    """Fetch player stats comparing performance across seasons.

    Returns player statistics with year-over-year comparison data, including
    team information for each season.

    Args:
        player_id: NBA player ID (required)
        league_id: League identifier ("00" for NBA)
        season: Season in YYYY-YY format (e.g., "2024-25")
        season_type: Type of season ("Regular Season", "Playoffs", "Pre Season")
        per_mode: Stat mode ("Totals", "PerGame", "Per36", etc.)
        measure_type: Measure type ("Base", "Advanced", "Misc", etc.)
        pace_adjust: Whether to pace adjust ("Y", "N")
        plus_minus: Whether to include plus/minus ("Y", "N")
        rank: Whether to include rank ("Y", "N")
        outcome: Filter by game outcome ("W", "L")
        location: Filter by game location ("Home", "Road")
        month: Filter by month (1-12)
        season_segment: Filter by season segment ("Pre All-Star", "Post All-Star")
        date_from: Filter games from date (MM/DD/YYYY)
        date_to: Filter games to date (MM/DD/YYYY)
        opponent_team_id: Filter by opponent team ID
        vs_conference: Filter by opponent conference ("East", "West")
        vs_division: Filter by opponent division
        game_segment: Filter by game segment ("First Half", "Second Half", "Overtime")
        period: Filter by period (0 for all)
        shot_clock_range: Filter by shot clock range
        last_n_games: Filter to last N games
        po_round: Playoff round filter

    """

    path: ClassVar[str] = "playerdashboardbyyearoveryear"
    response_model: ClassVar[type[PlayerDashboardByYearOverYearResponse]] = (
        PlayerDashboardByYearOverYearResponse
    )

    # Required parameters
    player_id: str = ""
    league_id: str = "00"
    season: str = "2024-25"
    season_type: str = "Regular Season"
    per_mode: str = "PerGame"
    measure_type: str = "Base"
    pace_adjust: str = "N"
    plus_minus: str = "N"
    rank: str = "N"

    # Optional filters
    outcome: str | None = None
    location: str | None = None
    month: str | None = None
    season_segment: str | None = None
    date_from: str | None = None
    date_to: str | None = None
    opponent_team_id: str | None = None
    vs_conference: str | None = None
    vs_division: str | None = None
    game_segment: str | None = None
    period: str | None = None
    shot_clock_range: str | None = None
    last_n_games: str | None = None
    po_round: str | None = None

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        result: dict[str, str] = {
            "PlayerID": self.player_id,
            "LeagueID": self.league_id,
            "Season": self.season,
            "SeasonType": self.season_type,
            "PerMode": self.per_mode,
            "MeasureType": self.measure_type,
            "PaceAdjust": self.pace_adjust,
            "PlusMinus": self.plus_minus,
            "Rank": self.rank,
        }

        optional_params = {
            "outcome": "Outcome",
            "location": "Location",
            "month": "Month",
            "season_segment": "SeasonSegment",
            "date_from": "DateFrom",
            "date_to": "DateTo",
            "opponent_team_id": "OpponentTeamID",
            "vs_conference": "VsConference",
            "vs_division": "VsDivision",
            "game_segment": "GameSegment",
            "period": "Period",
            "shot_clock_range": "ShotClockRange",
            "last_n_games": "LastNGames",
            "po_round": "PORound",
        }

        for attr, param_name in optional_params.items():
            value = getattr(self, attr)
            if value is not None:
                result[param_name] = value

        return result
