"""Models for the box score traditional v2 endpoint.

The v2 endpoint returns NBA's tabular result-set format (`PlayerStats`,
`TeamStats`, `TeamStarterBenchStats`) rather than the nested JSON used by
v3. The key field unique to v2 is ``START_POSITION`` — a non-empty string
("F"/"G"/"C") for starters and "" for bench players. The v3 ``position``
field is the league-registry position regardless of role and cannot be
used to identify starters.
"""

from typing import Annotated

from pydantic import BaseModel, BeforeValidator, Field, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.response import FrozenResponse
from fastbreak.models.common.result_set import named_result_sets_validator


def _empty_str_to_zero(v: object) -> object:
    """Coerce empty-string numeric fields to 0 (occurs in older / DNP rows)."""
    if v == "":
        return 0
    return v


_CoercedInt = Annotated[int, BeforeValidator(_empty_str_to_zero)]
_CoercedFloat = Annotated[float, BeforeValidator(_empty_str_to_zero)]
_CoercedMinutes = Annotated[str, BeforeValidator(str)]


class TraditionalPlayerV2(PandasMixin, PolarsMixin, BaseModel):
    """Player-level traditional statistics from a v2 box score.

    ``start_position`` is the v2-only field that distinguishes the five
    starters per team (non-empty: "F"/"G"/"C") from bench players ("").
    """

    game_id: str = Field(alias="GAME_ID")
    team_id: _CoercedInt = Field(alias="TEAM_ID")
    team_abbreviation: str = Field(alias="TEAM_ABBREVIATION")
    team_city: str = Field(alias="TEAM_CITY")
    player_id: _CoercedInt = Field(alias="PLAYER_ID")
    player_name: str = Field(alias="PLAYER_NAME")
    nickname: str | None = Field(default=None, alias="NICKNAME")
    start_position: str = Field(alias="START_POSITION")
    comment: str = Field(alias="COMMENT")
    minutes: _CoercedMinutes | None = Field(default=None, alias="MIN")
    fgm: _CoercedInt = Field(alias="FGM")
    fga: _CoercedInt = Field(alias="FGA")
    fg_pct: _CoercedFloat = Field(alias="FG_PCT")
    fg3m: _CoercedInt = Field(alias="FG3M")
    fg3a: _CoercedInt = Field(alias="FG3A")
    fg3_pct: _CoercedFloat = Field(alias="FG3_PCT")
    ftm: _CoercedInt = Field(alias="FTM")
    fta: _CoercedInt = Field(alias="FTA")
    ft_pct: _CoercedFloat = Field(alias="FT_PCT")
    oreb: _CoercedInt = Field(alias="OREB")
    dreb: _CoercedInt = Field(alias="DREB")
    reb: _CoercedInt = Field(alias="REB")
    ast: _CoercedInt = Field(alias="AST")
    stl: _CoercedInt = Field(alias="STL")
    blk: _CoercedInt = Field(alias="BLK")
    to: _CoercedInt = Field(alias="TO")
    pf: _CoercedInt = Field(alias="PF")
    pts: _CoercedInt = Field(alias="PTS")
    plus_minus: _CoercedFloat | None = Field(default=None, alias="PLUS_MINUS")


class TraditionalTeamV2(PandasMixin, PolarsMixin, BaseModel):
    """Team-level traditional statistics from a v2 box score."""

    game_id: str = Field(alias="GAME_ID")
    team_id: _CoercedInt = Field(alias="TEAM_ID")
    team_name: str = Field(alias="TEAM_NAME")
    team_abbreviation: str = Field(alias="TEAM_ABBREVIATION")
    team_city: str = Field(alias="TEAM_CITY")
    minutes: _CoercedMinutes | None = Field(default=None, alias="MIN")
    fgm: _CoercedInt = Field(alias="FGM")
    fga: _CoercedInt = Field(alias="FGA")
    fg_pct: _CoercedFloat = Field(alias="FG_PCT")
    fg3m: _CoercedInt = Field(alias="FG3M")
    fg3a: _CoercedInt = Field(alias="FG3A")
    fg3_pct: _CoercedFloat = Field(alias="FG3_PCT")
    ftm: _CoercedInt = Field(alias="FTM")
    fta: _CoercedInt = Field(alias="FTA")
    ft_pct: _CoercedFloat = Field(alias="FT_PCT")
    oreb: _CoercedInt = Field(alias="OREB")
    dreb: _CoercedInt = Field(alias="DREB")
    reb: _CoercedInt = Field(alias="REB")
    ast: _CoercedInt = Field(alias="AST")
    stl: _CoercedInt = Field(alias="STL")
    blk: _CoercedInt = Field(alias="BLK")
    to: _CoercedInt = Field(alias="TO")
    pf: _CoercedInt = Field(alias="PF")
    pts: _CoercedInt = Field(alias="PTS")
    plus_minus: _CoercedFloat | None = Field(default=None, alias="PLUS_MINUS")


class TraditionalStarterBenchV2(PandasMixin, PolarsMixin, BaseModel):
    """Aggregated starter / bench split from a v2 box score."""

    game_id: str = Field(alias="GAME_ID")
    team_id: _CoercedInt = Field(alias="TEAM_ID")
    team_name: str = Field(alias="TEAM_NAME")
    team_abbreviation: str = Field(alias="TEAM_ABBREVIATION")
    team_city: str = Field(alias="TEAM_CITY")
    starters_bench: str = Field(alias="STARTERS_BENCH")
    minutes: _CoercedMinutes | None = Field(default=None, alias="MIN")
    fgm: _CoercedInt = Field(alias="FGM")
    fga: _CoercedInt = Field(alias="FGA")
    fg_pct: _CoercedFloat = Field(alias="FG_PCT")
    fg3m: _CoercedInt = Field(alias="FG3M")
    fg3a: _CoercedInt = Field(alias="FG3A")
    fg3_pct: _CoercedFloat = Field(alias="FG3_PCT")
    ftm: _CoercedInt = Field(alias="FTM")
    fta: _CoercedInt = Field(alias="FTA")
    ft_pct: _CoercedFloat = Field(alias="FT_PCT")
    oreb: _CoercedInt = Field(alias="OREB")
    dreb: _CoercedInt = Field(alias="DREB")
    reb: _CoercedInt = Field(alias="REB")
    ast: _CoercedInt = Field(alias="AST")
    stl: _CoercedInt = Field(alias="STL")
    blk: _CoercedInt = Field(alias="BLK")
    to: _CoercedInt = Field(alias="TO")
    pf: _CoercedInt = Field(alias="PF")
    pts: _CoercedInt = Field(alias="PTS")


class BoxScoreTraditionalV2Response(FrozenResponse):
    """Response from the boxscoretraditionalv2 endpoint.

    Returns three result sets in NBA's tabular format:

    - ``player_stats`` — per-player traditional stats including
      ``start_position`` (the v2-only field that identifies the five
      starters per team).
    - ``team_stats`` — per-team aggregated stats.
    - ``starter_bench_stats`` — per-team aggregates split by starters vs
      bench (four rows per game).
    """

    player_stats: list[TraditionalPlayerV2] = Field(
        default_factory=list[TraditionalPlayerV2]
    )
    team_stats: list[TraditionalTeamV2] = Field(default_factory=list[TraditionalTeamV2])
    starter_bench_stats: list[TraditionalStarterBenchV2] = Field(
        default_factory=list[TraditionalStarterBenchV2]
    )

    from_result_sets = model_validator(mode="before")(
        named_result_sets_validator(
            {
                "player_stats": "PlayerStats",
                "team_stats": "TeamStats",
                "starter_bench_stats": "TeamStarterBenchStats",
            }
        )
    )
