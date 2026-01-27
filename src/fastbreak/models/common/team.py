from pydantic import BaseModel

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.player import Player
from fastbreak.models.common.usage_statistics import UsageStatistics


class Team(PandasMixin, PolarsMixin, BaseModel):
    teamId: int
    teamCity: str
    teamName: str
    teamTricode: str
    teamSlug: str
    players: list[Player]
    statistics: UsageStatistics
