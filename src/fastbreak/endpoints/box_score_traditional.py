from fastbreak.endpoints.base import GameEndpoint
from fastbreak.models import BoxScoreTraditionalResponse


class BoxScoreTraditional(GameEndpoint[BoxScoreTraditionalResponse]):
    """Fetch traditional box score statistics for a game.

    This endpoint provides standard box score statistics including
    field goals, three-pointers, free throws, rebounds, assists,
    steals, blocks, turnovers, fouls, points, and plus/minus.
    Also includes aggregated starters and bench statistics per team.
    """

    path = "boxscoretraditionalv3"
    response_model = BoxScoreTraditionalResponse
