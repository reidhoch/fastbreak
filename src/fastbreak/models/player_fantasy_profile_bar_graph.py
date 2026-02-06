"""Models for the Player Fantasy Profile Bar Graph endpoint response."""

from typing import Any

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.response import FrozenResponse
from fastbreak.models.common.result_set import (
    is_tabular_response,
    parse_single_result_set,
)


class FantasyStats(PandasMixin, PolarsMixin, BaseModel):
    """Fantasy statistics for a player.

    Contains fantasy points for FanDuel and NBA Fantasy leagues,
    plus the underlying stats used in fantasy scoring.
    """

    player_id: int = Field(alias="PLAYER_ID")
    player_name: str = Field(alias="PLAYER_NAME")
    team_id: int = Field(alias="TEAM_ID")
    team_abbreviation: str = Field(alias="TEAM_ABBREVIATION")
    fan_duel_pts: float | None = Field(alias="FAN_DUEL_PTS")
    nba_fantasy_pts: float | None = Field(alias="NBA_FANTASY_PTS")
    pts: float = Field(alias="PTS")
    reb: float = Field(alias="REB")
    ast: float = Field(alias="AST")
    fg3m: float = Field(alias="FG3M")
    ft_pct: float | None = Field(alias="FT_PCT")
    stl: float = Field(alias="STL")
    blk: float = Field(alias="BLK")
    tov: float = Field(alias="TOV")
    fg_pct: float | None = Field(alias="FG_PCT")


class PlayerFantasyProfileBarGraphResponse(FrozenResponse):
    """Response from the player fantasy profile bar graph endpoint.

    Contains season averages and last 5 games averages for fantasy stats.
    """

    season_avg: FantasyStats | None = None
    last_five_games_avg: FantasyStats | None = None

    @model_validator(mode="before")
    @classmethod
    def from_result_sets(cls, data: object) -> dict[str, Any]:
        """Transform NBA's tabular resultSets format into structured data."""
        if not is_tabular_response(data):
            return data  # type: ignore[return-value]

        d = data
        return {
            "season_avg": parse_single_result_set(d, "SeasonAvg"),
            "last_five_games_avg": parse_single_result_set(d, "LastFiveGamesAvg"),
        }
