"""Models for the game rotation endpoint."""

from typing import Any

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.result_set import is_tabular_response, parse_result_set_by_name


class RotationEntry(BaseModel):
    """A single rotation entry (player stint)."""

    game_id: str = Field(alias="GAME_ID")
    team_id: int = Field(alias="TEAM_ID")
    team_city: str = Field(alias="TEAM_CITY")
    team_name: str = Field(alias="TEAM_NAME")
    person_id: int = Field(alias="PERSON_ID")
    player_first: str = Field(alias="PLAYER_FIRST")
    player_last: str = Field(alias="PLAYER_LAST")
    in_time_real: float = Field(alias="IN_TIME_REAL")
    out_time_real: float = Field(alias="OUT_TIME_REAL")
    player_pts: int = Field(alias="PLAYER_PTS")
    pt_diff: float = Field(alias="PT_DIFF")
    usg_pct: float = Field(alias="USG_PCT")


class GameRotationResponse(BaseModel):
    """Response from the game rotation endpoint."""

    away_team: list[RotationEntry] = Field(default_factory=list)
    home_team: list[RotationEntry] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def from_result_sets(cls, data: object) -> dict[str, Any]:
        """Transform NBA's tabular resultSets format into structured data."""
        if not is_tabular_response(data):
            return data  # type: ignore[return-value]

        return {
            "away_team": parse_result_set_by_name(data, "AwayTeam"),  # type: ignore[arg-type]
            "home_team": parse_result_set_by_name(data, "HomeTeam"),  # type: ignore[arg-type]
        }
