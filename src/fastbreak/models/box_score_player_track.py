from pydantic import BaseModel

from fastbreak.models.meta import Meta
from fastbreak.models.player_track_statistics import (
    PlayerTrackStatistics,
    TeamPlayerTrackStatistics,
)


class PlayerTrackPlayer(BaseModel):
    """Player with tracking statistics."""

    personId: int
    firstName: str
    familyName: str
    nameI: str
    playerSlug: str
    position: str
    comment: str
    jerseyNum: str
    statistics: PlayerTrackStatistics


class PlayerTrackTeam(BaseModel):
    """Team with players and tracking statistics."""

    teamId: int
    teamCity: str
    teamName: str
    teamTricode: str
    teamSlug: str
    players: list[PlayerTrackPlayer]
    statistics: TeamPlayerTrackStatistics


class BoxScorePlayerTrackData(BaseModel):
    """Box score player tracking data for a game."""

    gameId: str
    awayTeamId: int
    homeTeamId: int
    homeTeam: PlayerTrackTeam
    awayTeam: PlayerTrackTeam


class BoxScorePlayerTrackResponse(BaseModel):
    """Response from the boxscoreplayertrack endpoint."""

    meta: Meta
    boxScorePlayerTrack: BoxScorePlayerTrackData
