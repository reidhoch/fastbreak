from typing import Any

from pydantic import BaseModel

from fastbreak.models.common.period import Period
from fastbreak.models.common.summary_player import InactivePlayer, SummaryPlayer


class SummaryTeam(BaseModel):
    """Team info as it appears in box score summary."""

    teamId: int
    teamName: str
    teamCity: str
    teamTricode: str
    teamSlug: str
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
