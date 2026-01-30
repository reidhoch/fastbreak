"""Endpoint for fetching team shooting statistics by split categories."""

from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.team_dashboard_by_shooting_splits import (
    TeamDashboardByShootingSplitsResponse,
)
from fastbreak.types import (
    Conference,
    Date,
    Division,
    GameSegment,
    LeagueID,
    Location,
    MeasureType,
    Outcome,
    Period,
    PerMode,
    Season,
    SeasonSegment,
    SeasonType,
    ShotClockRange,
    YesNo,
)


class TeamDashboardByShootingSplits(Endpoint[TeamDashboardByShootingSplitsResponse]):
    """Fetch team shooting stats broken down by shot type and distance.

    Returns detailed shooting stats including:
    - Shot distance (5ft and 8ft increments)
    - Shot area (restricted area, paint, mid-range, 3pt zones)
    - Assisted vs unassisted shots
    - Shot type breakdown (dunks, layups, jumpers, etc.)
    - Assists by player

    Args:
        team_id: NBA team ID (required)
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
        month: Filter by month (0 for all, 1-12 for specific month)
        season_segment: Filter by season segment ("Pre All-Star", "Post All-Star")
        date_from: Filter games from date (MM/DD/YYYY)
        date_to: Filter games to date (MM/DD/YYYY)
        opponent_team_id: Filter by opponent team ID (0 for all)
        vs_conference: Filter by opponent conference ("East", "West")
        vs_division: Filter by opponent division
        game_segment: Filter by game segment ("First Half", "Second Half", "Overtime")
        period: Filter by period (0 for all)
        shot_clock_range: Filter by shot clock range
        last_n_games: Filter to last N games (0 for all)
        po_round: Playoff round filter (0 for all)

    """

    path: ClassVar[str] = "teamdashboardbyshootingsplits"
    response_model: ClassVar[type[TeamDashboardByShootingSplitsResponse]] = (
        TeamDashboardByShootingSplitsResponse
    )

    # Required parameters
    team_id: int
    league_id: LeagueID = "00"
    season: Season = "2024-25"
    season_type: SeasonType = "Regular Season"
    per_mode: PerMode = "PerGame"
    measure_type: MeasureType = "Base"
    pace_adjust: YesNo = "N"
    plus_minus: YesNo = "N"
    rank: YesNo = "N"

    # Filters with defaults
    month: int = 0
    period: Period = 0
    opponent_team_id: int = 0
    last_n_games: int = 0
    po_round: int = 0

    # Optional filters
    outcome: Outcome | None = None
    location: Location | None = None
    season_segment: SeasonSegment | None = None
    date_from: Date | None = None
    date_to: Date | None = None
    vs_conference: Conference | None = None
    vs_division: Division | None = None
    game_segment: GameSegment | None = None
    shot_clock_range: ShotClockRange | None = None

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        result: dict[str, str] = {
            "TeamID": str(self.team_id),
            "LeagueID": self.league_id,
            "Season": self.season,
            "SeasonType": self.season_type,
            "PerMode": self.per_mode,
            "MeasureType": self.measure_type,
            "PaceAdjust": self.pace_adjust,
            "PlusMinus": self.plus_minus,
            "Rank": self.rank,
            "Month": str(self.month),
            "Period": str(self.period),
            "OpponentTeamID": str(self.opponent_team_id),
            "LastNGames": str(self.last_n_games),
            "PORound": str(self.po_round),
        }

        # Map of optional attributes to API parameter names
        optional_params = {
            "outcome": "Outcome",
            "location": "Location",
            "season_segment": "SeasonSegment",
            "date_from": "DateFrom",
            "date_to": "DateTo",
            "vs_conference": "VsConference",
            "vs_division": "VsDivision",
            "game_segment": "GameSegment",
            "shot_clock_range": "ShotClockRange",
        }

        for attr, param_name in optional_params.items():
            value = getattr(self, attr)
            if value is not None:
                result[param_name] = value

        return result
