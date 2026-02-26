"""Endpoint for comparing team performance against a specific player."""

from typing import ClassVar

from pydantic import Field

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.team_vs_player import TeamVsPlayerResponse
from fastbreak.seasons import get_season_from_date
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


class TeamVsPlayer(Endpoint[TeamVsPlayerResponse]):
    """Fetch team statistics when facing a specific player.

    Shows how teams perform against a particular player, including
    on/off court splits and shooting breakdown by distance and area.

    Args:
        team_id: NBA team ID (required)
        vs_player_id: Target player ID to compare against (required)
        season: Season in YYYY-YY format (e.g., "2024-25")
        season_type: Type of season ("Regular Season", "Playoffs", etc.)
        per_mode: Stat mode ("PerGame", "Totals", "Per36", etc.)
        measure_type: Measure type ("Base", "Advanced", etc.)
        league_id: League identifier ("00" for NBA)

    """

    path: ClassVar[str] = "teamvsplayer"
    response_model: ClassVar[type[TeamVsPlayerResponse]] = TeamVsPlayerResponse

    team_id: int
    vs_player_id: int
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
            "VsPlayerID": str(self.vs_player_id),
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
