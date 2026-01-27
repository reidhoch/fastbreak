from pydantic import BaseModel

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin


class Dunk(PandasMixin, PolarsMixin, BaseModel):
    """Individual dunk with scores and biomechanical data."""

    # Game context
    gameId: str
    gameDate: str
    matchup: str
    period: int
    gameClockTime: str
    eventNum: int

    # Player info
    playerId: int
    playerName: str
    firstName: str
    lastName: str

    # Team info
    teamId: int
    teamName: str
    teamCity: str
    teamAbbreviation: str

    # Dunk scores
    dunkScore: float
    jumpSubscore: float
    powerSubscore: float
    styleSubscore: float
    defensiveContestSubscore: float

    # Biomechanics
    maxBallHeight: float
    ballSpeedThroughRim: float
    playerVertical: float
    hangTime: float
    takeoffDistance: float
    playerRotation: float
    playerLateralSpeed: float
    ballDistanceTraveled: float
    ballReachBack: float
    totalBallAcceleration: float

    # Style flags
    reverseDunk: bool
    dunk360: bool
    throughTheLegs: bool
    alleyOop: bool
    tipIn: bool
    selfOop: bool

    # Execution details
    dunkingHand: str
    jumpingFoot: str

    # Pass/assist data (empty when self-created)
    passLength: float
    catchingHand: str
    catchDistance: float
    lateralCatchDistance: float
    passerId: int
    passerName: str
    passerFirstName: str
    passerLastName: str
    passReleasePoint: str

    # Shot contest data (for tip-ins off missed shots)
    shooterId: int
    shooterName: str
    shooterFirstName: str
    shooterLastName: str
    shotReleasePoint: str
    shotLength: float

    # Defense
    defensiveContestLevel: float
    possibleAttemptedCharge: bool

    # Media
    videoAvailable: bool


class DunkScoreLeadersResponse(BaseModel):
    """Response from dunk score leaders endpoint."""

    params: dict[str, str | int | None]
    dunks: list[Dunk]
