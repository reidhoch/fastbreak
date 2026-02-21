"""Endpoint for comparing a player's stats against another player."""

from typing import ClassVar

from pydantic import Field

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.player_vs_player import PlayerVsPlayerResponse
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
    YesNo,
)
from fastbreak.utils import get_season_from_date


class PlayerVsPlayer(Endpoint[PlayerVsPlayerResponse]):
    """Compare a player's stats when playing against another player.

    This endpoint shows how a player performs when matched up against
    a specific opponent, including on/off court splits and shot charts.

    Args:
        league_id: League identifier ("00" for NBA)
        player_id: ID of the player to analyze
        vs_player_id: ID of the player to compare against
        season: Season in YYYY-YY format (e.g., "2024-25")
        season_type: Type of season ("Regular Season", "Playoffs", "Pre Season")
        per_mode: Stat mode ("Totals", "PerGame", "Per36", etc.)
        measure_type: Measure type ("Base", "Advanced", "Misc", etc.)
        pace_adjust: Whether to pace adjust ("Y", "N")
        plus_minus: Whether to include plus/minus ("Y", "N")
        rank: Whether to include rank ("Y", "N")
        conference: Filter by conference ("East", "West")
        division: Filter by division
        game_segment: Filter by game segment ("First Half", "Second Half", "Overtime")
        last_n_games: Filter to last N games
        location: Filter by game location ("Home", "Road")
        month: Filter by month (1-12)
        opponent_team_id: Filter by opponent team ID
        outcome: Filter by game outcome ("W", "L")
        period: Filter by period (0 for all)
        season_segment: Filter by season segment ("Pre All-Star", "Post All-Star")
        date_from: Filter games from date (MM/DD/YYYY)
        date_to: Filter games to date (MM/DD/YYYY)
        vs_conference: Filter by opponent conference ("East", "West")
        vs_division: Filter by opponent division

    """

    path: ClassVar[str] = "playervsplayer"
    response_model: ClassVar[type[PlayerVsPlayerResponse]] = PlayerVsPlayerResponse

    # Required parameters
    player_id: str
    vs_player_id: str
    league_id: LeagueID = "00"
    season: Season = Field(default_factory=get_season_from_date)
    season_type: SeasonType = "Regular Season"
    per_mode: PerMode = "PerGame"
    measure_type: MeasureType = "Base"
    pace_adjust: YesNo = "N"
    plus_minus: YesNo = "N"
    rank: YesNo = "N"

    # Optional filters
    conference: Conference | None = None
    division: Division | None = None
    game_segment: GameSegment | None = None
    last_n_games: str = "0"
    location: Location | None = None
    month: str = "0"
    opponent_team_id: str = "0"
    outcome: Outcome | None = None
    period: str = "0"
    season_segment: SeasonSegment | None = None
    date_from: Date | None = None
    date_to: Date | None = None
    vs_conference: Conference | None = None
    vs_division: Division | None = None

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        result: dict[str, str] = {
            "LeagueID": self.league_id,
            "PlayerID": self.player_id,
            "VsPlayerID": self.vs_player_id,
            "Season": self.season,
            "SeasonType": self.season_type,
            "PerMode": self.per_mode,
            "MeasureType": self.measure_type,
            "PaceAdjust": self.pace_adjust,
            "PlusMinus": self.plus_minus,
            "Rank": self.rank,
            "LastNGames": self.last_n_games,
            "Month": self.month,
            "OpponentTeamID": self.opponent_team_id,
            "Period": self.period,
        }

        # Map of optional attributes to API parameter names
        optional_params = {
            "conference": "Conference",
            "division": "Division",
            "game_segment": "GameSegment",
            "location": "Location",
            "outcome": "Outcome",
            "season_segment": "SeasonSegment",
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
