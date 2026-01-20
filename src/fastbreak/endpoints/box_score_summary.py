from fastbreak.endpoints.base import GameEndpoint
from fastbreak.models import BoxScoreSummaryResponse


class BoxScoreSummary(GameEndpoint[BoxScoreSummaryResponse]):
    """Fetch box score summary for a game.

    Returns game metadata, team info, officials, broadcasters,
    last five meetings, and pre/postgame charts.
    """

    path = "boxscoresummaryv3"
    response_model = BoxScoreSummaryResponse
