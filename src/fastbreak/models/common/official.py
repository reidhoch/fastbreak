from pydantic import BaseModel

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin


class Official(PandasMixin, PolarsMixin, BaseModel):
    personId: int
    name: str
    nameI: str
    firstName: str
    familyName: str
    jerseyNum: str
    assignment: str
