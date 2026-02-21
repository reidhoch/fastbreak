"""Box score hustle v2 endpoint."""

from typing import ClassVar

from fastbreak.endpoints.base import GameIdEndpoint
from fastbreak.models.box_score_hustle import BoxScoreHustleResponse


class BoxScoreHustle(GameIdEndpoint[BoxScoreHustleResponse]):
    """Fetch hustle statistics for a specific game in v2 format.

    Returns hustle stats including contested shots, deflections, loose balls
    recovered, screen assists, charges drawn, and box outs for all players
    and both teams.

    This endpoint uses the modern nested JSON format (v2) rather than the
    traditional result sets format. It includes additional player metadata
    like first/last names and player slugs.

    For the traditional result sets format, use HustleStatsBoxscore instead.

    Args:
        game_id: NBA game identifier (e.g., "0022400001")

    Example:
        >>> async with NBAClient() as client:
        ...     hustle = await client.get(BoxScoreHustle(game_id="0022400001"))
        ...     for player in hustle.box_score_hustle.home_team.players:
        ...         print(f"{player.name_i}: {player.statistics.deflections} deflections")

    """

    path: ClassVar[str] = "boxscorehustlev2"
    response_model: ClassVar[type[BoxScoreHustleResponse]] = BoxScoreHustleResponse
