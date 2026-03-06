"""Player Dashboard PT Shots endpoint for player tracking shot statistics."""

from typing import ClassVar

from pydantic import Field

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.player_dash_pt_shots import PlayerDashPtShotsResponse
from fastbreak.seasons import get_season_from_date
from fastbreak.types import (
    Conference,
    Date,
    Division,
    GameSegment,
    LeagueID,
    Location,
    Outcome,
    Period,
    PerMode,
    Season,
    SeasonSegment,
    SeasonType,
)


class PlayerDashPtShots(Endpoint[PlayerDashPtShotsResponse]):
    """Fetch player shot statistics with tracking data breakdowns.

    Returns shooting stats broken down by shot type, shot clock, dribbles,
    closest defender distance, and touch time.

    Args:
        player_id: NBA player ID (required)
        league_id: League identifier ("00" for NBA)
        season: Season in YYYY-YY format (e.g., "2024-25")
        season_type: Type of season ("Regular Season", "Playoffs", "Pre Season")
        per_mode: Stat mode ("Totals", "PerGame")
        team_id: Team ID filter
        outcome: Filter by game outcome ("W", "L")
        location: Filter by game location ("Home", "Road")
        month: Filter by month (1-12)
        season_segment: Filter by season segment ("Pre All-Star", "Post All-Star")
        date_from: Filter games from date (MM/DD/YYYY)
        date_to: Filter games to date (MM/DD/YYYY)
        opponent_team_id: Filter by opponent team ID
        vs_conference: Filter by opponent conference ("East", "West")
        vs_division: Filter by opponent division
        game_segment: Filter by game segment ("First Half", "Second Half", "Overtime")
        period: Filter by period (0 for all)
        last_n_games: Filter to last N games

    """

    path: ClassVar[str] = "playerdashptshots"
    response_model: ClassVar[type[PlayerDashPtShotsResponse]] = (
        PlayerDashPtShotsResponse
    )

    # Required parameters
    player_id: int
    league_id: LeagueID = "00"
    season: Season = Field(default_factory=get_season_from_date)
    season_type: SeasonType = "Regular Season"
    per_mode: PerMode = "PerGame"

    # Always-sent filters with defaults
    team_id: int = 0
    month: int = 0
    opponent_team_id: int = 0
    period: Period = 0
    last_n_games: int = 0

    # Optional filters
    outcome: Outcome | None = None
    location: Location | None = None
    season_segment: SeasonSegment | None = None
    date_from: Date | None = None
    date_to: Date | None = None
    vs_conference: Conference | None = None
    vs_division: Division | None = None
    game_segment: GameSegment | None = None

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        result: dict[str, str] = {
            "PlayerID": str(self.player_id),
            "LeagueID": self.league_id,
            "Season": self.season,
            "SeasonType": self.season_type,
            "PerMode": self.per_mode,
            "TeamID": str(self.team_id),
            "Month": str(self.month),
            "OpponentTeamID": str(self.opponent_team_id),
            "Period": str(self.period),
            "LastNGames": str(self.last_n_games),
        }

        optional_params = {
            "outcome": "Outcome",
            "location": "Location",
            "season_segment": "SeasonSegment",
            "date_from": "DateFrom",
            "date_to": "DateTo",
            "vs_conference": "VsConference",
            "vs_division": "VsDivision",
            "game_segment": "GameSegment",
        }

        for attr, param_name in optional_params.items():
            value = getattr(self, attr)
            if value is not None:
                result[param_name] = value

        return result
