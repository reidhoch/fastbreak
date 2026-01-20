from fastbreak.endpoints.base import GameEndpoint
from fastbreak.models import BoxScoreFourFactorsResponse


class BoxScoreFourFactors(GameEndpoint[BoxScoreFourFactorsResponse]):
    """Fetch four factors box score statistics for a game.

    The four factors are: effective field goal percentage, free throw rate,
    turnover percentage, and offensive rebound percentage. Both offensive
    and defensive (opponent) versions are included.
    """

    path = "boxscorefourfactorsv3"
    response_model = BoxScoreFourFactorsResponse
