"""Models for the common all players endpoint."""

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.result_set import tabular_validator


class CommonPlayer(PandasMixin, PolarsMixin, BaseModel):
    """A player entry from the CommonAllPlayers endpoint."""

    person_id: int = Field(alias="PERSON_ID")
    display_last_comma_first: str = Field(alias="DISPLAY_LAST_COMMA_FIRST")
    display_first_last: str = Field(alias="DISPLAY_FIRST_LAST")
    roster_status: int = Field(alias="ROSTERSTATUS")
    from_year: str = Field(alias="FROM_YEAR")
    to_year: str = Field(alias="TO_YEAR")
    player_code: str = Field(alias="PLAYERCODE")
    player_slug: str = Field(alias="PLAYER_SLUG")
    team_id: int = Field(alias="TEAM_ID")
    team_city: str = Field(alias="TEAM_CITY")
    team_name: str = Field(alias="TEAM_NAME")
    team_abbreviation: str = Field(alias="TEAM_ABBREVIATION")
    team_slug: str | None = Field(alias="TEAM_SLUG")
    team_code: str = Field(alias="TEAM_CODE")
    games_played_flag: str = Field(alias="GAMES_PLAYED_FLAG")
    other_league_experience: str = Field(alias="OTHERLEAGUE_EXPERIENCE_CH")


class CommonAllPlayersResponse(BaseModel):
    """Response from the common all players endpoint."""

    players: list[CommonPlayer] = Field(default_factory=list)

    from_result_sets = model_validator(mode="before")(tabular_validator("players"))
