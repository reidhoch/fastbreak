from pydantic import BaseModel

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.meta import Meta
from fastbreak.models.common.response import FrozenResponse


class PlayByPlayAction(PandasMixin, PolarsMixin, BaseModel):
    """A single play-by-play action in a game.

    Represents events like shots, turnovers, fouls, substitutions, etc.
    Court coordinates (xLegacy, yLegacy) are provided for shot attempts.
    """

    actionNumber: int
    clock: str
    period: int
    teamId: int
    teamTricode: str
    personId: int
    playerName: str
    playerNameI: str
    xLegacy: int
    yLegacy: int
    shotDistance: int
    shotResult: str
    isFieldGoal: int
    scoreHome: str
    scoreAway: str
    pointsTotal: int
    location: str
    description: str
    actionType: str
    subType: str
    videoAvailable: int
    shotValue: int
    actionId: int


class PlayByPlayGame(PandasMixin, PolarsMixin, BaseModel):
    """Play-by-play data for a single game."""

    gameId: str
    videoAvailable: int
    actions: list[PlayByPlayAction]


class PlayByPlayResponse(FrozenResponse):
    """Response from the play-by-play endpoint."""

    meta: Meta
    game: PlayByPlayGame
