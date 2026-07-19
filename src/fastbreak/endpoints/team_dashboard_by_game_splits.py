"""Endpoint for fetching team stats by game splits."""

from typing import ClassVar

from fastbreak.endpoints.base import TeamDashboardEndpoint
from fastbreak.models.team_dashboard_by_game_splits import (
    TeamDashboardByGameSplitsResponse,
)


class TeamDashboardByGameSplits(
    TeamDashboardEndpoint[TeamDashboardByGameSplitsResponse]
):
    """Fetch team stats broken down by game splits.

    Team-level counterpart to :class:`PlayerDashboardByGameSplits`. Returns
    stats split by half, period, general score margin, and specific
    score-margin ranges.

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

    path: ClassVar[str] = "teamdashboardbygamesplits"
    response_model: ClassVar[type[TeamDashboardByGameSplitsResponse]] = (
        TeamDashboardByGameSplitsResponse
    )
