from pydantic import BaseModel

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin


class Period(PandasMixin, PolarsMixin, BaseModel):
    period: int
    periodType: str
    score: int
