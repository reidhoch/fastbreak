"""Player Dashboard PT Shots endpoint for player tracking shot statistics."""

from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.player_dash_pt_shots import PlayerDashPtShotsResponse
from fastbreak.types import Date, LeagueID, PerMode, Season, SeasonType


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
    player_id: str
    league_id: LeagueID = "00"
    season: Season = "2024-25"
    season_type: SeasonType = "Regular Season"
    per_mode: PerMode = "PerGame"

    # Optional filters with defaults that the API requires
    team_id: str = "0"
    outcome: str = ""
    location: str = ""
    month: str = "0"
    season_segment: str = ""
    date_from: Date | None = None
    date_to: Date | None = None
    opponent_team_id: str = "0"
    vs_conference: str = ""
    vs_division: str = ""
    game_segment: str = ""
    period: str = "0"
    last_n_games: str = "0"

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {
            "PlayerID": self.player_id,
            "LeagueID": self.league_id,
            "Season": self.season,
            "SeasonType": self.season_type,
            "PerMode": self.per_mode,
            "TeamID": self.team_id,
            "Outcome": self.outcome,
            "Location": self.location,
            "Month": self.month,
            "SeasonSegment": self.season_segment,
            "DateFrom": self.date_from or "",
            "DateTo": self.date_to or "",
            "OpponentTeamID": self.opponent_team_id,
            "VsConference": self.vs_conference,
            "VsDivision": self.vs_division,
            "GameSegment": self.game_segment,
            "Period": self.period,
            "LastNGames": self.last_n_games,
        }
