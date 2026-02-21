"""Player Compare endpoint for comparing stats between players."""

from typing import ClassVar

from pydantic import Field

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.player_compare import PlayerCompareResponse
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
from fastbreak.utils import get_season_from_date


class PlayerCompare(Endpoint[PlayerCompareResponse]):
    """Compare stats between two groups of players.

    Args:
        league_id: League identifier ("00" for NBA)
        player_id_list: Comma-separated list of player IDs to compare
        vs_player_id_list: Comma-separated list of player IDs to compare against
        season: Season in YYYY-YY format (e.g., "2024-25")
        season_type: Type of season ("Regular Season", "Playoffs", "Pre Season")
        per_mode: Stat mode ("Totals", "PerGame", "Per36", etc.)
        measure_type: Measure type ("Base", "Advanced", "Misc", etc.)
        pace_adjust: Whether to pace adjust ("Y", "N")
        plus_minus: Whether to include plus/minus ("Y", "N")
        rank: Whether to include rank ("Y", "N")
        month: Filter by month (0 for all)
        opponent_team_id: Filter by opponent team ID (0 for all)
        period: Filter by period (0 for all)
        last_n_games: Filter to last N games (0 for all)
        conference: Filter by conference ("East", "West")
        division: Filter by division
        game_segment: Filter by game segment ("First Half", "Second Half", "Overtime")
        location: Filter by game location ("Home", "Road")
        outcome: Filter by game outcome ("W", "L")
        season_segment: Filter by season segment ("Pre All-Star", "Post All-Star")
        shot_clock_range: Filter by shot clock range
        date_from: Filter games from date (MM/DD/YYYY)
        date_to: Filter games to date (MM/DD/YYYY)
        vs_conference: Filter by opponent conference ("East", "West")
        vs_division: Filter by opponent division

    """

    path: ClassVar[str] = "playercompare"
    response_model: ClassVar[type[PlayerCompareResponse]] = PlayerCompareResponse

    # Required parameters
    league_id: LeagueID = "00"
    player_id_list: str = ""
    vs_player_id_list: str = ""
    season: Season = Field(default_factory=get_season_from_date)
    season_type: SeasonType = "Regular Season"
    per_mode: PerMode = "PerGame"
    measure_type: MeasureType = "Base"
    pace_adjust: YesNo = "N"
    plus_minus: YesNo = "N"
    rank: YesNo = "N"

    # Always-sent filters with defaults
    month: int = 0
    opponent_team_id: int = 0
    period: Period = 0
    last_n_games: int = 0

    # Optional filters
    conference: Conference | None = None
    division: Division | None = None
    game_segment: GameSegment | None = None
    location: Location | None = None
    outcome: Outcome | None = None
    season_segment: SeasonSegment | None = None
    shot_clock_range: ShotClockRange | None = None
    date_from: Date | None = None
    date_to: Date | None = None
    vs_conference: Conference | None = None
    vs_division: Division | None = None

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        result: dict[str, str] = {
            "LeagueID": self.league_id,
            "PlayerIDList": self.player_id_list,
            "VsPlayerIDList": self.vs_player_id_list,
            "Season": self.season,
            "SeasonType": self.season_type,
            "PerMode": self.per_mode,
            "MeasureType": self.measure_type,
            "PaceAdjust": self.pace_adjust,
            "PlusMinus": self.plus_minus,
            "Rank": self.rank,
            "Month": str(self.month),
            "OpponentTeamID": str(self.opponent_team_id),
            "Period": str(self.period),
            "LastNGames": str(self.last_n_games),
        }

        # Map of optional attributes to API parameter names
        optional_params = {
            "conference": "Conference",
            "division": "Division",
            "game_segment": "GameSegment",
            "location": "Location",
            "outcome": "Outcome",
            "season_segment": "SeasonSegment",
            "shot_clock_range": "ShotClockRange",
            "date_from": "DateFrom",
            "date_to": "DateTo",
            "vs_conference": "VsConference",
            "vs_division": "VsDivision",
        }

        for attr, param_name in optional_params.items():
            value = getattr(self, attr)
            if value is not None:
                result[param_name] = value

        return result
