"""Endpoint for fetching summarized team on/off court statistics by player."""

from dataclasses import dataclass
from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.team_player_on_off_summary import TeamPlayerOnOffSummaryResponse


@dataclass(frozen=True)
class TeamPlayerOnOffSummary(Endpoint[TeamPlayerOnOffSummaryResponse]):
    """Fetch summarized team on/off court statistics for each player.

    More compact than TeamPlayerOnOffDetails - focuses on key impact metrics:
    offensive rating, defensive rating, net rating, and plus/minus.

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

    path: ClassVar[str] = "teamplayeronoffsummary"
    response_model: ClassVar[type[TeamPlayerOnOffSummaryResponse]] = (
        TeamPlayerOnOffSummaryResponse
    )

    team_id: int = 0
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
