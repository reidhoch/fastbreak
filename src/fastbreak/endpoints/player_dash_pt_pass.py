"""Player Dashboard Passing endpoint for tracking pass statistics."""

from dataclasses import dataclass
from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.player_dash_pt_pass import PlayerDashPtPassResponse


@dataclass(frozen=True)
class PlayerDashPtPass(Endpoint[PlayerDashPtPassResponse]):
    """Fetch player passing statistics by teammate.

    Returns passing data including assists, field goal efficiency on passes made
    and received with each teammate.

    Args:
        player_id: NBA player ID (required)
        league_id: League identifier ("00" for NBA)
        season: Season in YYYY-YY format (e.g., "2024-25")
        season_type: Type of season ("Regular Season", "Playoffs", "Pre Season")
        per_mode: Stat mode ("Totals", "PerGame")
        team_id: Team ID filter (0 for all)
        outcome: Filter by game outcome ("W", "L")
        location: Filter by game location ("Home", "Road")
        month: Filter by month (1-12, 0 for all)
        season_segment: Filter by season segment ("Pre All-Star", "Post All-Star")
        date_from: Filter games from date (MM/DD/YYYY)
        date_to: Filter games to date (MM/DD/YYYY)
        opponent_team_id: Filter by opponent team ID (0 for all)
        vs_conference: Filter by opponent conference ("East", "West")
        vs_division: Filter by opponent division
        last_n_games: Filter to last N games (0 for all)
        ist_round: In-Season Tournament round filter

    """

    path: ClassVar[str] = "playerdashptpass"
    response_model: ClassVar[type[PlayerDashPtPassResponse]] = PlayerDashPtPassResponse

    # Required parameters
    player_id: int = 0
    league_id: str = "00"
    season: str = "2024-25"
    season_type: str = "Regular Season"
    per_mode: str = "PerGame"

    # Always-sent filters with defaults
    team_id: int = 0
    month: int = 0
    opponent_team_id: int = 0
    last_n_games: int = 0

    # Optional filters
    outcome: str | None = None
    location: str | None = None
    season_segment: str | None = None
    date_from: str | None = None
    date_to: str | None = None
    vs_conference: str | None = None
    vs_division: str | None = None
    ist_round: str | None = None

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
            "ist_round": "ISTRound",
        }

        for attr, param_name in optional_params.items():
            value = getattr(self, attr)
            if value is not None:
                result[param_name] = value

        return result
