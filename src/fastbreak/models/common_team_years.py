"""Models for common team years response."""

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.result_set import tabular_validator


class TeamYear(BaseModel):
    """A team's years of existence in the league."""

    league_id: str = Field(alias="LEAGUE_ID")
    team_id: int = Field(alias="TEAM_ID")
    min_year: str = Field(alias="MIN_YEAR")
    max_year: str = Field(alias="MAX_YEAR")
    abbreviation: str | None = Field(alias="ABBREVIATION")


class CommonTeamYearsResponse(BaseModel):
    """Response from the commonteamyears endpoint."""

    teams: list[TeamYear] = Field(default_factory=list)

    from_result_sets = model_validator(mode="before")(tabular_validator("teams"))
