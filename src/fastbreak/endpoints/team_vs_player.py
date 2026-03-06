"""Endpoint for comparing team performance against a specific player."""

from typing import ClassVar

from fastbreak.endpoints.base import TeamDashboardEndpoint
from fastbreak.models.team_vs_player import TeamVsPlayerResponse


class TeamVsPlayer(TeamDashboardEndpoint[TeamVsPlayerResponse]):
    """Fetch team statistics when facing a specific player.

    Shows how teams perform against a particular player, including
    on/off court splits and shooting breakdown by distance and area.

    Args:
        team_id: NBA team ID (required)
        vs_player_id: Target player ID to compare against (required)
        season: Season in YYYY-YY format (e.g., "2024-25")
        season_type: Type of season ("Regular Season", "Playoffs", etc.)
        per_mode: Stat mode ("PerGame", "Totals", "Per36", etc.)
        measure_type: Measure type ("Base", "Advanced", etc.)
        league_id: League identifier ("00" for NBA)

    """

    path: ClassVar[str] = "teamvsplayer"
    response_model: ClassVar[type[TeamVsPlayerResponse]] = TeamVsPlayerResponse

    vs_player_id: int

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        result = super().params()
        result["VsPlayerID"] = str(self.vs_player_id)
        return result
