"""Models for the team and players vs players endpoint."""

from typing import Any

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.result_set import (
    is_tabular_response,
    parse_result_set_by_name,
)


class VsPlayersStats(PandasMixin, PolarsMixin, BaseModel):
    """Base stats for player/team comparison with descriptions."""

    group_set: str = Field(alias="GROUP_SET")
    title_description: str = Field(alias="TITLE_DESCRIPTION")
    description: str = Field(alias="DESCRIPTION")
    min: float = Field(alias="MIN")
    fgm: float = Field(alias="FGM")
    fga: float = Field(alias="FGA")
    fg_pct: float | None = Field(alias="FG_PCT")
    fg3m: float = Field(alias="FG3M")
    fg3a: float = Field(alias="FG3A")
    fg3_pct: float | None = Field(alias="FG3_PCT")
    ftm: float = Field(alias="FTM")
    fta: float = Field(alias="FTA")
    ft_pct: float | None = Field(alias="FT_PCT")
    oreb: float = Field(alias="OREB")
    dreb: float = Field(alias="DREB")
    reb: float = Field(alias="REB")
    ast: float = Field(alias="AST")
    tov: float = Field(alias="TOV")
    stl: float = Field(alias="STL")
    blk: float = Field(alias="BLK")
    blka: float = Field(alias="BLKA")
    pf: float = Field(alias="PF")
    pfd: float = Field(alias="PFD")
    pts: float = Field(alias="PTS")
    plus_minus: float = Field(alias="PLUS_MINUS")


class PlayerVsPlayersStats(PandasMixin, PolarsMixin, BaseModel):
    """Player stats for on/off court comparison."""

    group_set: str = Field(alias="GROUP_SET")
    title_description: str = Field(alias="TITLE_DESCRIPTION")
    player_id: int = Field(alias="PLAYER_ID")
    player_name: str = Field(alias="PLAYER_NAME")
    min: float = Field(alias="MIN")
    fgm: float = Field(alias="FGM")
    fga: float = Field(alias="FGA")
    fg_pct: float | None = Field(alias="FG_PCT")
    fg3m: float = Field(alias="FG3M")
    fg3a: float = Field(alias="FG3A")
    fg3_pct: float | None = Field(alias="FG3_PCT")
    ftm: float = Field(alias="FTM")
    fta: float = Field(alias="FTA")
    ft_pct: float | None = Field(alias="FT_PCT")
    oreb: float = Field(alias="OREB")
    dreb: float = Field(alias="DREB")
    reb: float = Field(alias="REB")
    ast: float = Field(alias="AST")
    tov: float = Field(alias="TOV")
    stl: float = Field(alias="STL")
    blk: float = Field(alias="BLK")
    blka: float = Field(alias="BLKA")
    pf: float = Field(alias="PF")
    pfd: float = Field(alias="PFD")
    pts: float = Field(alias="PTS")
    plus_minus: float = Field(alias="PLUS_MINUS")


class TeamAndPlayersVsPlayersResponse(BaseModel):
    """Response from the team and players vs players endpoint.

    Contains comparison stats between two teams and their players.
    """

    players_vs_players: list[VsPlayersStats] = Field(default_factory=list)
    team_players_vs_players_off: list[PlayerVsPlayersStats] = Field(
        default_factory=list
    )
    team_players_vs_players_on: list[PlayerVsPlayersStats] = Field(default_factory=list)
    team_vs_players: list[VsPlayersStats] = Field(default_factory=list)
    team_vs_players_off: list[VsPlayersStats] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def from_result_sets(cls, data: object) -> dict[str, Any]:
        """Transform NBA's tabular resultSets format into structured data."""
        if not is_tabular_response(data):
            return data  # type: ignore[return-value]

        return {
            "players_vs_players": parse_result_set_by_name(
                data,
                "PlayersVsPlayers",
            ),
            "team_players_vs_players_off": parse_result_set_by_name(
                data,
                "TeamPlayersVsPlayersOff",
            ),
            "team_players_vs_players_on": parse_result_set_by_name(
                data,
                "TeamPlayersVsPlayersOn",
            ),
            "team_vs_players": parse_result_set_by_name(
                data,
                "TeamVsPlayers",
            ),
            "team_vs_players_off": parse_result_set_by_name(
                data,
                "TeamVsPlayersOff",
            ),
        }
