from dataclasses import dataclass
from typing import ClassVar

from fastbreak.endpoints.base import GameIdEndpoint
from fastbreak.models import BoxScoreUsageResponse


@dataclass(frozen=True)
class BoxScoreUsage(GameIdEndpoint[BoxScoreUsageResponse]):
    """Fetch usage percentage statistics for a game.

    This endpoint shows each player's share of team statistics while
    on the court, including their percentage of field goals, rebounds,
    assists, turnovers, steals, blocks, and points.
    """

    path: ClassVar[str] = "boxscoreusagev3"
    response_model: ClassVar[type[BoxScoreUsageResponse]] = BoxScoreUsageResponse
