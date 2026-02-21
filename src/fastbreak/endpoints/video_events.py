"""Video events endpoint."""

from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.video_events import VideoEventsResponse


class VideoEvents(Endpoint[VideoEventsResponse]):
    """Fetch video metadata for a specific play event in a game.

    Returns video URLs and playlist information for an individual play,
    which can be used to access video clips of shots, turnovers,
    fouls, and other game events.

    To use this endpoint effectively, first fetch play-by-play data
    using the PlayByPlay endpoint to get event IDs, then use those
    IDs to retrieve video clips.

    Args:
        game_id: NBA game identifier (e.g., "0022400001")
        game_event_id: Event ID from play-by-play data

    Example:
        >>> async with NBAClient() as client:
        ...     # First get play-by-play to find event IDs
        ...     pbp = await client.get(PlayByPlay(game_id="0022400001"))
        ...     event_id = pbp.game.actions[0].action_number
        ...
        ...     # Then fetch video for that event
        ...     video = await client.get(VideoEvents(
        ...         game_id="0022400001",
        ...         game_event_id=event_id
        ...     ))
        ...     for item in video.result_sets.playlist:
        ...         print(f"Play: {item.description}")

    """

    path: ClassVar[str] = "videoevents"
    response_model: ClassVar[type[VideoEventsResponse]] = VideoEventsResponse

    game_id: str
    game_event_id: int

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {
            "GameID": self.game_id,
            "GameEventID": str(self.game_event_id),
        }
