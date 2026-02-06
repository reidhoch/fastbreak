from pydantic import BaseModel

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.meta import Meta
from fastbreak.models.common.response import FrozenResponse
from fastbreak.models.common.usage_statistics import UsageStatistics


class UsagePlayer(PandasMixin, PolarsMixin, BaseModel):
    """Player with usage statistics."""

    personId: int
    firstName: str
    familyName: str
    nameI: str
    playerSlug: str
    position: str
    comment: str
    jerseyNum: str
    statistics: UsageStatistics


class UsageTeam(PandasMixin, PolarsMixin, BaseModel):
    """Team with players and usage statistics."""

    teamId: int
    teamCity: str
    teamName: str
    teamTricode: str
    teamSlug: str
    players: list[UsagePlayer]
    statistics: UsageStatistics


class BoxScoreUsageData(PandasMixin, PolarsMixin, BaseModel):
    """Box score usage data for a game."""

    gameId: str
    awayTeamId: int
    homeTeamId: int
    homeTeam: UsageTeam
    awayTeam: UsageTeam


class BoxScoreUsageResponse(FrozenResponse):
    """Response from the boxscoreusage endpoint."""

    meta: Meta
    boxScoreUsage: BoxScoreUsageData
