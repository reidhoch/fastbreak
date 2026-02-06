"""Models for the Player Dashboard Rebounding endpoint response."""

from typing import Any

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.response import FrozenResponse
from fastbreak.models.common.result_set import (
    is_tabular_response,
    parse_result_set_by_name,
    parse_single_result_set,
)


class OverallRebounding(PandasMixin, PolarsMixin, BaseModel):
    """Overall rebounding statistics for a player.

    Contains total rebounding stats including contested/uncontested breakdown.
    """

    player_id: int = Field(alias="PLAYER_ID")
    player_name_last_first: str = Field(alias="PLAYER_NAME_LAST_FIRST")
    games: int = Field(alias="G")
    overall: str = Field(alias="OVERALL")
    reb_frequency: float = Field(alias="REB_FREQUENCY")
    oreb: float = Field(alias="OREB")
    dreb: float = Field(alias="DREB")
    reb: float = Field(alias="REB")
    c_oreb: float = Field(alias="C_OREB")
    c_dreb: float = Field(alias="C_DREB")
    c_reb: float = Field(alias="C_REB")
    c_reb_pct: float = Field(alias="C_REB_PCT")
    uc_oreb: float = Field(alias="UC_OREB")
    uc_dreb: float = Field(alias="UC_DREB")
    uc_reb: float = Field(alias="UC_REB")
    uc_reb_pct: float = Field(alias="UC_REB_PCT")


class ShotTypeRebounding(PandasMixin, PolarsMixin, BaseModel):
    """Rebounding statistics by shot type (2FG miss vs 3FG miss)."""

    player_id: int = Field(alias="PLAYER_ID")
    player_name_last_first: str = Field(alias="PLAYER_NAME_LAST_FIRST")
    sort_order: int | None = Field(alias="SORT_ORDER")
    games: int = Field(alias="G")
    shot_type_range: str = Field(alias="SHOT_TYPE_RANGE")
    reb_frequency: float = Field(alias="REB_FREQUENCY")
    oreb: float = Field(alias="OREB")
    dreb: float = Field(alias="DREB")
    reb: float = Field(alias="REB")
    c_oreb: float = Field(alias="C_OREB")
    c_dreb: float = Field(alias="C_DREB")
    c_reb: float = Field(alias="C_REB")
    c_reb_pct: float = Field(alias="C_REB_PCT")
    uc_oreb: float = Field(alias="UC_OREB")
    uc_dreb: float = Field(alias="UC_DREB")
    uc_reb: float = Field(alias="UC_REB")
    uc_reb_pct: float = Field(alias="UC_REB_PCT")


class NumContestedRebounding(PandasMixin, PolarsMixin, BaseModel):
    """Rebounding statistics by number of players contesting."""

    player_id: int = Field(alias="PLAYER_ID")
    player_name_last_first: str = Field(alias="PLAYER_NAME_LAST_FIRST")
    sort_order: int | None = Field(alias="SORT_ORDER")
    games: int = Field(alias="G")
    reb_num_contesting_range: str = Field(alias="REB_NUM_CONTESTING_RANGE")
    reb_frequency: float = Field(alias="REB_FREQUENCY")
    oreb: float = Field(alias="OREB")
    dreb: float = Field(alias="DREB")
    reb: float = Field(alias="REB")
    c_oreb: float = Field(alias="C_OREB")
    c_dreb: float = Field(alias="C_DREB")
    c_reb: float = Field(alias="C_REB")
    c_reb_pct: float = Field(alias="C_REB_PCT")
    uc_oreb: float = Field(alias="UC_OREB")
    uc_dreb: float = Field(alias="UC_DREB")
    uc_reb: float = Field(alias="UC_REB")
    uc_reb_pct: float = Field(alias="UC_REB_PCT")


class ShotDistanceRebounding(PandasMixin, PolarsMixin, BaseModel):
    """Rebounding statistics by shot distance."""

    player_id: int = Field(alias="PLAYER_ID")
    player_name_last_first: str = Field(alias="PLAYER_NAME_LAST_FIRST")
    sort_order: int | None = Field(alias="SORT_ORDER")
    games: int = Field(alias="G")
    shot_dist_range: str = Field(alias="SHOT_DIST_RANGE")
    reb_frequency: float = Field(alias="REB_FREQUENCY")
    oreb: float = Field(alias="OREB")
    dreb: float = Field(alias="DREB")
    reb: float = Field(alias="REB")
    c_oreb: float = Field(alias="C_OREB")
    c_dreb: float = Field(alias="C_DREB")
    c_reb: float = Field(alias="C_REB")
    c_reb_pct: float = Field(alias="C_REB_PCT")
    uc_oreb: float = Field(alias="UC_OREB")
    uc_dreb: float = Field(alias="UC_DREB")
    uc_reb: float = Field(alias="UC_REB")
    uc_reb_pct: float = Field(alias="UC_REB_PCT")


class RebDistanceRebounding(PandasMixin, PolarsMixin, BaseModel):
    """Rebounding statistics by rebound distance from basket."""

    player_id: int = Field(alias="PLAYER_ID")
    player_name_last_first: str = Field(alias="PLAYER_NAME_LAST_FIRST")
    sort_order: int | None = Field(alias="SORT_ORDER")
    games: int = Field(alias="G")
    reb_dist_range: str | None = Field(alias="REB_DIST_RANGE")
    reb_frequency: float = Field(alias="REB_FREQUENCY")
    oreb: float = Field(alias="OREB")
    dreb: float = Field(alias="DREB")
    reb: float = Field(alias="REB")
    c_oreb: float = Field(alias="C_OREB")
    c_dreb: float = Field(alias="C_DREB")
    c_reb: float = Field(alias="C_REB")
    c_reb_pct: float = Field(alias="C_REB_PCT")
    uc_oreb: float = Field(alias="UC_OREB")
    uc_dreb: float = Field(alias="UC_DREB")
    uc_reb: float = Field(alias="UC_REB")
    uc_reb_pct: float = Field(alias="UC_REB_PCT")


class PlayerDashPtRebResponse(FrozenResponse):
    """Response from the player dashboard rebounding endpoint.

    Contains rebounding statistics broken down by:
    - overall: Overall rebounding totals
    - by_shot_type: Breakdown by 2FG vs 3FG misses
    - by_num_contested: Breakdown by number of players contesting
    - by_shot_distance: Breakdown by shot distance
    - by_reb_distance: Breakdown by rebound distance from basket
    """

    overall: OverallRebounding | None = None
    by_shot_type: list[ShotTypeRebounding] = Field(default_factory=list)
    by_num_contested: list[NumContestedRebounding] = Field(default_factory=list)
    by_shot_distance: list[ShotDistanceRebounding] = Field(default_factory=list)
    by_reb_distance: list[RebDistanceRebounding] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def from_result_sets(cls, data: object) -> dict[str, Any]:
        """Transform NBA's tabular resultSets format into structured data."""
        if not is_tabular_response(data):
            return data  # type: ignore[return-value]

        d = data
        return {
            "overall": parse_single_result_set(d, "OverallRebounding"),
            "by_shot_type": parse_result_set_by_name(d, "ShotTypeRebounding"),
            "by_num_contested": parse_result_set_by_name(d, "NumContestedRebounding"),
            "by_shot_distance": parse_result_set_by_name(d, "ShotDistanceRebounding"),
            "by_reb_distance": parse_result_set_by_name(d, "RebDistanceRebounding"),
        }
