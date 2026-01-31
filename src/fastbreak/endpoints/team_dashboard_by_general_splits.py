"""Endpoint for fetching team stats by general splits."""

from typing import ClassVar

from fastbreak.endpoints.base import TeamDashboardEndpoint
from fastbreak.models.team_dashboard_by_general_splits import (
    TeamDashboardByGeneralSplitsResponse,
)


class TeamDashboardByGeneralSplits(
    TeamDashboardEndpoint[TeamDashboardByGeneralSplitsResponse]
):
    """Fetch team stats broken down by general categories.

    Returns stats split by location, wins/losses, month, pre/post All-Star,
    and days of rest.

    Args:
        team_id: NBA team ID (required)
        league_id: League identifier ("00" for NBA)
        season: Season in YYYY-YY format (e.g., "2024-25")
        season_type: Type of season ("Regular Season", "Playoffs", "Pre Season")
        per_mode: Stat mode ("Totals", "PerGame", "Per36", etc.)
        measure_type: Measure type ("Base", "Advanced", "Misc", etc.)
        pace_adjust: Whether to pace adjust ("Y", "N")
        plus_minus: Whether to include plus/minus ("Y", "N")
        rank: Whether to include rank ("Y", "N")
        outcome: Filter by game outcome ("W", "L")
        location: Filter by game location ("Home", "Road")
        month: Filter by month (0 for all, 1-12 for specific month)
        season_segment: Filter by season segment ("Pre All-Star", "Post All-Star")
        date_from: Filter games from date (MM/DD/YYYY)
        date_to: Filter games to date (MM/DD/YYYY)
        opponent_team_id: Filter by opponent team ID (0 for all)
        vs_conference: Filter by opponent conference ("East", "West")
        vs_division: Filter by opponent division
        game_segment: Filter by game segment ("First Half", "Second Half", "Overtime")
        period: Filter by period (0 for all)
        shot_clock_range: Filter by shot clock range
        last_n_games: Filter to last N games (0 for all)
        po_round: Playoff round filter (0 for all)

    """

    path: ClassVar[str] = "teamdashboardbygeneralsplits"
    response_model: ClassVar[type[TeamDashboardByGeneralSplitsResponse]] = (
        TeamDashboardByGeneralSplitsResponse
    )
