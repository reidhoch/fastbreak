from pydantic import BaseModel

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.meta import Meta
from fastbreak.models.common.scoring_statistics import ScoringStatistics


class ScoringPlayer(PandasMixin, PolarsMixin, BaseModel):
    """Player with scoring distribution statistics."""

    personId: int
    firstName: str
    familyName: str
    nameI: str
    playerSlug: str
    position: str
    comment: str
    jerseyNum: str
    statistics: ScoringStatistics


class ScoringTeam(PandasMixin, PolarsMixin, BaseModel):
    """Team with players and scoring distribution statistics."""

    teamId: int
    teamCity: str
    teamName: str
    teamTricode: str
    teamSlug: str
    players: list[ScoringPlayer]
    statistics: ScoringStatistics


class BoxScoreScoringData(PandasMixin, PolarsMixin, BaseModel):
    """Box score scoring data for a game."""

    gameId: str
    awayTeamId: int
    homeTeamId: int
    homeTeam: ScoringTeam
    awayTeam: ScoringTeam


class BoxScoreScoringResponse(BaseModel):
    """Response from the boxscorescoring endpoint."""

    meta: Meta
    boxScoreScoring: BoxScoreScoringData
