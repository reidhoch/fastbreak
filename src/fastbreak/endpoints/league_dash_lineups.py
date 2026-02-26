"""Endpoint for fetching league-wide lineup statistics."""

from typing import ClassVar

from pydantic import Field

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.league_dash_lineups import LeagueDashLineupsResponse
from fastbreak.seasons import get_season_from_date
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


class LeagueDashLineups(Endpoint[LeagueDashLineupsResponse]):
    """Fetch league-wide lineup combination statistics.

    Returns stats for all lineup combinations of the specified size
    across the entire league.

    Args:
        season: Season in YYYY-YY format (e.g., "2024-25")
        season_type: Type of season ("Regular Season", "Playoffs")
        per_mode: Stat mode ("Totals", "PerGame", "Per36", etc.)
        measure_type: Measure type ("Base", "Advanced", "Misc", etc.)
        group_quantity: Number of players in lineup (2-5, default 5)
        league_id: League identifier ("00" for NBA)
        team_id: Filter by specific team (0 for all teams)
        pace_adjust: Whether to pace adjust ("Y", "N")
        plus_minus: Whether to include plus/minus ("Y", "N")
        rank: Whether to include rank ("Y", "N")
        month: Filter by month (0 for all)
        period: Filter by period (0 for all)
        opponent_team_id: Filter by opponent (0 for all)
        last_n_games: Filter to last N games (0 for all)
        po_round: Playoff round filter (0 for all)
        outcome: Filter by game outcome ("W", "L")
        location: Filter by game location ("Home", "Road")
        date_from: Filter games from date (MM/DD/YYYY)
        date_to: Filter games to date (MM/DD/YYYY)
        vs_conference: Filter by opponent conference
        vs_division: Filter by opponent division
        game_segment: Filter by game segment
        shot_clock_range: Filter by shot clock range
        conference: Filter by team conference
        division: Filter by team division
        season_segment: Filter by season segment

    """

    path: ClassVar[str] = "leaguedashlineups"
    response_model: ClassVar[type[LeagueDashLineupsResponse]] = (
        LeagueDashLineupsResponse
    )

    # Core parameters
    team_id: int
    season: Season = Field(default_factory=get_season_from_date)
    season_type: SeasonType = "Regular Season"
    per_mode: PerMode = "PerGame"
    measure_type: MeasureType = "Base"
    group_quantity: int = 5
    league_id: LeagueID = "00"
    pace_adjust: YesNo = "N"
    plus_minus: YesNo = "N"
    rank: YesNo = "N"

    # Numeric filters with defaults
    month: int = 0
    period: Period = 0
    opponent_team_id: int = 0
    last_n_games: int = 0
    po_round: int = 0

    # Optional filters
    outcome: Outcome | None = None
    location: Location | None = None
    date_from: Date | None = None
    date_to: Date | None = None
    vs_conference: Conference | None = None
    vs_division: Division | None = None
    game_segment: GameSegment | None = None
    shot_clock_range: ShotClockRange | None = None
    conference: Conference | None = None
    division: Division | None = None
    season_segment: SeasonSegment | None = None

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        result: dict[str, str] = {
            "Season": self.season,
            "SeasonType": self.season_type,
            "PerMode": self.per_mode,
            "MeasureType": self.measure_type,
            "GroupQuantity": str(self.group_quantity),
            "LeagueID": self.league_id,
            "TeamID": str(self.team_id),
            "PaceAdjust": self.pace_adjust,
            "PlusMinus": self.plus_minus,
            "Rank": self.rank,
            "Month": str(self.month),
            "Period": str(self.period),
            "OpponentTeamID": str(self.opponent_team_id),
            "LastNGames": str(self.last_n_games),
            "PORound": str(self.po_round),
        }

        # Optional parameters - only include if set
        optional_params = {
            "outcome": "Outcome",
            "location": "Location",
            "date_from": "DateFrom",
            "date_to": "DateTo",
            "vs_conference": "VsConference",
            "vs_division": "VsDivision",
            "game_segment": "GameSegment",
            "shot_clock_range": "ShotClockRange",
            "conference": "Conference",
            "division": "Division",
            "season_segment": "SeasonSegment",
        }

        for attr, param_name in optional_params.items():
            value = getattr(self, attr)
            if value is not None:
                result[param_name] = value

        return result
