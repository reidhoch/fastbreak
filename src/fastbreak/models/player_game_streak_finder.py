"""Models for the Player Game Streak Finder endpoint response."""

from typing import Any

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.result_set import (
    is_tabular_response,
    parse_result_set_by_name,
)


class PlayerGameStreak(BaseModel):
    """A player's consecutive game streak information.

    Contains details about the longest or current game streak.
    """

    player_name: str = Field(alias="PLAYER_NAME_LAST_FIRST")
    player_id: int = Field(alias="PLAYER_ID")
    game_streak: int = Field(alias="GAMESTREAK")
    start_date: str = Field(alias="STARTDATE")
    end_date: str = Field(alias="ENDDATE")
    active_streak: int = Field(alias="ACTIVESTREAK")
    num_seasons: int = Field(alias="NUMSEASONS")
    last_season: str = Field(alias="LASTSEASON")
    first_season: str = Field(alias="FIRSTSEASON")


class PlayerGameStreakFinderResponse(BaseModel):
    """Response from the player game streak finder endpoint.

    Contains game streak information for a player.
    """

    streaks: list[PlayerGameStreak] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def from_result_sets(cls, data: object) -> dict[str, Any]:
        """Transform NBA's tabular resultSets format into structured data."""
        if not is_tabular_response(data):
            return data  # type: ignore[return-value]

        return {
            "streaks": parse_result_set_by_name(
                data,
                "PlayerGameStreakFinderResults",
            ),
        }
