"""Endpoint for fetching team stats by last N games."""

from typing import ClassVar

from fastbreak.endpoints.base import TeamDashboardEndpoint
from fastbreak.models.team_dashboard_by_last_n_games import (
    TeamDashboardByLastNGamesResponse,
)


class TeamDashboardByLastNGames(
    TeamDashboardEndpoint[TeamDashboardByLastNGamesResponse]
):
    """Fetch team stats broken down by recent-game windows.

    Team-level counterpart to :class:`PlayerDashboardByLastNGames`. Returns
    overall stats plus the last 5/10/15/20 games and a per-game-number split.

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

    path: ClassVar[str] = "teamdashboardbylastngames"
    response_model: ClassVar[type[TeamDashboardByLastNGamesResponse]] = (
        TeamDashboardByLastNGamesResponse
    )
