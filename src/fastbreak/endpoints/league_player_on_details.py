"""Endpoint for fetching league player on/off court details."""

from typing import ClassVar

from pydantic import Field

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.league_player_on_details import LeaguePlayerOnDetailsResponse
from fastbreak.types import (
    Conference,
    Date,
    Division,
    GameSegment,
    LeagueID,
    Location,
    MeasureType,
    Outcome,
    PerMode,
    Season,
    SeasonSegment,
    SeasonType,
    ShotClockRange,
    YesNo,
)
from fastbreak.utils import get_season_from_date


class LeaguePlayerOnDetails(Endpoint[LeaguePlayerOnDetailsResponse]):
    """Fetch team statistics when specific players are on the court.

    Returns team performance metrics for each player's on-court time,
    allowing analysis of individual player impact on team success.

    Args:
        team_id: Team identifier (required)
        season: Season in YYYY-YY format (e.g., "2024-25")
        season_type: Type of season ("Regular Season", "Playoffs")
        per_mode: Stat aggregation mode ("Totals", "PerGame", "Per100Possessions")
        measure_type: Type of stats ("Base", "Advanced", "Misc", "Scoring")
        league_id: League identifier ("00" for NBA)
        pace_adjust: Pace-adjusted stats ("Y", "N")
        plus_minus: Plus/minus stats ("Y", "N")
        rank: Include rankings ("Y", "N")

    """

    path: ClassVar[str] = "leagueplayerondetails"
    response_model: ClassVar[type[LeaguePlayerOnDetailsResponse]] = (
        LeaguePlayerOnDetailsResponse
    )

    team_id: int
    season: Season = Field(default_factory=get_season_from_date)
    season_type: SeasonType = "Regular Season"
    per_mode: PerMode = "Totals"
    measure_type: MeasureType = "Base"
    league_id: LeagueID = "00"
    pace_adjust: YesNo = "N"
    plus_minus: YesNo = "N"
    rank: YesNo = "N"
    date_from: Date | None = None
    date_to: Date | None = None
    game_segment: GameSegment | None = None
    last_n_games: int = 0
    location: Location | None = None
    month: int = 0
    opponent_team_id: int = 0
    outcome: Outcome | None = None
    po_round: int = 0
    period: int = 0
    season_segment: SeasonSegment | None = None
    shot_clock_range: ShotClockRange | None = None
    vs_conference: Conference | None = None
    vs_division: Division | None = None

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {
            "TeamID": str(self.team_id),
            "Season": self.season,
            "SeasonType": self.season_type,
            "PerMode": self.per_mode,
            "MeasureType": self.measure_type,
            "LeagueID": self.league_id,
            "PaceAdjust": self.pace_adjust,
            "PlusMinus": self.plus_minus,
            "Rank": self.rank,
            "DateFrom": self.date_from or "",
            "DateTo": self.date_to or "",
            "GameSegment": self.game_segment or "",
            "LastNGames": str(self.last_n_games),
            "Location": self.location or "",
            "Month": str(self.month),
            "OpponentTeamID": str(self.opponent_team_id),
            "Outcome": self.outcome or "",
            "PORound": str(self.po_round),
            "Period": str(self.period),
            "SeasonSegment": self.season_segment or "",
            "ShotClockRange": self.shot_clock_range or "",
            "VsConference": self.vs_conference or "",
            "VsDivision": self.vs_division or "",
        }
