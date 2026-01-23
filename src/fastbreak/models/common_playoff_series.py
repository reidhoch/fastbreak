"""Models for the common playoff series endpoint."""

from typing import Any

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.result_set import is_tabular_response, parse_result_set


class PlayoffSeriesGame(BaseModel):
    """A single game in a playoff series."""

    game_id: str = Field(alias="GAME_ID")
    home_team_id: int = Field(alias="HOME_TEAM_ID")
    visitor_team_id: int = Field(alias="VISITOR_TEAM_ID")
    series_id: str = Field(alias="SERIES_ID")
    game_num: int = Field(alias="GAME_NUM")


class CommonPlayoffSeriesResponse(BaseModel):
    """Response from the common playoff series endpoint."""

    games: list[PlayoffSeriesGame] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def from_result_sets(cls, data: object) -> dict[str, Any]:
        """Transform NBA's tabular resultSets format into structured data."""
        if not is_tabular_response(data):
            return data  # type: ignore[return-value]

        return {"games": parse_result_set(data)}
