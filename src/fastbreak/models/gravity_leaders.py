from pydantic import BaseModel, ConfigDict

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.response import FrozenResponse


class GravityLeader(PandasMixin, PolarsMixin, BaseModel):
    model_config = ConfigDict(alias_generator=str.upper, populate_by_name=True)

    PlayerID: int
    FirstName: str
    LastName: str
    TeamID: int
    TeamAbbreviation: str
    TeamName: str
    TeamCity: str
    Frames: int
    GravityScore: float
    AvgGravityScore: float
    OnBallPerimeterFrames: int
    OnBallPerimeterGravityScore: float
    AvgOnBallPerimeterGravityScore: float
    OffBallPerimeterFrames: int
    OffBallPerimeterGravityScore: float
    AvgOffBallPerimeterGravityScore: float
    OnBallInteriorFrames: int
    OnBallInteriorGravityScore: float
    AvgOnBallInteriorGravityScore: float
    OffBallInteriorFrames: int
    OffBallInteriorGravityScore: float
    AvgOffBallInteriorGravityScore: float
    GamesPlayed: int
    Minutes: float
    PTS: float
    REB: float
    AST: float


class GravityLeadersResponse(FrozenResponse):
    params: dict[str, str]
    leaders: list[GravityLeader]
