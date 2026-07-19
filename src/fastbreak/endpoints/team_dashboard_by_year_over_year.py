"""Endpoint for fetching team stats year over year."""

from typing import ClassVar

from fastbreak.endpoints.base import TeamDashboardEndpoint
from fastbreak.models.team_dashboard_by_year_over_year import (
    TeamDashboardByYearOverYearResponse,
)


class TeamDashboardByYearOverYear(
    TeamDashboardEndpoint[TeamDashboardByYearOverYearResponse]
):
    """Fetch team stats broken down season over season.

    Team-level counterpart to :class:`PlayerDashboardByYearOverYear`. Returns
    overall stats plus one row per season the franchise has played.

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

    path: ClassVar[str] = "teamdashboardbyyearoveryear"
    response_model: ClassVar[type[TeamDashboardByYearOverYearResponse]] = (
        TeamDashboardByYearOverYearResponse
    )
