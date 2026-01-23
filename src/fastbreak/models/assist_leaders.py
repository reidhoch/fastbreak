"""Models for the assist leaders endpoint."""

from typing import Any

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.result_set import is_tabular_response, parse_result_set


class TeamAssistLeader(BaseModel):
    """A team's assist leader entry (PlayerOrTeam=Team)."""

    rank: int = Field(alias="RANK")
    team_id: int = Field(alias="TEAM_ID")
    team_abbreviation: str = Field(alias="TEAM_ABBREVIATION")
    team_name: str = Field(alias="TEAM_NAME")
    ast: float = Field(alias="AST")


class PlayerAssistLeader(BaseModel):
    """A player's assist leader entry (PlayerOrTeam=Player)."""

    rank: int = Field(alias="RANK")
    player_id: int = Field(alias="PLAYER_ID")
    player: str = Field(alias="PLAYER")
    team_id: int = Field(alias="TEAM_ID")
    team_abbreviation: str = Field(alias="TEAM_ABBREVIATION")
    team_name: str = Field(alias="TEAM_NAME")
    jersey_num: str = Field(alias="JERSEY_NUM")
    player_position: str = Field(alias="PLAYER_POSITION")
    ast: float = Field(alias="AST")


class AssistLeadersResponse(BaseModel):
    """Response from the assist leaders endpoint.

    Contains either team_leaders or player_leaders depending on the
    PlayerOrTeam parameter used in the request.
    """

    team_leaders: list[TeamAssistLeader] = Field(default_factory=list)
    player_leaders: list[PlayerAssistLeader] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def from_result_sets(cls, data: object) -> dict[str, Any]:
        """Transform NBA's tabular resultSets format into structured data."""
        if not is_tabular_response(data):
            return data  # type: ignore[return-value]

        rows = parse_result_set(data)

        if not rows:
            return {"team_leaders": [], "player_leaders": []}

        # Check if this is player or team data by looking for PLAYER_ID
        if "PLAYER_ID" in rows[0]:
            return {"player_leaders": rows}
        return {"team_leaders": rows}
