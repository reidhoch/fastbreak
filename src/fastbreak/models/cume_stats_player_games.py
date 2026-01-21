"""Models for the cumestatsplayergames endpoint."""

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.result_set import named_result_sets_validator


class PlayerGame(BaseModel):
    """A game entry for a player."""

    matchup: str = Field(alias="MATCHUP")
    game_id: str = Field(alias="GAME_ID")


class CumeStatsPlayerGamesResponse(BaseModel):
    """Response from the cumestatsplayergames endpoint.

    Contains a list of games the player has participated in,
    with optional filtering by location, outcome, opponent, etc.
    """

    games: list[PlayerGame] = Field(default_factory=list[PlayerGame])

    from_result_sets = model_validator(mode="before")(
        named_result_sets_validator({"games": ("CumeStatsPlayerGames", False)})
    )
