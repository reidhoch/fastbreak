"""Models for the Player Game Logs endpoint response."""

from typing import Any

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.response import FrozenResponse
from fastbreak.models.common.result_set import (
    is_tabular_response,
    parse_result_set_by_name,
)


class PlayerGameLogsEntry(PandasMixin, PolarsMixin, BaseModel):
    """A single game entry in a player's game logs (extended format).

    Contains traditional box score statistics plus rankings and fantasy points.
    """

    # Season and player info
    season_year: str = Field(alias="SEASON_YEAR")
    player_id: int = Field(alias="PLAYER_ID")
    player_name: str = Field(alias="PLAYER_NAME")
    nickname: str | None = Field(alias="NICKNAME")
    team_id: int = Field(alias="TEAM_ID")
    team_abbreviation: str = Field(alias="TEAM_ABBREVIATION")
    team_name: str = Field(alias="TEAM_NAME")

    # Game info
    game_id: str = Field(alias="GAME_ID")
    game_date: str = Field(alias="GAME_DATE")
    matchup: str = Field(alias="MATCHUP")
    wl: str | None = Field(alias="WL")

    # Traditional stats
    minutes: float | None = Field(alias="MIN")
    fgm: int = Field(alias="FGM")
    fga: int = Field(alias="FGA")
    fg_pct: float | None = Field(alias="FG_PCT")
    fg3m: int = Field(alias="FG3M")
    fg3a: int = Field(alias="FG3A")
    fg3_pct: float | None = Field(alias="FG3_PCT")
    ftm: int = Field(alias="FTM")
    fta: int = Field(alias="FTA")
    ft_pct: float | None = Field(alias="FT_PCT")
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
    plus_minus: int | None = Field(alias="PLUS_MINUS")

    # Fantasy and special stats
    nba_fantasy_pts: float | None = Field(alias="NBA_FANTASY_PTS")
    dd2: int = Field(alias="DD2")
    td3: int = Field(alias="TD3")
    wnba_fantasy_pts: float | None = Field(alias="WNBA_FANTASY_PTS")

    # Rankings
    gp_rank: int | None = Field(alias="GP_RANK")
    w_rank: int | None = Field(alias="W_RANK")
    l_rank: int | None = Field(alias="L_RANK")
    w_pct_rank: int | None = Field(alias="W_PCT_RANK")
    min_rank: int | None = Field(alias="MIN_RANK")
    fgm_rank: int | None = Field(alias="FGM_RANK")
    fga_rank: int | None = Field(alias="FGA_RANK")
    fg_pct_rank: int | None = Field(alias="FG_PCT_RANK")
    fg3m_rank: int | None = Field(alias="FG3M_RANK")
    fg3a_rank: int | None = Field(alias="FG3A_RANK")
    fg3_pct_rank: int | None = Field(alias="FG3_PCT_RANK")
    ftm_rank: int | None = Field(alias="FTM_RANK")
    fta_rank: int | None = Field(alias="FTA_RANK")
    ft_pct_rank: int | None = Field(alias="FT_PCT_RANK")
    oreb_rank: int | None = Field(alias="OREB_RANK")
    dreb_rank: int | None = Field(alias="DREB_RANK")
    reb_rank: int | None = Field(alias="REB_RANK")
    ast_rank: int | None = Field(alias="AST_RANK")
    tov_rank: int | None = Field(alias="TOV_RANK")
    stl_rank: int | None = Field(alias="STL_RANK")
    blk_rank: int | None = Field(alias="BLK_RANK")
    blka_rank: int | None = Field(alias="BLKA_RANK")
    pf_rank: int | None = Field(alias="PF_RANK")
    pfd_rank: int | None = Field(alias="PFD_RANK")
    pts_rank: int | None = Field(alias="PTS_RANK")
    plus_minus_rank: int | None = Field(alias="PLUS_MINUS_RANK")
    nba_fantasy_pts_rank: int | None = Field(alias="NBA_FANTASY_PTS_RANK")
    dd2_rank: int | None = Field(alias="DD2_RANK")
    td3_rank: int | None = Field(alias="TD3_RANK")
    wnba_fantasy_pts_rank: int | None = Field(alias="WNBA_FANTASY_PTS_RANK")

    # Metadata
    available_flag: int = Field(alias="AVAILABLE_FLAG")
    min_sec: str | None = Field(alias="MIN_SEC")
    team_count: int | None = Field(alias="TEAM_COUNT")


class PlayerGameLogsResponse(FrozenResponse):
    """Response from the player game logs endpoint.

    Contains extended game log entries with rankings and fantasy points.
    """

    games: list[PlayerGameLogsEntry] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def from_result_sets(cls, data: object) -> dict[str, Any]:
        """Transform NBA's tabular resultSets format into structured data."""
        if not is_tabular_response(data):
            return data  # type: ignore[return-value]

        return {
            "games": parse_result_set_by_name(data, "PlayerGameLogs"),
        }
