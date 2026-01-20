from fastbreak.endpoints.base import GameEndpoint
from fastbreak.models.play_by_play import PlayByPlayResponse


class PlayByPlay(GameEndpoint[PlayByPlayResponse]):
    """Fetch play-by-play data for a game.

    Returns all actions/events that occurred during the game,
    including shots, turnovers, fouls, substitutions, and more.
    """

    path = "playbyplayv3"
    response_model = PlayByPlayResponse
