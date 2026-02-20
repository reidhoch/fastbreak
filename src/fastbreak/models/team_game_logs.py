"""Models for the Team Game Logs endpoint response."""

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.response import FrozenResponse
from fastbreak.models.common.result_set import named_result_sets_validator


class TeamGameLogsEntry(PandasMixin, PolarsMixin, BaseModel):
    """A single game entry in a team's game logs (extended format).

    Contains traditional box score statistics plus league-wide rankings.
    """

    # Season and team info
    season_year: str = Field(alias="SEASON_YEAR")
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
    tov: float = Field(alias="TOV")
    stl: int = Field(alias="STL")
    blk: int = Field(alias="BLK")
    blka: int = Field(alias="BLKA")
    pf: int = Field(alias="PF")
    pfd: int = Field(alias="PFD")
    pts: int = Field(alias="PTS")
    plus_minus: float | None = Field(alias="PLUS_MINUS")

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

    # Metadata
    available_flag: int = Field(alias="AVAILABLE_FLAG")


class TeamGameLogsResponse(FrozenResponse):
    """Response from the team game logs endpoint.

    Contains extended game log entries with league-wide rankings.
    """

    games: list[TeamGameLogsEntry] = Field(default_factory=list)

    from_result_sets = model_validator(mode="before")(
        named_result_sets_validator({"games": "TeamGameLogs"})
    )
