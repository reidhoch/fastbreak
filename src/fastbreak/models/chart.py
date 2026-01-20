from typing import Any

from pydantic import BaseModel


class ChartTeam(BaseModel):
    """Team info with statistics for pre/postgame charts."""

    teamId: int
    teamCity: str
    teamName: str
    teamTricode: str
    statistics: dict[str, Any]


class Charts(BaseModel):
    """Pre or postgame chart data for both teams."""

    homeTeam: ChartTeam
    awayTeam: ChartTeam
