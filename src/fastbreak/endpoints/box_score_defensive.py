"""Box score defensive v2 endpoint."""

from typing import ClassVar

from fastbreak.endpoints.base import GameIdEndpoint
from fastbreak.models.box_score_defensive import BoxScoreDefensiveResponse


class BoxScoreDefensive(GameIdEndpoint[BoxScoreDefensiveResponse]):
    """Fetch defensive statistics for a specific game in v2 format.

    Returns matchup-based defensive stats for all players, showing how
    opponents performed while being guarded by each player. Includes
    matchup field goals allowed, defensive rebounds, steals, blocks,
    and partial possessions defended.

    This endpoint uses the modern nested JSON format (v2) rather than the
    traditional result sets format. It includes additional player metadata
    like first/last names and player slugs.

    Args:
        game_id: NBA game identifier (e.g., "0022400001")

    Example:
        >>> async with NBAClient() as client:
        ...     defense = await client.get(BoxScoreDefensive(game_id="0022400001"))
        ...     for player in defense.box_score_defensive.home_team.players:
        ...         stats = player.statistics
        ...         print(f"{player.name_i}: {stats.matchup_field_goal_percentage:.1%} opp FG%")

    """

    path: ClassVar[str] = "boxscoredefensivev2"
    response_model: ClassVar[type[BoxScoreDefensiveResponse]] = (
        BoxScoreDefensiveResponse
    )
