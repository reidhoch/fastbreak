from pydantic import BaseModel

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.meta import Meta
from fastbreak.models.common.player_track_statistics import (
    PlayerTrackStatistics,
    TeamPlayerTrackStatistics,
)
from fastbreak.models.common.response import FrozenResponse


class PlayerTrackPlayer(PandasMixin, PolarsMixin, BaseModel):
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


class PlayerTrackTeam(PandasMixin, PolarsMixin, BaseModel):
    """Team with players and tracking statistics."""

    teamId: int
    teamCity: str
    teamName: str
    teamTricode: str
    teamSlug: str
    players: list[PlayerTrackPlayer]
    statistics: TeamPlayerTrackStatistics


class BoxScorePlayerTrackData(PandasMixin, PolarsMixin, BaseModel):
    """Box score player tracking data for a game."""

    gameId: str
    awayTeamId: int
    homeTeamId: int
    homeTeam: PlayerTrackTeam
    awayTeam: PlayerTrackTeam


class BoxScorePlayerTrackResponse(FrozenResponse):
    """Response from the boxscoreplayertrack endpoint."""

    meta: Meta
    boxScorePlayerTrack: BoxScorePlayerTrackData
