"""Endpoint for fetching shot chart data with lineup context."""

from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.shot_chart_lineup_detail import ShotChartLineupDetailResponse
from fastbreak.types import (
    Conference,
    ContextMeasure,
    Date,
    Division,
    GameSegment,
    LeagueID,
    Location,
    Outcome,
    Season,
    SeasonSegment,
    SeasonType,
)


class ShotChartLineupDetail(Endpoint[ShotChartLineupDetailResponse]):
    """Fetch shot chart data with lineup grouping information.

    Returns individual shot attempts with location coordinates and lineup
    context (GROUP_ID, GROUP_NAME), along with league average percentages.

    Args:
        league_id: League identifier ("00" for NBA)
        season: Season in YYYY-YY format (e.g., "2024-25")
        season_type: Type of season ("Regular Season", "Playoffs", "Pre Season")
        team_id: Team ID filter (0 for all teams)
        context_measure: Shot type ("FGA", "FGM", "FG3A", "FG3M", etc.)
        game_id: Filter by specific game ID
        group_id: Filter by specific lineup group ID
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
        context_filter: Additional context filter

    """

    path: ClassVar[str] = "shotchartlineupdetail"
    response_model: ClassVar[type[ShotChartLineupDetailResponse]] = (
        ShotChartLineupDetailResponse
    )

    # Required parameters
    team_id: int
    league_id: LeagueID = "00"
    season: Season = "2024-25"
    season_type: SeasonType = "Regular Season"
    context_measure: ContextMeasure = "FGA"

    # Optional filters
    game_id: str | None = None
    group_id: str | None = None
    opponent_team_id: int | None = None
    period: int | None = None
    last_n_games: int | None = None
    month: int | None = None
    location: Location | None = None
    outcome: Outcome | None = None
    date_from: Date | None = None
    date_to: Date | None = None
    vs_conference: Conference | None = None
    vs_division: Division | None = None
    game_segment: GameSegment | None = None
    season_segment: SeasonSegment | None = None
    context_filter: str | None = None

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        result: dict[str, str] = {
            "LeagueID": self.league_id,
            "Season": self.season,
            "SeasonType": self.season_type,
            "TeamID": str(self.team_id),
            "ContextMeasure": self.context_measure,
        }

        # Map of optional attributes to API parameter names
        optional_params = {
            "game_id": "GameID",
            "group_id": "GROUP_ID",
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
            "context_filter": "ContextFilter",
        }

        for attr, param_name in optional_params.items():
            value = getattr(self, attr)
            if value is not None:
                result[param_name] = str(value)

        return result
