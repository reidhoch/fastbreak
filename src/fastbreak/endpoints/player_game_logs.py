"""Player Game Logs endpoint for extended game statistics with rankings."""

from typing import ClassVar

from fastbreak.endpoints.base import PlayerSeasonEndpoint
from fastbreak.models.player_game_logs import PlayerGameLogsResponse


class PlayerGameLogs(PlayerSeasonEndpoint[PlayerGameLogsResponse]):
    """Fetch extended game-by-game statistics for a player.

    Returns traditional box score stats plus rankings and fantasy points
    for each game played in a season.

    Args:
        player_id: NBA player ID (required)
        league_id: League identifier ("00" for NBA)
        season: Season in YYYY-YY format (e.g., "2024-25")
        season_type: Type of season ("Regular Season", "Playoffs", "Pre Season")

    """

    path: ClassVar[str] = "playergamelogs"
    response_model: ClassVar[type[PlayerGameLogsResponse]] = PlayerGameLogsResponse
