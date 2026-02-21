"""League dashboard player stats endpoint."""

from typing import ClassVar

from pydantic import Field

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.league_dash_player_stats import LeagueDashPlayerStatsResponse
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


class LeagueDashPlayerStats(Endpoint[LeagueDashPlayerStatsResponse]):
    """Fetch league-wide player statistics dashboard.

    Returns comprehensive statistics for all players across the league.

    Args:
        season: Season in YYYY-YY format (e.g., "2024-25")
        season_type: Type of season ("Regular Season", "Playoffs", etc.)
        per_mode: Stat aggregation mode ("PerGame", "Totals", "Per36", etc.)
        measure_type: Type of stats ("Base", "Advanced", "Misc", etc.)
        league_id: League identifier ("00" for NBA)

    """

    path: ClassVar[str] = "leaguedashplayerstats"
    response_model: ClassVar[type[LeagueDashPlayerStatsResponse]] = (
        LeagueDashPlayerStatsResponse
    )

    # Required parameters
    season: Season = Field(default_factory=get_season_from_date)
    season_type: SeasonType = "Regular Season"
    per_mode: PerMode = "PerGame"
    measure_type: MeasureType = "Base"
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
