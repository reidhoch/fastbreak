"""Endpoint for video availability status."""

from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.video_status import VideoStatusResponse
from fastbreak.types import LeagueID


class VideoStatus(Endpoint[VideoStatusResponse]):
    """Fetch video availability status for games on a given date.

    Returns information about which games have video available
    (full game video, play-by-play video, etc.).

    Args:
        league_id: League identifier ("00" for NBA, "10" for WNBA, "20" for G-League)
        game_date: Date to check video status for (MM/DD/YYYY format)

    """

    path: ClassVar[str] = "videostatus"
    response_model: ClassVar[type[VideoStatusResponse]] = VideoStatusResponse

    league_id: LeagueID = "00"
    game_date: str = ""

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {
            "LeagueID": self.league_id,
            "GameDate": self.game_date,
        }
