from pydantic import BaseModel

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin


class Meta(PandasMixin, PolarsMixin, BaseModel):
    version: int
    request: str
    time: str
