from dataclasses import dataclass
from typing import ClassVar

from fastbreak.endpoints.base import GameIdEndpoint
from fastbreak.models import BoxScoreSummaryResponse


@dataclass(frozen=True)
class BoxScoreSummary(GameIdEndpoint[BoxScoreSummaryResponse]):
    """Fetch box score summary for a game.

    Returns game metadata, team info, officials, broadcasters,
    last five meetings, and pre/postgame charts.
    """

    path: ClassVar[str] = "boxscoresummaryv3"
    response_model: ClassVar[type[BoxScoreSummaryResponse]] = BoxScoreSummaryResponse
