from pydantic import BaseModel

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.usage_statistics import UsageStatistics


class Player(PandasMixin, PolarsMixin, BaseModel):
    personId: int
    firstName: str
    familyName: str
    nameI: str
    playerSlug: str
    position: str
    comment: str
    jerseyNum: str
    statistics: UsageStatistics
