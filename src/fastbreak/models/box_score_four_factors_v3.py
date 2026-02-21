"""Models for the box score four factors v3 endpoint."""

from pydantic import BaseModel, Field

from fastbreak.models.common.box_score_v3 import (
    BoxScoreDataV3Base,
    BoxScorePlayerV3,
    BoxScoreTeamV3,
)
from fastbreak.models.common.meta import Meta
from fastbreak.models.common.response import FrozenResponse


class FourFactorsStatisticsV3(BaseModel):
    """Four factors statistics in V3 format."""

    minutes: str
    effective_field_goal_percentage: float = Field(alias="effectiveFieldGoalPercentage")
    free_throw_attempt_rate: float = Field(alias="freeThrowAttemptRate")
    team_turnover_percentage: float = Field(alias="teamTurnoverPercentage")
    offensive_rebound_percentage: float = Field(alias="offensiveReboundPercentage")
    opp_effective_field_goal_percentage: float = Field(
        alias="oppEffectiveFieldGoalPercentage"
    )
    opp_free_throw_attempt_rate: float = Field(alias="oppFreeThrowAttemptRate")
    opp_team_turnover_percentage: float = Field(alias="oppTeamTurnoverPercentage")
    opp_offensive_rebound_percentage: float = Field(
        alias="oppOffensiveReboundPercentage"
    )


class FourFactorsPlayerV3(BoxScorePlayerV3[FourFactorsStatisticsV3]):
    """Player with four factors statistics in V3 format."""


class FourFactorsTeamV3(BoxScoreTeamV3[FourFactorsStatisticsV3]):
    """Team with four factors statistics in V3 format."""

    players: list[FourFactorsPlayerV3]  # type: ignore[assignment]


class BoxScoreFourFactorsV3Data(BoxScoreDataV3Base):
    """Four factors box score data in V3 format."""

    home_team: FourFactorsTeamV3 = Field(alias="homeTeam")
    away_team: FourFactorsTeamV3 = Field(alias="awayTeam")


class BoxScoreFourFactorsV3Response(FrozenResponse):
    """Response from the box score four factors v3 endpoint.

    Contains Dean Oliver's "Four Factors" analytics (eFG%, FTA rate,
    turnover rate, offensive rebounding) in modern nested JSON format.
    """

    meta: Meta
    box_score_four_factors: BoxScoreFourFactorsV3Data = Field(
        alias="boxScoreFourFactors"
    )
