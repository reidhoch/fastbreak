"""League dashboard player clutch stats endpoint."""

from typing import ClassVar

from pydantic import Field

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.league_dash_player_clutch import LeagueDashPlayerClutchResponse
from fastbreak.types import (
    AheadBehind,
    ClutchTime,
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
    PlayerExperience,
    PlayerPosition,
    Season,
    SeasonSegment,
    SeasonType,
    ShotClockRange,
    StarterBench,
    YesNo,
)
from fastbreak.utils import get_season_from_date


class LeagueDashPlayerClutch(Endpoint[LeagueDashPlayerClutchResponse]):
    """Fetch league-wide player clutch statistics dashboard.

    Returns clutch statistics for all players (last 5 minutes, score within 5).

    Args:
        season: Season in YYYY-YY format (e.g., "2024-25")
        season_type: Type of season ("Regular Season", "Playoffs", etc.)
        clutch_time: Time remaining filter (e.g., "Last 5 Minutes")
        ahead_behind: Score situation filter (e.g., "Ahead or Behind")
        point_diff: Maximum point differential to qualify as clutch
        measure_type: Type of statistical measure ("Base", "Advanced", etc.)
        per_mode: Stat aggregation mode ("PerGame", "Totals", etc.)
        league_id: League identifier ("00" for NBA)

    """

    path: ClassVar[str] = "leaguedashplayerclutch"
    response_model: ClassVar[type[LeagueDashPlayerClutchResponse]] = (
        LeagueDashPlayerClutchResponse
    )

    # Required parameters
    season: Season = Field(default_factory=get_season_from_date)
    season_type: SeasonType = "Regular Season"
    clutch_time: ClutchTime = "Last 5 Minutes"
    ahead_behind: AheadBehind = "Ahead or Behind"
    point_diff: int = 5
    measure_type: MeasureType = "Base"
    per_mode: PerMode = "PerGame"
    league_id: LeagueID = "00"

    # Optional filters (empty string = no filter)
    conference: Conference | str = ""
    date_from: Date | str = ""
    date_to: Date | str = ""
    division: Division | str = ""
    game_scope: str = ""
    game_segment: GameSegment | str = ""
    last_n_games: int = 0
    location: Location | str = ""
    month: int = 0
    opponent_team_id: int = 0
    outcome: Outcome | str = ""
    pace_adjust: YesNo = "N"
    period: Period = 0
    player_experience: PlayerExperience | str = ""
    player_position: PlayerPosition | str = ""
    plus_minus: YesNo = "N"
    po_round: int = 0
    rank: YesNo = "N"
    season_segment: SeasonSegment | str = ""
    shot_clock_range: ShotClockRange | str = ""
    starter_bench: StarterBench | str = ""
    team_id: int = 0
    vs_conference: Conference | str = ""
    vs_division: Division | str = ""

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {
            "AheadBehind": self.ahead_behind,
            "ClutchTime": self.clutch_time,
            "Conference": self.conference,
            "DateFrom": self.date_from,
            "DateTo": self.date_to,
            "Division": self.division,
            "GameScope": self.game_scope,
            "GameSegment": self.game_segment,
            "LastNGames": str(self.last_n_games),
            "LeagueID": self.league_id,
            "Location": self.location,
            "MeasureType": self.measure_type,
            "Month": str(self.month),
            "OpponentTeamID": str(self.opponent_team_id),
            "Outcome": self.outcome,
            "PORound": str(self.po_round),
            "PaceAdjust": self.pace_adjust,
            "PerMode": self.per_mode,
            "Period": str(self.period),
            "PlayerExperience": self.player_experience,
            "PlayerPosition": self.player_position,
            "PlusMinus": self.plus_minus,
            "PointDiff": str(self.point_diff),
            "Rank": self.rank,
            "Season": self.season,
            "SeasonSegment": self.season_segment,
            "SeasonType": self.season_type,
            "ShotClockRange": self.shot_clock_range,
            "StarterBench": self.starter_bench,
            "TeamID": str(self.team_id),
            "VsConference": self.vs_conference,
            "VsDivision": self.vs_division,
        }
