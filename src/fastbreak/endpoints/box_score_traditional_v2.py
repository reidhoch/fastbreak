"""Box score traditional v2 endpoint."""

from typing import ClassVar

from fastbreak.endpoints.base import GameIdEndpoint
from fastbreak.models.box_score_traditional_v2 import BoxScoreTraditionalV2Response


class BoxScoreTraditionalV2(GameIdEndpoint[BoxScoreTraditionalV2Response]):
    """Fetch traditional box score statistics for a game in v2 format.

    The v2 endpoint returns NBA's tabular result-set format with three
    result sets: per-player stats, per-team stats, and a starter / bench
    aggregation. The key field unique to v2 is ``START_POSITION`` — a
    non-empty string ("F"/"G"/"C") for starters and "" for bench players.
    The v3 endpoint's ``position`` field is the league-registry position
    regardless of role and cannot be used to identify starters.

    Args:
        game_id: NBA game identifier (e.g., "0022400123")

    Example:
        >>> async with NBAClient() as client:
        ...     box = await client.get(BoxScoreTraditionalV2(game_id="0022400123"))
        ...     starters = [p for p in box.player_stats if p.start_position]
        ...     for p in starters:
        ...         print(f"{p.player_name} ({p.start_position}): {p.pts} pts")

    """

    path: ClassVar[str] = "boxscoretraditionalv2"
    response_model: ClassVar[type[BoxScoreTraditionalV2Response]] = (
        BoxScoreTraditionalV2Response
    )
