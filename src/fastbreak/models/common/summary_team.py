from typing import Any

from pydantic import BaseModel

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.period import Period
from fastbreak.models.common.summary_player import InactivePlayer, SummaryPlayer


class SummaryTeam(PandasMixin, PolarsMixin, BaseModel):
    """Team info as it appears in box score summary.

    Note: Some fields are optional because the NBA API returns null values
    for certain games where this data was not tracked or is not yet available.
    """

    teamId: int
    teamName: str | None = None
    teamCity: str | None = None
    teamTricode: str | None = None
    teamSlug: str | None = None
    teamWins: int
    teamLosses: int
    score: int
    inBonus: str
    timeoutsRemaining: int
    seed: int
    statistics: dict[str, Any]
    periods: list[Period]
    players: list[SummaryPlayer]
    inactives: list[InactivePlayer]
