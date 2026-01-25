"""Models for the Player Dashboard Passing endpoint response."""

from typing import Any

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.result_set import (
    is_tabular_response,
    parse_result_set_by_name,
)


class PassMade(BaseModel):
    """Statistics for passes made by a player to a teammate.

    Contains passing and shooting efficiency data for passes to a specific teammate.
    """

    player_id: int = Field(alias="PLAYER_ID")
    player_name_last_first: str = Field(alias="PLAYER_NAME_LAST_FIRST")
    team_name: str = Field(alias="TEAM_NAME")
    team_id: int = Field(alias="TEAM_ID")
    team_abbreviation: str = Field(alias="TEAM_ABBREVIATION")
    pass_type: str = Field(alias="PASS_TYPE")
    games: int = Field(alias="G")
    pass_to: str = Field(alias="PASS_TO")
    pass_teammate_player_id: int = Field(alias="PASS_TEAMMATE_PLAYER_ID")
    frequency: float = Field(alias="FREQUENCY")
    passes: float = Field(alias="PASS")
    ast: float = Field(alias="AST")
    fgm: float = Field(alias="FGM")
    fga: float = Field(alias="FGA")
    fg_pct: float | None = Field(alias="FG_PCT")
    fg2m: float = Field(alias="FG2M")
    fg2a: float = Field(alias="FG2A")
    fg2_pct: float | None = Field(alias="FG2_PCT")
    fg3m: float = Field(alias="FG3M")
    fg3a: float = Field(alias="FG3A")
    fg3_pct: float | None = Field(alias="FG3_PCT")


class PassReceived(BaseModel):
    """Statistics for passes received by a player from a teammate.

    Contains passing and shooting efficiency data for passes from a specific teammate.
    """

    player_id: int = Field(alias="PLAYER_ID")
    player_name_last_first: str = Field(alias="PLAYER_NAME_LAST_FIRST")
    team_name: str = Field(alias="TEAM_NAME")
    team_id: int = Field(alias="TEAM_ID")
    team_abbreviation: str = Field(alias="TEAM_ABBREVIATION")
    pass_type: str = Field(alias="PASS_TYPE")
    games: int = Field(alias="G")
    pass_from: str = Field(alias="PASS_FROM")
    pass_teammate_player_id: int = Field(alias="PASS_TEAMMATE_PLAYER_ID")
    frequency: float = Field(alias="FREQUENCY")
    passes: float = Field(alias="PASS")
    ast: float = Field(alias="AST")
    fgm: float = Field(alias="FGM")
    fga: float = Field(alias="FGA")
    fg_pct: float | None = Field(alias="FG_PCT")
    fg2m: float = Field(alias="FG2M")
    fg2a: float = Field(alias="FG2A")
    fg2_pct: float | None = Field(alias="FG2_PCT")
    fg3m: float = Field(alias="FG3M")
    fg3a: float = Field(alias="FG3A")
    fg3_pct: float | None = Field(alias="FG3_PCT")


class PlayerDashPtPassResponse(BaseModel):
    """Response from the player dashboard passing endpoint.

    Contains pass statistics for:
    - passes_made: Passes the player made to teammates
    - passes_received: Passes the player received from teammates
    """

    passes_made: list[PassMade] = Field(default_factory=list)
    passes_received: list[PassReceived] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def from_result_sets(cls, data: object) -> dict[str, Any]:
        """Transform NBA's tabular resultSets format into structured data."""
        if not is_tabular_response(data):
            return data  # type: ignore[return-value]

        return {
            "passes_made": parse_result_set_by_name(
                data,
                "PassesMade",
            ),
            "passes_received": parse_result_set_by_name(
                data,
                "PassesReceived",
            ),
        }
