from pydantic import BaseModel

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.meta import Meta
from fastbreak.models.common.response import FrozenResponse
from fastbreak.models.common.traditional_statistics import (
    TraditionalGroupStatistics,
    TraditionalStatistics,
)


class TraditionalPlayer(PandasMixin, PolarsMixin, BaseModel):
    """Player with traditional statistics."""

    personId: int
    firstName: str
    familyName: str
    nameI: str
    playerSlug: str
    position: str
    comment: str
    jerseyNum: str
    statistics: TraditionalStatistics


class TraditionalTeam(PandasMixin, PolarsMixin, BaseModel):
    """Team with players and traditional statistics.

    Note: Some fields are optional because the NBA API returns null values
    for certain games where this data was not tracked or is not yet available.
    """

    teamId: int
    teamCity: str | None = None
    teamName: str | None = None
    teamTricode: str | None = None
    teamSlug: str | None = None
    players: list[TraditionalPlayer]
    statistics: TraditionalStatistics
    starters: TraditionalGroupStatistics | None = None
    bench: TraditionalGroupStatistics | None = None


class BoxScoreTraditionalData(PandasMixin, PolarsMixin, BaseModel):
    """Box score traditional data for a game."""

    gameId: str
    awayTeamId: int
    homeTeamId: int
    homeTeam: TraditionalTeam
    awayTeam: TraditionalTeam


class BoxScoreTraditionalResponse(FrozenResponse):
    """Response from the boxscoretraditional endpoint."""

    meta: Meta
    boxScoreTraditional: BoxScoreTraditionalData
