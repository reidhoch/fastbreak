"""Endpoint for comparing team performance against a specific player."""

from dataclasses import dataclass
from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.team_vs_player import TeamVsPlayerResponse


@dataclass(frozen=True)
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

    team_id: int = 0
    vs_player_id: int = 0
    season: str = "2024-25"
    season_type: str = "Regular Season"
    per_mode: str = "PerGame"
    measure_type: str = "Base"
    league_id: str = "00"
    month: int = 0
    opponent_team_id: int = 0
    period: int = 0
    last_n_games: int = 0
    date_from: str = ""
    date_to: str = ""
    game_segment: str = ""
    location: str = ""
    outcome: str = ""
    pace_adjust: str = "N"
    plus_minus: str = "N"
    rank: str = "N"
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
            "DateFrom": self.date_from,
            "DateTo": self.date_to,
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
