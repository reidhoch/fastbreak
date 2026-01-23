"""Endpoint for fetching league player on/off court details."""

from dataclasses import dataclass
from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.league_player_on_details import LeaguePlayerOnDetailsResponse


@dataclass(frozen=True)
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
    season: str = "2024-25"
    season_type: str = "Regular Season"
    per_mode: str = "Totals"
    measure_type: str = "Base"
    league_id: str = "00"
    pace_adjust: str = "N"
    plus_minus: str = "N"
    rank: str = "N"
    date_from: str | None = None
    date_to: str | None = None
    game_segment: str | None = None
    last_n_games: int = 0
    location: str | None = None
    month: int = 0
    opponent_team_id: int = 0
    outcome: str | None = None
    po_round: int = 0
    period: int = 0
    season_segment: str | None = None
    shot_clock_range: str | None = None
    vs_conference: str | None = None
    vs_division: str | None = None

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
