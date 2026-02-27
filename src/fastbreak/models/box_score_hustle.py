"""Models for the box score hustle v2 endpoint."""

from typing import Self

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.meta import Meta
from fastbreak.models.common.response import FrozenResponse


class HustleStatistics(BaseModel):
    """Hustle statistics for a player or team."""

    minutes: str
    points: int = Field(ge=0)
    contested_shots: int = Field(ge=0, alias="contestedShots")
    contested_shots_2pt: int = Field(ge=0, alias="contestedShots2pt")
    contested_shots_3pt: int = Field(ge=0, alias="contestedShots3pt")
    deflections: int = Field(ge=0)
    charges_drawn: int = Field(ge=0, alias="chargesDrawn")
    screen_assists: int = Field(ge=0, alias="screenAssists")
    screen_assist_points: int = Field(ge=0, alias="screenAssistPoints")
    loose_balls_recovered_offensive: int = Field(
        ge=0, alias="looseBallsRecoveredOffensive"
    )
    loose_balls_recovered_defensive: int = Field(
        ge=0, alias="looseBallsRecoveredDefensive"
    )
    loose_balls_recovered_total: int = Field(ge=0, alias="looseBallsRecoveredTotal")
    offensive_box_outs: int = Field(ge=0, alias="offensiveBoxOuts")
    defensive_box_outs: int = Field(ge=0, alias="defensiveBoxOuts")
    box_out_player_team_rebounds: int = Field(ge=0, alias="boxOutPlayerTeamRebounds")
    box_out_player_rebounds: int = Field(ge=0, alias="boxOutPlayerRebounds")
    box_outs: int = Field(ge=0, alias="boxOuts")

    @model_validator(mode="after")
    def check_partitions(self) -> Self:
        """Validate that 2pt + 3pt contested shots and loose balls sum correctly."""
        if self.contested_shots_2pt + self.contested_shots_3pt != self.contested_shots:
            msg = (
                f"contested_shots_2pt ({self.contested_shots_2pt}) + "
                f"contested_shots_3pt ({self.contested_shots_3pt}) != "
                f"contested_shots ({self.contested_shots})"
            )
            raise ValueError(msg)
        if (
            self.loose_balls_recovered_offensive + self.loose_balls_recovered_defensive
            != self.loose_balls_recovered_total
        ):
            msg = (
                f"loose_balls_recovered_offensive ({self.loose_balls_recovered_offensive}) + "
                f"loose_balls_recovered_defensive ({self.loose_balls_recovered_defensive}) != "
                f"loose_balls_recovered_total ({self.loose_balls_recovered_total})"
            )
            raise ValueError(msg)
        return self


class HustlePlayer(PandasMixin, PolarsMixin, BaseModel):
    """Player with hustle statistics from a box score."""

    person_id: int = Field(alias="personId")
    first_name: str = Field(alias="firstName")
    family_name: str = Field(alias="familyName")
    name_i: str = Field(alias="nameI")
    player_slug: str = Field(alias="playerSlug")
    position: str
    comment: str
    jersey_num: str = Field(alias="jerseyNum")
    statistics: HustleStatistics


class HustleTeam(PandasMixin, PolarsMixin, BaseModel):
    """Team with hustle statistics from a box score.

    Note: Some fields are optional because the NBA API returns null values
    for certain games where this data was not tracked or is not yet available.
    """

    team_id: int = Field(alias="teamId")
    team_city: str | None = Field(None, alias="teamCity")
    team_name: str | None = Field(None, alias="teamName")
    team_tricode: str | None = Field(None, alias="teamTricode")
    team_slug: str | None = Field(None, alias="teamSlug")
    players: list[HustlePlayer]
    statistics: HustleStatistics


class BoxScoreHustleData(BaseModel):
    """Box score hustle data containing both teams."""

    game_id: str = Field(alias="gameId")
    away_team_id: int = Field(alias="awayTeamId")
    home_team_id: int = Field(alias="homeTeamId")
    home_team: HustleTeam = Field(alias="homeTeam")
    away_team: HustleTeam = Field(alias="awayTeam")


class BoxScoreHustleResponse(FrozenResponse):
    """Response from the box score hustle v2 endpoint.

    Contains hustle statistics for all players and both teams in a game,
    organized by home and away team with nested player data.

    The v2 format uses modern nested JSON rather than the traditional
    result sets format, providing additional player metadata like
    first/last names and player slugs.
    """

    meta: Meta
    box_score_hustle: BoxScoreHustleData = Field(alias="boxScoreHustle")
