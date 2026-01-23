"""Models for common team roster response."""

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.result_set import named_result_sets_validator


class RosterPlayer(BaseModel):
    """A player on a team roster."""

    team_id: int = Field(alias="TeamID")
    season: str = Field(alias="SEASON")
    league_id: str = Field(alias="LeagueID")
    player: str = Field(alias="PLAYER")
    nickname: str = Field(alias="NICKNAME")
    player_slug: str = Field(alias="PLAYER_SLUG")
    num: str = Field(alias="NUM")
    position: str = Field(alias="POSITION")
    height: str = Field(alias="HEIGHT")
    weight: str = Field(alias="WEIGHT")
    birth_date: str = Field(alias="BIRTH_DATE")
    age: float = Field(alias="AGE")
    exp: str = Field(alias="EXP")
    school: str = Field(alias="SCHOOL")
    player_id: int = Field(alias="PLAYER_ID")
    how_acquired: str | None = Field(alias="HOW_ACQUIRED")


class Coach(BaseModel):
    """A coach on a team."""

    team_id: int = Field(alias="TEAM_ID")
    season: str = Field(alias="SEASON")
    coach_id: int = Field(alias="COACH_ID")
    first_name: str = Field(alias="FIRST_NAME")
    last_name: str = Field(alias="LAST_NAME")
    coach_name: str = Field(alias="COACH_NAME")
    is_assistant: int = Field(alias="IS_ASSISTANT")
    coach_type: str = Field(alias="COACH_TYPE")
    sort_sequence: int | None = Field(alias="SORT_SEQUENCE")
    sub_sort_sequence: int = Field(alias="SUB_SORT_SEQUENCE")


class CommonTeamRosterResponse(BaseModel):
    """Response from the commonteamroster endpoint."""

    players: list[RosterPlayer] = Field(default_factory=list)
    coaches: list[Coach] = Field(default_factory=list)

    from_result_sets = model_validator(mode="before")(
        named_result_sets_validator(
            {
                "players": "CommonTeamRoster",
                "coaches": "Coaches",
            }
        )
    )
