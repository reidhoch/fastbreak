"""Shot chart detail endpoint for individual shot location data."""

from dataclasses import dataclass
from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.shot_chart_detail import ShotChartDetailResponse


@dataclass(frozen=True)
class ShotChartDetail(Endpoint[ShotChartDetailResponse]):
    """Fetch shot chart data with x/y coordinates for visualization.

    Returns individual shot attempts with location coordinates (LOC_X, LOC_Y)
    and zone classifications, along with league average percentages by zone.

    Args:
        player_id: NBA player ID (required)
        team_id: Team ID filter (0 for all teams)
        league_id: League identifier ("00" for NBA)
        season: Season in YYYY-YY format (e.g., "2024-25")
        season_type: Type of season ("Regular Season", "Playoffs", "Pre Season")
        context_measure: Shot type ("FGA", "FGM", "FG3A", "FG3M", etc.)
        game_id: Filter by specific game ID
        opponent_team_id: Filter by opponent team ID
        period: Filter by period (0 for all)
        last_n_games: Filter to last N games (0 for all)
        month: Filter by month (0 for all)
        location: Filter by game location ("Home", "Road")
        outcome: Filter by game outcome ("W", "L")
        date_from: Filter games from date (MM/DD/YYYY)
        date_to: Filter games to date (MM/DD/YYYY)
        vs_conference: Filter by opponent conference ("East", "West")
        vs_division: Filter by opponent division
        game_segment: Filter by game segment ("First Half", "Second Half", "Overtime")
        season_segment: Filter by season segment ("Pre All-Star", "Post All-Star")
        player_position: Filter by position ("Guard", "Forward", "Center")
        rookie_year: Filter by rookie year

    """

    path: ClassVar[str] = "shotchartdetail"
    response_model: ClassVar[type[ShotChartDetailResponse]] = ShotChartDetailResponse

    # Required parameters
    player_id: int = 0
    team_id: int = 0
    league_id: str = "00"
    season: str = "2024-25"
    season_type: str = "Regular Season"
    context_measure: str = "FGA"

    # Optional filters
    game_id: str | None = None
    opponent_team_id: int | None = None
    period: int | None = None
    last_n_games: int | None = None
    month: int | None = None
    location: str | None = None
    outcome: str | None = None
    date_from: str | None = None
    date_to: str | None = None
    vs_conference: str | None = None
    vs_division: str | None = None
    game_segment: str | None = None
    season_segment: str | None = None
    player_position: str | None = None
    rookie_year: str | None = None

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        result: dict[str, str] = {
            "PlayerID": str(self.player_id),
            "TeamID": str(self.team_id),
            "LeagueID": self.league_id,
            "Season": self.season,
            "SeasonType": self.season_type,
            "ContextMeasure": self.context_measure,
        }

        # Map of optional attributes to API parameter names
        optional_params = {
            "game_id": "GameID",
            "opponent_team_id": "OpponentTeamID",
            "period": "Period",
            "last_n_games": "LastNGames",
            "month": "Month",
            "location": "Location",
            "outcome": "Outcome",
            "date_from": "DateFrom",
            "date_to": "DateTo",
            "vs_conference": "VsConference",
            "vs_division": "VsDivision",
            "game_segment": "GameSegment",
            "season_segment": "SeasonSegment",
            "player_position": "PlayerPosition",
            "rookie_year": "RookieYear",
        }

        for attr, param_name in optional_params.items():
            value = getattr(self, attr)
            if value is not None:
                result[param_name] = str(value)

        return result
