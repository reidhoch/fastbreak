"""League dashboard player clutch stats response model."""

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.response import FrozenResponse
from fastbreak.models.common.result_set import tabular_validator


class LeagueDashPlayerClutchRow(PandasMixin, PolarsMixin, BaseModel):
    """Individual player clutch statistics from league dashboard."""

    group_set: str | None = Field(default=None, alias="GROUP_SET")
    player_id: int = Field(alias="PLAYER_ID")
    player_name: str = Field(alias="PLAYER_NAME")
    nickname: str | None = Field(default=None, alias="NICKNAME")
    team_id: int = Field(alias="TEAM_ID")
    team_abbreviation: str = Field(alias="TEAM_ABBREVIATION")
    age: float | None = Field(default=None, alias="AGE")
    gp: int = Field(alias="GP")
    w: int = Field(alias="W")
    losses: int = Field(alias="L")
    w_pct: float | None = Field(default=None, alias="W_PCT")
    min: float = Field(alias="MIN")
    fgm: float = Field(alias="FGM")
    fga: float = Field(alias="FGA")
    fg_pct: float | None = Field(default=None, alias="FG_PCT")
    fg3m: float = Field(alias="FG3M")
    fg3a: float = Field(alias="FG3A")
    fg3_pct: float | None = Field(default=None, alias="FG3_PCT")
    ftm: float = Field(alias="FTM")
    fta: float = Field(alias="FTA")
    ft_pct: float | None = Field(default=None, alias="FT_PCT")
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
    nba_fantasy_pts: float | None = Field(default=None, alias="NBA_FANTASY_PTS")
    dd2: int | None = Field(default=None, alias="DD2")
    td3: int | None = Field(default=None, alias="TD3")
    wnba_fantasy_pts: float | None = Field(default=None, alias="WNBA_FANTASY_PTS")

    # Rank columns
    gp_rank: int = Field(alias="GP_RANK")
    w_rank: int = Field(alias="W_RANK")
    l_rank: int = Field(alias="L_RANK")
    w_pct_rank: int = Field(alias="W_PCT_RANK")
    min_rank: int = Field(alias="MIN_RANK")
    fgm_rank: int = Field(alias="FGM_RANK")
    fga_rank: int = Field(alias="FGA_RANK")
    fg_pct_rank: int = Field(alias="FG_PCT_RANK")
    fg3m_rank: int = Field(alias="FG3M_RANK")
    fg3a_rank: int = Field(alias="FG3A_RANK")
    fg3_pct_rank: int = Field(alias="FG3_PCT_RANK")
    ftm_rank: int = Field(alias="FTM_RANK")
    fta_rank: int = Field(alias="FTA_RANK")
    ft_pct_rank: int = Field(alias="FT_PCT_RANK")
    oreb_rank: int = Field(alias="OREB_RANK")
    dreb_rank: int = Field(alias="DREB_RANK")
    reb_rank: int = Field(alias="REB_RANK")
    ast_rank: int = Field(alias="AST_RANK")
    tov_rank: int = Field(alias="TOV_RANK")
    stl_rank: int = Field(alias="STL_RANK")
    blk_rank: int = Field(alias="BLK_RANK")
    blka_rank: int = Field(alias="BLKA_RANK")
    pf_rank: int = Field(alias="PF_RANK")
    pfd_rank: int = Field(alias="PFD_RANK")
    pts_rank: int = Field(alias="PTS_RANK")
    plus_minus_rank: int = Field(alias="PLUS_MINUS_RANK")
    nba_fantasy_pts_rank: int = Field(alias="NBA_FANTASY_PTS_RANK")
    dd2_rank: int = Field(alias="DD2_RANK")
    td3_rank: int = Field(alias="TD3_RANK")
    wnba_fantasy_pts_rank: int = Field(alias="WNBA_FANTASY_PTS_RANK")


class LeagueDashPlayerClutchResponse(FrozenResponse):
    """Response from leaguedashplayerclutch endpoint."""

    players: list[LeagueDashPlayerClutchRow] = Field(default_factory=list)

    from_result_sets = model_validator(mode="before")(tabular_validator("players"))
