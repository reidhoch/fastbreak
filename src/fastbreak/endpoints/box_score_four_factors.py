from dataclasses import dataclass
from typing import ClassVar

from fastbreak.endpoints.base import GameIdEndpoint
from fastbreak.models import BoxScoreFourFactorsResponse


@dataclass(frozen=True)
class BoxScoreFourFactors(GameIdEndpoint[BoxScoreFourFactorsResponse]):
    """Fetch four factors box score statistics for a game.

    The four factors are: effective field goal percentage, free throw rate,
    turnover percentage, and offensive rebound percentage. Both offensive
    and defensive (opponent) versions are included.
    """

    path: ClassVar[str] = "boxscorefourfactorsv3"
    response_model: ClassVar[type[BoxScoreFourFactorsResponse]] = (
        BoxScoreFourFactorsResponse
    )
