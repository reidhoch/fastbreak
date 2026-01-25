"""Models for the draft history endpoint."""

from typing import Any

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.result_set import is_tabular_response, parse_result_set


class DraftPick(PandasMixin, PolarsMixin, BaseModel):
    """A single draft pick entry."""

    person_id: int = Field(alias="PERSON_ID")
    player_name: str = Field(alias="PLAYER_NAME")
    season: str = Field(alias="SEASON")
    round_number: int = Field(alias="ROUND_NUMBER")
    round_pick: int = Field(alias="ROUND_PICK")
    overall_pick: int = Field(alias="OVERALL_PICK")
    draft_type: str = Field(alias="DRAFT_TYPE")
    team_id: int | None = Field(alias="TEAM_ID")
    team_city: str | None = Field(alias="TEAM_CITY")
    team_name: str | None = Field(alias="TEAM_NAME")
    team_abbreviation: str | None = Field(alias="TEAM_ABBREVIATION")
    organization: str = Field(alias="ORGANIZATION")
    organization_type: str = Field(alias="ORGANIZATION_TYPE")
    player_profile_flag: int = Field(alias="PLAYER_PROFILE_FLAG")


class DraftHistoryResponse(BaseModel):
    """Response from the draft history endpoint."""

    picks: list[DraftPick] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def from_result_sets(cls, data: object) -> dict[str, Any]:
        """Transform NBA's tabular resultSets format into structured data."""
        if not is_tabular_response(data):
            return data  # type: ignore[return-value]

        rows = parse_result_set(data)

        return {"picks": rows}
