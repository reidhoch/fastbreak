from pydantic import BaseModel

from fastbreak.models.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.meta import Meta
from fastbreak.models.traditional_statistics import (
    TraditionalGroupStatistics,
    TraditionalStatistics,
)


class TraditionalPlayer(PandasMixin, PolarsMixin):
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


class TraditionalTeam(BaseModel):
    """Team with players and traditional statistics."""

    teamId: int
    teamCity: str
    teamName: str
    teamTricode: str
    teamSlug: str
    players: list[TraditionalPlayer]
    statistics: TraditionalStatistics
    starters: TraditionalGroupStatistics
    bench: TraditionalGroupStatistics


class BoxScoreTraditionalData(BaseModel):
    """Box score traditional data for a game."""

    gameId: str
    awayTeamId: int
    homeTeamId: int
    homeTeam: TraditionalTeam
    awayTeam: TraditionalTeam


class BoxScoreTraditionalResponse(BaseModel):
    """Response from the boxscoretraditional endpoint."""

    meta: Meta
    boxScoreTraditional: BoxScoreTraditionalData
