"""Endpoint for fetching league-wide team shot location statistics."""

from typing import ClassVar

from pydantic import Field

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.league_dash_team_shot_locations import (
    LeagueDashTeamShotLocationsResponse,
)
from fastbreak.types import (
    Conference,
    Date,
    DistanceRange,
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
    YesNo,
)
from fastbreak.utils import get_season_from_date


class LeagueDashTeamShotLocations(Endpoint[LeagueDashTeamShotLocationsResponse]):
    """Fetch league-wide team shot statistics by distance/location.

    Returns shooting stats for all teams broken down by shot distance ranges
    (e.g., 0-4 ft, 5-9 ft, 10-14 ft, etc.).

    Args:
        season: Season in YYYY-YY format (e.g., "2024-25")
        season_type: Type of season ("Regular Season", "Playoffs")
        per_mode: Stat mode ("Totals", "PerGame")
        measure_type: "Base" for team's own shots, "Opponent" for opponent shots allowed
        distance_range: Shot distance grouping ("5ft Range", "8ft Range", "By Zone")
        league_id: League identifier ("00" for NBA)
        team_id: Filter by specific team (0 for all teams)
        month: Filter by month (0 for all)
        period: Filter by period (0 for all)
        opponent_team_id: Filter by opponent (0 for all)
        last_n_games: Filter to last N games (0 for all)
        po_round: Playoff round filter (0 for all)
        pace_adjust: Whether to pace adjust ("Y", "N")
        plus_minus: Whether to include plus/minus ("Y", "N")
        rank: Whether to include rank ("Y", "N")
        outcome: Filter by game outcome ("W", "L")
        location: Filter by game location ("Home", "Road")
        date_from: Filter games from date (MM/DD/YYYY)
        date_to: Filter games to date (MM/DD/YYYY)
        vs_conference: Filter by opponent conference
        vs_division: Filter by opponent division
        game_segment: Filter by game segment
        conference: Filter by team conference
        division: Filter by team division
        season_segment: Filter by season segment

    """

    path: ClassVar[str] = "leaguedashteamshotlocations"
    response_model: ClassVar[type[LeagueDashTeamShotLocationsResponse]] = (
        LeagueDashTeamShotLocationsResponse
    )

    # Core parameters
    team_id: int
    season: Season = Field(default_factory=get_season_from_date)
    season_type: SeasonType = "Regular Season"
    per_mode: PerMode = "PerGame"
    measure_type: MeasureType = "Base"
    distance_range: DistanceRange = "5ft Range"
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
            "DistanceRange": self.distance_range,
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
            "conference": "Conference",
            "division": "Division",
            "season_segment": "SeasonSegment",
        }

        for attr, param_name in optional_params.items():
            value = getattr(self, attr)
            if value is not None:
                result[param_name] = value

        return result
