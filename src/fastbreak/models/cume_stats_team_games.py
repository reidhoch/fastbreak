"""Models for the cumestatsteamgames endpoint."""

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.result_set import named_result_sets_validator


class TeamGame(PandasMixin, PolarsMixin, BaseModel):
    """A game entry for a team."""

    matchup: str = Field(alias="MATCHUP")
    game_id: str = Field(alias="GAME_ID")


class CumeStatsTeamGamesResponse(BaseModel):
    """Response from the cumestatsteamgames endpoint.

    Contains a list of games the team has participated in,
    with optional filtering by location, outcome, opponent, etc.
    """

    games: list[TeamGame] = Field(default_factory=list)

    from_result_sets = model_validator(mode="before")(
        named_result_sets_validator({"games": "CumeStatsTeamGames"})
    )
