"""Endpoint for fetching team stats by clutch-time scenarios."""

from typing import ClassVar

from fastbreak.endpoints.base import TeamDashboardEndpoint
from fastbreak.models.team_dashboard_by_clutch import (
    TeamDashboardByClutchResponse,
)


class TeamDashboardByClutch(TeamDashboardEndpoint[TeamDashboardByClutchResponse]):
    """Fetch team stats broken down by clutch-time scenarios.

    Team-level counterpart to :class:`PlayerDashboardByClutch`. Returns stats
    for the standard clutch definitions (last 5/3/1 min within 5 pts, last
    30/10 sec within 3 pts, plus the plus/minus variants).

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

    path: ClassVar[str] = "teamdashboardbyclutch"
    response_model: ClassVar[type[TeamDashboardByClutchResponse]] = (
        TeamDashboardByClutchResponse
    )
