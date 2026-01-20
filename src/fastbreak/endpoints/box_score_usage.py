from fastbreak.endpoints.base import GameEndpoint
from fastbreak.models import BoxScoreUsageResponse


class BoxScoreUsage(GameEndpoint[BoxScoreUsageResponse]):
    """Fetch usage percentage statistics for a game.

    This endpoint shows each player's share of team statistics while
    on the court, including their percentage of field goals, rebounds,
    assists, turnovers, steals, blocks, and points.
    """

    path = "boxscoreusagev3"
    response_model = BoxScoreUsageResponse
