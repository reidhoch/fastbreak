"""Player Dashboard by Shooting Splits endpoint for detailed shot analysis."""

from typing import ClassVar

from fastbreak.endpoints.base import PlayerDashboardEndpoint
from fastbreak.models.player_dashboard_by_shooting_splits import (
    PlayerDashboardByShootingSplitsResponse,
)


class PlayerDashboardByShootingSplits(
    PlayerDashboardEndpoint[PlayerDashboardByShootingSplitsResponse]
):
    """Fetch detailed shooting splits by distance, area, and shot type.

    Returns shooting stats split by distance, court area, shot type, and assisting player.

    Args:
        player_id: NBA player ID (required)
        league_id: League identifier ("00" for NBA)
        season: Season in YYYY-YY format (e.g., "2024-25")
        season_type: Type of season ("Regular Season", "Playoffs", "Pre Season")
        per_mode: Stat mode ("Totals", "PerGame", "Per36", etc.)
        measure_type: Measure type ("Base", "Advanced", "Misc", etc.)
        pace_adjust: Whether to pace adjust ("Y", "N")
        plus_minus: Whether to include plus/minus ("Y", "N")
        rank: Whether to include rank ("Y", "N")
        po_round: Playoff round filter (0 for all)
        month: Filter by month (0 for all)
        opponent_team_id: Filter by opponent team ID (0 for all)
        period: Filter by period (0 for all)
        last_n_games: Filter to last N games (0 for all)
        ist_round: In-Season Tournament round filter
        outcome: Filter by game outcome ("W", "L")
        location: Filter by game location ("Home", "Road")
        season_segment: Filter by season segment ("Pre All-Star", "Post All-Star")
        date_from: Filter games from date (MM/DD/YYYY)
        date_to: Filter games to date (MM/DD/YYYY)
        vs_conference: Filter by opponent conference ("East", "West")
        vs_division: Filter by opponent division
        game_segment: Filter by game segment ("First Half", "Second Half", "Overtime")
        shot_clock_range: Filter by shot clock range

    """

    path: ClassVar[str] = "playerdashboardbyshootingsplits"
    response_model: ClassVar[type[PlayerDashboardByShootingSplitsResponse]] = (
        PlayerDashboardByShootingSplitsResponse
    )
