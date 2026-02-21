"""Endpoint for fetching team on/off court statistics by player."""

from typing import ClassVar

from pydantic import Field

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.team_player_on_off_details import TeamPlayerOnOffDetailsResponse
from fastbreak.types import (
    Date,
    LeagueID,
    MeasureType,
    Period,
    PerMode,
    Season,
    SeasonType,
    YesNo,
)
from fastbreak.utils import get_season_from_date


class TeamPlayerOnOffDetails(Endpoint[TeamPlayerOnOffDetailsResponse]):
    """Fetch team statistics with on/off court splits for each player.

    Shows how the team performs when each player is on the court
    versus when they are off, useful for analyzing player impact.

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

    path: ClassVar[str] = "teamplayeronoffdetails"
    response_model: ClassVar[type[TeamPlayerOnOffDetailsResponse]] = (
        TeamPlayerOnOffDetailsResponse
    )

    team_id: int
    season: Season = Field(default_factory=get_season_from_date)
    season_type: SeasonType = "Regular Season"
    per_mode: PerMode = "PerGame"
    measure_type: MeasureType = "Base"
    league_id: LeagueID = "00"
    month: int = 0
    opponent_team_id: int = 0
    period: Period = 0
    last_n_games: int = 0
    date_from: Date | None = None
    date_to: Date | None = None
    game_segment: str = ""
    location: str = ""
    outcome: str = ""
    pace_adjust: YesNo = "N"
    plus_minus: YesNo = "N"
    rank: YesNo = "N"
    season_segment: str = ""
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
            "DateFrom": self.date_from or "",
            "DateTo": self.date_to or "",
            "GameSegment": self.game_segment,
            "Location": self.location,
            "Outcome": self.outcome,
            "PaceAdjust": self.pace_adjust,
            "PlusMinus": self.plus_minus,
            "Rank": self.rank,
            "SeasonSegment": self.season_segment,
            "VsConference": self.vs_conference,
            "VsDivision": self.vs_division,
        }
