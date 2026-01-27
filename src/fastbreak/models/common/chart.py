from typing import Any

from pydantic import BaseModel

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin


class ChartTeam(PandasMixin, PolarsMixin, BaseModel):
    """Team info with statistics for pre/postgame charts."""

    teamId: int
    teamCity: str
    teamName: str
    teamTricode: str
    statistics: dict[str, Any]


class Charts(PandasMixin, PolarsMixin, BaseModel):
    """Pre or postgame chart data for both teams."""

    homeTeam: ChartTeam
    awayTeam: ChartTeam
