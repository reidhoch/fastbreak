"""Models for the Team Player On/Off Summary endpoint response."""

from typing import Any

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.result_set import is_tabular_response, parse_result_set_by_name


class TeamOnOffSummaryOverall(BaseModel):
    """Team's overall statistics for the season.

    Contains aggregate stats with league-wide rankings.
    """

    group_set: str = Field(alias="GROUP_SET")
    group_value: str = Field(alias="GROUP_VALUE")
    team_id: int = Field(alias="TEAM_ID")
    team_abbreviation: str = Field(alias="TEAM_ABBREVIATION")
    team_name: str = Field(alias="TEAM_NAME")

    # Record
    gp: int = Field(alias="GP")
    wins: int = Field(alias="W")
    losses: int = Field(alias="L")
    win_pct: float = Field(alias="W_PCT")

    # Traditional stats
    minutes: float = Field(alias="MIN")
    fgm: float = Field(alias="FGM")
    fga: float = Field(alias="FGA")
    fg_pct: float = Field(alias="FG_PCT")
    fg3m: float = Field(alias="FG3M")
    fg3a: float = Field(alias="FG3A")
    fg3_pct: float = Field(alias="FG3_PCT")
    ftm: float = Field(alias="FTM")
    fta: float = Field(alias="FTA")
    ft_pct: float = Field(alias="FT_PCT")
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

    # Rankings
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


class PlayerOnOffSummary(BaseModel):
    """Summarized on/off court statistics for a player.

    Contains key impact metrics: ratings and plus/minus.
    """

    group_set: str = Field(alias="GROUP_SET")
    team_id: int = Field(alias="TEAM_ID")
    team_abbreviation: str = Field(alias="TEAM_ABBREVIATION")
    team_name: str = Field(alias="TEAM_NAME")
    vs_player_id: int = Field(alias="VS_PLAYER_ID")
    vs_player_name: str = Field(alias="VS_PLAYER_NAME")
    court_status: str = Field(alias="COURT_STATUS")

    # Key metrics
    gp: int = Field(alias="GP")
    minutes: float = Field(alias="MIN")
    plus_minus: float = Field(alias="PLUS_MINUS")
    off_rating: float = Field(alias="OFF_RATING")
    def_rating: float = Field(alias="DEF_RATING")
    net_rating: float = Field(alias="NET_RATING")


class TeamPlayerOnOffSummaryResponse(BaseModel):
    """Response from the team player on/off summary endpoint.

    Contains overall team stats plus summarized on/off court splits per player.
    More compact than the Details endpoint - focuses on ratings and plus/minus.
    """

    overall: TeamOnOffSummaryOverall | None = Field(default=None)
    players_on_court: list[PlayerOnOffSummary] = Field(default_factory=list)
    players_off_court: list[PlayerOnOffSummary] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def from_result_sets(cls, data: object) -> dict[str, Any]:
        """Transform NBA's tabular resultSets format into structured data."""
        if not is_tabular_response(data):
            return data  # type: ignore[return-value]

        overall_rows = parse_result_set_by_name(
            data,
            "OverallTeamPlayerOnOffSummary",
        )

        return {
            "overall": overall_rows[0] if overall_rows else None,
            "players_on_court": parse_result_set_by_name(
                data,
                "PlayersOnCourtTeamPlayerOnOffSummary",
            ),
            "players_off_court": parse_result_set_by_name(
                data,
                "PlayersOffCourtTeamPlayerOnOffSummary",
            ),
        }
