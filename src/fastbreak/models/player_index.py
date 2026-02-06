"""Models for the Player Index endpoint response."""

from typing import Any

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.response import FrozenResponse
from fastbreak.models.common.result_set import (
    is_tabular_response,
    parse_result_set_by_name,
)


class PlayerIndexEntry(PandasMixin, PolarsMixin, BaseModel):
    """A player entry in the player index.

    Contains biographical, team, and draft information for a player.
    """

    # Player info
    person_id: int = Field(alias="PERSON_ID")
    player_last_name: str = Field(alias="PLAYER_LAST_NAME")
    player_first_name: str = Field(alias="PLAYER_FIRST_NAME")
    player_slug: str = Field(alias="PLAYER_SLUG")

    # Team info
    team_id: int | None = Field(alias="TEAM_ID")
    team_slug: str | None = Field(alias="TEAM_SLUG")
    is_defunct: int | None = Field(alias="IS_DEFUNCT")
    team_city: str | None = Field(alias="TEAM_CITY")
    team_name: str | None = Field(alias="TEAM_NAME")
    team_abbreviation: str | None = Field(alias="TEAM_ABBREVIATION")

    # Physical and biographical
    jersey_number: str | None = Field(alias="JERSEY_NUMBER")
    position: str | None = Field(alias="POSITION")
    height: str | None = Field(alias="HEIGHT")
    weight: str | None = Field(alias="WEIGHT")
    college: str | None = Field(alias="COLLEGE")
    country: str | None = Field(alias="COUNTRY")

    # Draft info
    draft_year: int | None = Field(alias="DRAFT_YEAR")
    draft_round: int | None = Field(alias="DRAFT_ROUND")
    draft_number: int | None = Field(alias="DRAFT_NUMBER")

    # Status and years
    roster_status: float | None = Field(alias="ROSTER_STATUS")
    from_year: str | None = Field(alias="FROM_YEAR")
    to_year: str | None = Field(alias="TO_YEAR")

    # Stats
    pts: float | None = Field(alias="PTS")
    reb: float | None = Field(alias="REB")
    ast: float | None = Field(alias="AST")
    stats_timeframe: str | None = Field(alias="STATS_TIMEFRAME")


class PlayerIndexResponse(FrozenResponse):
    """Response from the player index endpoint.

    Contains a list of all players for the specified season.
    """

    players: list[PlayerIndexEntry] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def from_result_sets(cls, data: object) -> dict[str, Any]:
        """Transform NBA's tabular resultSets format into structured data."""
        if not is_tabular_response(data):
            return data  # type: ignore[return-value]

        return {
            "players": parse_result_set_by_name(data, "PlayerIndex"),
        }
