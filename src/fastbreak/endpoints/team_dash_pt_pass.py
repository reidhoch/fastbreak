"""Endpoint for fetching team passing statistics."""

from typing import ClassVar

from pydantic import Field

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.team_dash_pt_pass import TeamDashPtPassResponse
from fastbreak.types import (
    Conference,
    Date,
    Division,
    LeagueID,
    Location,
    Outcome,
    PerMode,
    Season,
    SeasonSegment,
    SeasonType,
)
from fastbreak.utils import get_season_from_date


class TeamDashPtPass(Endpoint[TeamDashPtPassResponse]):
    """Fetch team passing statistics by player.

    Returns passing data including assists and field goal efficiency on passes
    made and received by each player on the team.

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
        last_n_games: Filter to last N games (0 for all)

    """

    path: ClassVar[str] = "teamdashptpass"
    response_model: ClassVar[type[TeamDashPtPassResponse]] = TeamDashPtPassResponse

    # Required parameters
    team_id: int
    league_id: LeagueID = "00"
    season: Season = Field(default_factory=get_season_from_date)
    season_type: SeasonType = "Regular Season"
    per_mode: PerMode = "PerGame"

    # Filters with defaults
    month: int = 0
    opponent_team_id: int = 0
    last_n_games: int = 0

    # Optional filters
    outcome: Outcome | None = None
    location: Location | None = None
    season_segment: SeasonSegment | None = None
    date_from: Date | None = None
    date_to: Date | None = None
    vs_conference: Conference | None = None
    vs_division: Division | None = None

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
            "LastNGames": str(self.last_n_games),
            "DateFrom": self.date_from or "",
            "DateTo": self.date_to or "",
        }

        optional_params = {
            "outcome": "Outcome",
            "location": "Location",
            "season_segment": "SeasonSegment",
            "vs_conference": "VsConference",
            "vs_division": "VsDivision",
        }

        for attr, param_name in optional_params.items():
            value = getattr(self, attr)
            if value is not None:
                result[param_name] = value

        return result
