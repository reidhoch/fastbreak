"""Endpoint for fetching team player dashboard statistics."""

from typing import ClassVar

from fastbreak.endpoints.base import TeamDashboardEndpoint
from fastbreak.models.team_player_dashboard import TeamPlayerDashboardResponse


class TeamPlayerDashboard(TeamDashboardEndpoint[TeamPlayerDashboardResponse]):
    """Fetch team and individual player statistics.

    Returns team aggregate statistics and per-player breakdowns
    with traditional stats, fantasy points, and league rankings.

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

    path: ClassVar[str] = "teamplayerdashboard"
    response_model: ClassVar[type[TeamPlayerDashboardResponse]] = (
        TeamPlayerDashboardResponse
    )
