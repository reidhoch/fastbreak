"""Models for the player vs player endpoint."""

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.response import FrozenResponse
from fastbreak.models.common.result_set import named_result_sets_validator


class PlayerVsPlayerOverallStats(PandasMixin, PolarsMixin, BaseModel):
    """Overall stats for a player in a player vs player comparison."""

    group_set: str | None = Field(default=None, alias="GROUP_SET")
    group_value: str | None = Field(default=None, alias="GROUP_VALUE")
    player_id: int | None = Field(default=None, alias="PLAYER_ID")
    player_name: str | None = Field(default=None, alias="PLAYER_NAME")
    gp: int | None = Field(default=None, alias="GP")
    wins: int | None = Field(default=None, alias="W")
    losses: int | None = Field(default=None, alias="L")
    w_pct: float | None = Field(default=None, alias="W_PCT")
    min: float | None = Field(default=None, alias="MIN")
    fgm: float | None = Field(default=None, alias="FGM")
    fga: float | None = Field(default=None, alias="FGA")
    fg_pct: float | None = Field(default=None, alias="FG_PCT")
    fg3m: float | None = Field(default=None, alias="FG3M")
    fg3a: float | None = Field(default=None, alias="FG3A")
    fg3_pct: float | None = Field(default=None, alias="FG3_PCT")
    ftm: float | None = Field(default=None, alias="FTM")
    fta: float | None = Field(default=None, alias="FTA")
    ft_pct: float | None = Field(default=None, alias="FT_PCT")
    oreb: float | None = Field(default=None, alias="OREB")
    dreb: float | None = Field(default=None, alias="DREB")
    reb: float | None = Field(default=None, alias="REB")
    ast: float | None = Field(default=None, alias="AST")
    tov: float | None = Field(default=None, alias="TOV")
    stl: float | None = Field(default=None, alias="STL")
    blk: float | None = Field(default=None, alias="BLK")
    blka: float | None = Field(default=None, alias="BLKA")
    pf: float | None = Field(default=None, alias="PF")
    pfd: float | None = Field(default=None, alias="PFD")
    pts: float | None = Field(default=None, alias="PTS")
    plus_minus: float | None = Field(default=None, alias="PLUS_MINUS")
    nba_fantasy_pts: float | None = Field(default=None, alias="NBA_FANTASY_PTS")


class PlayerVsPlayerOnOffCourtStats(PandasMixin, PolarsMixin, BaseModel):
    """Stats for a player when vs player is on/off court."""

    group_set: str | None = Field(default=None, alias="GROUP_SET")
    player_id: int | None = Field(default=None, alias="PLAYER_ID")
    player_name: str | None = Field(default=None, alias="PLAYER_NAME")
    vs_player_id: int | None = Field(default=None, alias="VS_PLAYER_ID")
    vs_player_name: str | None = Field(default=None, alias="VS_PLAYER_NAME")
    court_status: str | None = Field(default=None, alias="COURT_STATUS")
    gp: int | None = Field(default=None, alias="GP")
    wins: int | None = Field(default=None, alias="W")
    losses: int | None = Field(default=None, alias="L")
    w_pct: float | None = Field(default=None, alias="W_PCT")
    min: float | None = Field(default=None, alias="MIN")
    fgm: float | None = Field(default=None, alias="FGM")
    fga: float | None = Field(default=None, alias="FGA")
    fg_pct: float | None = Field(default=None, alias="FG_PCT")
    fg3m: float | None = Field(default=None, alias="FG3M")
    fg3a: float | None = Field(default=None, alias="FG3A")
    fg3_pct: float | None = Field(default=None, alias="FG3_PCT")
    ftm: float | None = Field(default=None, alias="FTM")
    fta: float | None = Field(default=None, alias="FTA")
    ft_pct: float | None = Field(default=None, alias="FT_PCT")
    oreb: float | None = Field(default=None, alias="OREB")
    dreb: float | None = Field(default=None, alias="DREB")
    reb: float | None = Field(default=None, alias="REB")
    ast: float | None = Field(default=None, alias="AST")
    tov: float | None = Field(default=None, alias="TOV")
    stl: float | None = Field(default=None, alias="STL")
    blk: float | None = Field(default=None, alias="BLK")
    blka: float | None = Field(default=None, alias="BLKA")
    pf: float | None = Field(default=None, alias="PF")
    pfd: float | None = Field(default=None, alias="PFD")
    pts: float | None = Field(default=None, alias="PTS")
    plus_minus: float | None = Field(default=None, alias="PLUS_MINUS")
    nba_fantasy_pts: float | None = Field(default=None, alias="NBA_FANTASY_PTS")


class PlayerVsPlayerShotDistanceStats(PandasMixin, PolarsMixin, BaseModel):
    """Shot distance stats for a player overall."""

    group_set: str | None = Field(default=None, alias="GROUP_SET")
    group_value: str | None = Field(default=None, alias="GROUP_VALUE")
    player_id: int | None = Field(default=None, alias="PLAYER_ID")
    player_name: str | None = Field(default=None, alias="PLAYER_NAME")
    fgm: float | None = Field(default=None, alias="FGM")
    fga: float | None = Field(default=None, alias="FGA")
    fg_pct: float | None = Field(default=None, alias="FG_PCT")


class PlayerVsPlayerShotDistanceOnOffStats(PandasMixin, PolarsMixin, BaseModel):
    """Shot distance stats for a player when vs player is on/off court."""

    group_set: str | None = Field(default=None, alias="GROUP_SET")
    player_id: int | None = Field(default=None, alias="PLAYER_ID")
    player_name: str | None = Field(default=None, alias="PLAYER_NAME")
    vs_player_id: int | None = Field(default=None, alias="VS_PLAYER_ID")
    vs_player_name: str | None = Field(default=None, alias="VS_PLAYER_NAME")
    court_status: str | None = Field(default=None, alias="COURT_STATUS")
    group_value: str | None = Field(default=None, alias="GROUP_VALUE")
    fgm: float | None = Field(default=None, alias="FGM")
    fga: float | None = Field(default=None, alias="FGA")
    fg_pct: float | None = Field(default=None, alias="FG_PCT")


class PlayerVsPlayerShotAreaStats(PandasMixin, PolarsMixin, BaseModel):
    """Shot area stats for a player overall."""

    group_set: str | None = Field(default=None, alias="GROUP_SET")
    group_value: str | None = Field(default=None, alias="GROUP_VALUE")
    player_id: int | None = Field(default=None, alias="PLAYER_ID")
    player_name: str | None = Field(default=None, alias="PLAYER_NAME")
    fgm: float | None = Field(default=None, alias="FGM")
    fga: float | None = Field(default=None, alias="FGA")
    fg_pct: float | None = Field(default=None, alias="FG_PCT")


class PlayerVsPlayerShotAreaOnOffStats(PandasMixin, PolarsMixin, BaseModel):
    """Shot area stats for a player when vs player is on/off court."""

    group_set: str | None = Field(default=None, alias="GROUP_SET")
    player_id: int | None = Field(default=None, alias="PLAYER_ID")
    player_name: str | None = Field(default=None, alias="PLAYER_NAME")
    vs_player_id: int | None = Field(default=None, alias="VS_PLAYER_ID")
    vs_player_name: str | None = Field(default=None, alias="VS_PLAYER_NAME")
    court_status: str | None = Field(default=None, alias="COURT_STATUS")
    group_value: str | None = Field(default=None, alias="GROUP_VALUE")
    fgm: float | None = Field(default=None, alias="FGM")
    fga: float | None = Field(default=None, alias="FGA")
    fg_pct: float | None = Field(default=None, alias="FG_PCT")


class PlayerVsPlayerPlayerInfo(PandasMixin, PolarsMixin, BaseModel):
    """Player info from player vs player endpoint."""

    person_id: int | None = Field(default=None, alias="PERSON_ID")
    first_name: str | None = Field(default=None, alias="FIRST_NAME")
    last_name: str | None = Field(default=None, alias="LAST_NAME")
    display_first_last: str | None = Field(default=None, alias="DISPLAY_FIRST_LAST")
    display_last_comma_first: str | None = Field(
        default=None, alias="DISPLAY_LAST_COMMA_FIRST"
    )
    display_fi_last: str | None = Field(default=None, alias="DISPLAY_FI_LAST")
    birthdate: str | None = Field(default=None, alias="BIRTHDATE")
    school: str | None = Field(default=None, alias="SCHOOL")
    country: str | None = Field(default=None, alias="COUNTRY")
    last_affiliation: str | None = Field(default=None, alias="LAST_AFFILIATION")


class PlayerVsPlayerResponse(FrozenResponse):
    """Response from the player vs player endpoint.

    Contains multiple result sets:
    - overall: Overall stats for both players
    - on_off_court: Player stats when vs player is on/off court
    - shot_distance_overall: Shot distance breakdown overall
    - shot_distance_on_court: Shot distance when vs player is on court
    - shot_distance_off_court: Shot distance when vs player is off court
    - shot_area_overall: Shot area breakdown overall
    - shot_area_on_court: Shot area when vs player is on court
    - shot_area_off_court: Shot area when vs player is off court
    - player_info: Info about the primary player
    - vs_player_info: Info about the vs player
    """

    overall: list[PlayerVsPlayerOverallStats] = Field(default_factory=list)
    on_off_court: list[PlayerVsPlayerOnOffCourtStats] = Field(default_factory=list)
    shot_distance_overall: list[PlayerVsPlayerShotDistanceStats] = Field(
        default_factory=list
    )
    shot_distance_on_court: list[PlayerVsPlayerShotDistanceOnOffStats] = Field(
        default_factory=list
    )
    shot_distance_off_court: list[PlayerVsPlayerShotDistanceOnOffStats] = Field(
        default_factory=list
    )
    shot_area_overall: list[PlayerVsPlayerShotAreaStats] = Field(default_factory=list)
    shot_area_on_court: list[PlayerVsPlayerShotAreaOnOffStats] = Field(
        default_factory=list
    )
    shot_area_off_court: list[PlayerVsPlayerShotAreaOnOffStats] = Field(
        default_factory=list
    )
    player_info: list[PlayerVsPlayerPlayerInfo] = Field(default_factory=list)
    vs_player_info: list[PlayerVsPlayerPlayerInfo] = Field(default_factory=list)

    from_result_sets = model_validator(mode="before")(
        named_result_sets_validator(
            {
                "overall": "Overall",
                "on_off_court": "OnOffCourt",
                "shot_distance_overall": "ShotDistanceOverall",
                "shot_distance_on_court": "ShotDistanceOnCourt",
                "shot_distance_off_court": "ShotDistanceOffCourt",
                "shot_area_overall": "ShotAreaOverall",
                "shot_area_on_court": "ShotAreaOnCourt",
                "shot_area_off_court": "ShotAreaOffCourt",
                "player_info": "PlayerInfo",
                "vs_player_info": "VsPlayerInfo",
            }
        )
    )
