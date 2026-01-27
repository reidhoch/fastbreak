from pydantic import BaseModel

from fastbreak.models.common.arena import Arena
from fastbreak.models.common.broadcaster import Broadcasters
from fastbreak.models.common.chart import Charts
from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.meeting import LastFiveMeetings
from fastbreak.models.common.meta import Meta
from fastbreak.models.common.official import Official
from fastbreak.models.common.summary_team import SummaryTeam


class BoxScoreSummaryData(PandasMixin, PolarsMixin, BaseModel):
    """The main box score summary data."""

    gameId: str
    gameCode: str
    gameStatus: int
    gameStatusText: str
    period: int
    gameClock: str
    gameTimeUTC: str
    gameEt: str
    awayTeamId: int
    homeTeamId: int
    duration: str
    attendance: int
    sellout: int
    seriesGameNumber: str
    gameLabel: str
    gameSubLabel: str
    seriesText: str
    ifNecessary: bool
    isNeutral: bool
    arena: Arena
    officials: list[Official]
    broadcasters: Broadcasters
    homeTeam: SummaryTeam
    awayTeam: SummaryTeam
    lastFiveMeetings: LastFiveMeetings
    pregameCharts: Charts
    postgameCharts: Charts
    videoAvailableFlag: int
    ptAvailable: int
    ptXYZAvailable: int
    whStatus: int
    hustleStatus: int
    historicalStatus: int
    gameSubtype: str


class BoxScoreSummaryResponse(BaseModel):
    """Response from the box score summary endpoint."""

    meta: Meta
    boxScoreSummary: BoxScoreSummaryData
