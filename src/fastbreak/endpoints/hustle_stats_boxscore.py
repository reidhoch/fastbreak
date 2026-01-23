"""Hustle stats box score endpoint."""

from dataclasses import dataclass
from typing import ClassVar

from fastbreak.endpoints.base import GameIdEndpoint
from fastbreak.models.hustle_stats_boxscore import HustleStatsBoxscoreResponse


@dataclass(frozen=True)
class HustleStatsBoxscore(GameIdEndpoint[HustleStatsBoxscoreResponse]):
    """Fetch hustle statistics for a specific game.

    Hustle stats include contested shots, deflections, loose balls recovered,
    screen assists, charges drawn, and box outs at both player and team level.

    Args:
        game_id: NBA game identifier (e.g., "0022500571")

    """

    path: ClassVar[str] = "hustlestatsboxscore"
    response_model: ClassVar[type[HustleStatsBoxscoreResponse]] = (
        HustleStatsBoxscoreResponse
    )
