from pydantic import BaseModel

from fastbreak.models.common.arena import Arena
from fastbreak.models.common.broadcaster import Broadcasters
from fastbreak.models.common.chart import Charts
from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.meeting import LastFiveMeetings
from fastbreak.models.common.meta import Meta
from fastbreak.models.common.official import Official
from fastbreak.models.common.response import FrozenResponse
from fastbreak.models.common.summary_team import SummaryTeam


class BoxScoreSummaryData(PandasMixin, PolarsMixin, BaseModel):
    """The main box score summary data."""

    gameId: str | None = None
    gameCode: str | None = None
    gameStatus: int = 0
    gameStatusText: str | None = None
    period: int = 0
    gameClock: str | None = None
    gameTimeUTC: str | None = None
    gameEt: str | None = None
    awayTeamId: int = 0
    homeTeamId: int = 0
    duration: str | None = None
    attendance: int = 0
    sellout: int = 0
    seriesGameNumber: str | None = None
    gameLabel: str | None = None
    gameSubLabel: str | None = None
    seriesText: str | None = None
    ifNecessary: bool | None = None
    isNeutral: bool | None = None
    arena: Arena | None = None
    officials: list[Official] = []
    broadcasters: Broadcasters | None = None
    homeTeam: SummaryTeam | None = None
    awayTeam: SummaryTeam | None = None
    lastFiveMeetings: LastFiveMeetings | None = None
    pregameCharts: Charts | None = None
    postgameCharts: Charts | None = None
    videoAvailableFlag: int = 0
    ptAvailable: int = 0
    ptXYZAvailable: int = 0
    whStatus: int = 0
    hustleStatus: int = 0
    historicalStatus: int = 0
    gameSubtype: str | None = None


class BoxScoreSummaryResponse(FrozenResponse):
    """Response from the box score summary endpoint."""

    meta: Meta
    boxScoreSummary: BoxScoreSummaryData
