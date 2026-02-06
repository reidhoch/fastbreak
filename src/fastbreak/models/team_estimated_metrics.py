"""Models for the Team Estimated Metrics endpoint response."""

from typing import Any

from pydantic import BaseModel, Field, model_validator

from fastbreak.logging import logger
from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.response import FrozenResponse


class TeamEstimatedMetric(PandasMixin, PolarsMixin, BaseModel):
    """Estimated advanced metrics for a team.

    Contains estimated offensive/defensive ratings, efficiency percentages,
    and league-wide rankings for each metric.
    """

    # Basic info
    team_name: str = Field(alias="TEAM_NAME")
    team_id: int = Field(alias="TEAM_ID")
    gp: int = Field(alias="GP")
    wins: int = Field(alias="W")
    losses: int = Field(alias="L")
    win_pct: float | None = Field(alias="W_PCT")
    minutes: float = Field(alias="MIN")

    # Estimated metrics
    e_off_rating: float | None = Field(alias="E_OFF_RATING")
    e_def_rating: float | None = Field(alias="E_DEF_RATING")
    e_net_rating: float | None = Field(alias="E_NET_RATING")
    e_pace: float | None = Field(alias="E_PACE")
    e_ast_ratio: float | None = Field(alias="E_AST_RATIO")
    e_oreb_pct: float | None = Field(alias="E_OREB_PCT")
    e_dreb_pct: float | None = Field(alias="E_DREB_PCT")
    e_reb_pct: float | None = Field(alias="E_REB_PCT")
    e_tm_tov_pct: float | None = Field(alias="E_TM_TOV_PCT")

    # Rankings
    gp_rank: int | None = Field(alias="GP_RANK")
    w_rank: int | None = Field(alias="W_RANK")
    l_rank: int | None = Field(alias="L_RANK")
    w_pct_rank: int | None = Field(alias="W_PCT_RANK")
    min_rank: int | None = Field(alias="MIN_RANK")
    e_off_rating_rank: int | None = Field(alias="E_OFF_RATING_RANK")
    e_def_rating_rank: int | None = Field(alias="E_DEF_RATING_RANK")
    e_net_rating_rank: int | None = Field(alias="E_NET_RATING_RANK")
    e_ast_ratio_rank: int | None = Field(alias="E_AST_RATIO_RANK")
    e_oreb_pct_rank: int | None = Field(alias="E_OREB_PCT_RANK")
    e_dreb_pct_rank: int | None = Field(alias="E_DREB_PCT_RANK")
    e_reb_pct_rank: int | None = Field(alias="E_REB_PCT_RANK")
    e_tm_tov_pct_rank: int | None = Field(alias="E_TM_TOV_PCT_RANK")
    e_pace_rank: int | None = Field(alias="E_PACE_RANK")


class TeamEstimatedMetricsResponse(FrozenResponse):
    """Response from the team estimated metrics endpoint.

    Contains estimated advanced metrics for all teams in the league.
    """

    teams: list[TeamEstimatedMetric] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def from_result_set(cls, data: object) -> dict[str, Any]:
        """Transform NBA's singular resultSet format into structured data."""
        if not isinstance(data, dict):
            logger.debug(
                "team_estimated_metrics_passthrough",
                actual_type=type(data).__name__,
                hint="Expected dict with 'resultSet' key",
            )
            return data  # type: ignore[return-value]

        # This endpoint uses singular 'resultSet' instead of 'resultSets'
        result_set = data.get("resultSet")
        if not result_set or not isinstance(result_set, dict):
            logger.debug(
                "team_estimated_metrics_passthrough",
                keys=list(data.keys())[:10],
                has_result_set=result_set is not None,
                hint="Expected 'resultSet' key with dict value",
            )
            return data

        headers = result_set.get("headers", [])
        rows = result_set.get("rowSet", [])

        return {
            "teams": [dict(zip(headers, row, strict=True)) for row in rows],
        }
