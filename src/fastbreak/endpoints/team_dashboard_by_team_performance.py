"""Endpoint for fetching team stats by team performance."""

from typing import ClassVar

from fastbreak.endpoints.base import TeamDashboardEndpoint
from fastbreak.models.team_dashboard_by_team_performance import (
    TeamDashboardByTeamPerformanceResponse,
)


class TeamDashboardByTeamPerformance(
    TeamDashboardEndpoint[TeamDashboardByTeamPerformanceResponse]
):
    """Fetch team stats broken down by team performance.

    Team-level counterpart to :class:`PlayerDashboardByTeamPerformance`.
    Returns stats split by score differential, points scored, and points
    allowed.

    Args:
        team_id: NBA team ID (required)
        league_id: League identifier ("00" for NBA)
        season: Season in YYYY-YY format (e.g., "2025-26")
        season_type: Type of season ("Regular Season", "Playoffs", "Pre Season")
        per_mode: Stat mode ("Totals", "PerGame", "Per36", etc.)
        measure_type: Measure type ("Base", "Advanced", "Misc", etc.)
        (plus the standard dashboard filters inherited from
        :class:`TeamDashboardEndpoint`)

    """

    path: ClassVar[str] = "teamdashboardbyteamperformance"
    response_model: ClassVar[type[TeamDashboardByTeamPerformanceResponse]] = (
        TeamDashboardByTeamPerformanceResponse
    )
