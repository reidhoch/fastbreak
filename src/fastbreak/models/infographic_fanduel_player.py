"""Models for the infographic FanDuel player endpoint."""

from typing import Any

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.result_set import (
    is_tabular_response,
    parse_result_set_by_name,
)


class FanDuelPlayer(PandasMixin, PolarsMixin, BaseModel):
    """FanDuel fantasy player statistics from a game."""

    player_id: int = Field(alias="PLAYER_ID")
    player_name: str = Field(alias="PLAYER_NAME")
    team_id: int = Field(alias="TEAM_ID")
    team_name: str = Field(alias="TEAM_NAME")
    team_abbreviation: str = Field(alias="TEAM_ABBREVIATION")
    jersey_num: str = Field(alias="JERSEY_NUM")
    player_position: str = Field(alias="PLAYER_POSITION")
    location: str = Field(alias="LOCATION")
    fan_duel_pts: float = Field(alias="FAN_DUEL_PTS")
    nba_fantasy_pts: float = Field(alias="NBA_FANTASY_PTS")
    usg_pct: float = Field(alias="USG_PCT")
    min: float = Field(alias="MIN")
    fgm: int = Field(alias="FGM")
    fga: int = Field(alias="FGA")
    fg_pct: float = Field(alias="FG_PCT")
    fg3m: int = Field(alias="FG3M")
    fg3a: int = Field(alias="FG3A")
    fg3_pct: float = Field(alias="FG3_PCT")
    ftm: int = Field(alias="FTM")
    fta: int = Field(alias="FTA")
    ft_pct: float = Field(alias="FT_PCT")
    oreb: int = Field(alias="OREB")
    dreb: int = Field(alias="DREB")
    reb: int = Field(alias="REB")
    ast: int = Field(alias="AST")
    tov: int = Field(alias="TOV")
    stl: int = Field(alias="STL")
    blk: int = Field(alias="BLK")
    blka: int = Field(alias="BLKA")
    pf: int = Field(alias="PF")
    pfd: int = Field(alias="PFD")
    pts: int = Field(alias="PTS")
    plus_minus: int = Field(alias="PLUS_MINUS")


class InfographicFanDuelPlayerResponse(BaseModel):
    """Response from the infographic FanDuel player endpoint.

    Contains fantasy scoring and box score stats for all players in a game.
    """

    players: list[FanDuelPlayer] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def from_result_sets(cls, data: object) -> dict[str, Any]:
        """Transform NBA's tabular resultSets format into structured data."""
        if not is_tabular_response(data):
            return data  # type: ignore[return-value]

        return {
            "players": parse_result_set_by_name(
                data,
                "FanDuelPlayer",
            ),
        }
