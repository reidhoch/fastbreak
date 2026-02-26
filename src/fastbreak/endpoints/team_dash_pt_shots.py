"""Endpoint for fetching team shot tracking statistics."""

from typing import ClassVar

from pydantic import Field

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.team_dash_pt_shots import TeamDashPtShotsResponse
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


class TeamDashPtShots(Endpoint[TeamDashPtShotsResponse]):
    """Fetch team shot tracking statistics.

    Returns shooting data broken down by shot type/distance, shot clock,
    dribbles, defender distance, and touch time.

    Args:
        team_id: NBA team ID (required)
        league_id: League identifier ("00" for NBA)
        season: Season in YYYY-YY format (e.g., "2024-25")
        season_type: Type of season ("Regular Season", "Playoffs", "Pre Season")
        per_mode: Stat mode ("Totals", "PerGame")
        outcome: Filter by game outcome ("W", "L")
        location: Filter by game location ("Home", "Road")
        month: Filter by month (0 for all, 1-12 for specific month)
        season_segment: Filter by season segment ("Pre All-Star", "Post All-Star")
        date_from: Filter games from date (MM/DD/YYYY)
        date_to: Filter games to date (MM/DD/YYYY)
        opponent_team_id: Filter by opponent team ID (0 for all)
        vs_conference: Filter by opponent conference ("East", "West")
        vs_division: Filter by opponent division
        game_segment: Filter by game segment ("First Half", "Second Half", "Overtime")
        period: Filter by period (0 for all)
        last_n_games: Filter to last N games (0 for all)

    """

    path: ClassVar[str] = "teamdashptshots"
    response_model: ClassVar[type[TeamDashPtShotsResponse]] = TeamDashPtShotsResponse

    # Required parameters
    team_id: int
    league_id: LeagueID = "00"
    season: Season = Field(default_factory=get_season_from_date)
    season_type: SeasonType = "Regular Season"
    per_mode: PerMode = "PerGame"

    # Filters with defaults
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
            "TeamID": str(self.team_id),
            "LeagueID": self.league_id,
            "Season": self.season,
            "SeasonType": self.season_type,
            "PerMode": self.per_mode,
            "Month": str(self.month),
            "OpponentTeamID": str(self.opponent_team_id),
            "Period": str(self.period),
            "LastNGames": str(self.last_n_games),
            "DateFrom": self.date_from or "",
            "DateTo": self.date_to or "",
            "Outcome": self.outcome or "",
            "Location": self.location or "",
            "GameSegment": self.game_segment or "",
        }

        optional_params = {
            "season_segment": "SeasonSegment",
            "vs_conference": "VsConference",
            "vs_division": "VsDivision",
        }

        for attr, param_name in optional_params.items():
            value = getattr(self, attr)
            if value is not None:
                result[param_name] = value

        return result
