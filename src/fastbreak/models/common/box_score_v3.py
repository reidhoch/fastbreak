"""Shared base models for V3 box score endpoints."""

from pydantic import BaseModel, Field

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin


class BoxScorePlayerV3Base(PandasMixin, PolarsMixin, BaseModel):
    """Base player info for V3 box scores (without statistics)."""

    person_id: int = Field(alias="personId")
    first_name: str = Field(alias="firstName")
    family_name: str = Field(alias="familyName")
    name_i: str = Field(alias="nameI")
    player_slug: str = Field(alias="playerSlug")
    position: str
    comment: str
    jersey_num: str = Field(alias="jerseyNum")


class BoxScorePlayerV3[T: BaseModel](BoxScorePlayerV3Base):
    """Player with typed statistics for V3 box scores."""

    statistics: T


class BoxScoreTeamV3Base(PandasMixin, PolarsMixin, BaseModel):
    """Base team info for V3 box scores (without players/statistics)."""

    team_id: int = Field(alias="teamId")
    team_city: str = Field(alias="teamCity")
    team_name: str = Field(alias="teamName")
    team_tricode: str = Field(alias="teamTricode")
    team_slug: str = Field(alias="teamSlug")


class BoxScoreTeamV3[T: BaseModel](BoxScoreTeamV3Base):
    """Team with typed player list for V3 box scores."""

    players: list[BoxScorePlayerV3[T]]
    statistics: T


class BoxScoreDataV3Base(BaseModel):
    """Base structure for V3 box score data."""

    game_id: str = Field(alias="gameId")
    away_team_id: int = Field(alias="awayTeamId")
    home_team_id: int = Field(alias="homeTeamId")
