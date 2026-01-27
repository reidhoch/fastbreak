"""Response models for the playerawards endpoint."""

from typing import Any

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.result_set import is_tabular_response, parse_result_set


class PlayerAward(PandasMixin, PolarsMixin, BaseModel):
    """A player award entry."""

    person_id: int = Field(alias="PERSON_ID")
    first_name: str = Field(alias="FIRST_NAME")
    last_name: str = Field(alias="LAST_NAME")
    team: str | None = Field(alias="TEAM")
    description: str = Field(alias="DESCRIPTION")
    all_nba_team_number: str | None = Field(alias="ALL_NBA_TEAM_NUMBER")
    season: str = Field(alias="SEASON")
    month: str | None = Field(alias="MONTH")
    week: str | None = Field(alias="WEEK")
    conference: str | None = Field(alias="CONFERENCE")
    type: str = Field(alias="TYPE")
    subtype1: str | None = Field(alias="SUBTYPE1")
    subtype2: str | None = Field(alias="SUBTYPE2")
    subtype3: str | None = Field(alias="SUBTYPE3")


class PlayerAwardsResponse(BaseModel):
    """Response from the playerawards endpoint.

    Contains all awards for a specific player.
    """

    awards: list[PlayerAward] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def from_result_sets(cls, data: object) -> dict[str, Any]:
        """Transform NBA's tabular resultSets format into structured data."""
        if not is_tabular_response(data):
            return data  # type: ignore[return-value]

        rows = parse_result_set(data)

        return {"awards": rows}
