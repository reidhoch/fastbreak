"""Models for the Player Fantasy Profile endpoint response."""

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.response import FrozenResponse
from fastbreak.models.common.result_set import named_result_sets_validator


class FantasyProfileStats(PandasMixin, PolarsMixin, BaseModel):
    """Player fantasy-production stats for one split segment.

    The standard box-score block plus fantasy columns (double-doubles,
    triple-doubles, FanDuel and NBA fantasy points). Unlike the dashboard
    splits this endpoint returns no ``*_RANK`` columns. ``season_year`` is
    populated only for the days-rest split (which carries an extra column);
    it is ``None`` for the other splits.
    """

    group_set: str = Field(alias="GROUP_SET")
    group_value: str = Field(alias="GROUP_VALUE")
    season_year: str | None = Field(default=None, alias="SEASON_YEAR")

    gp: int = Field(alias="GP")
    w: int = Field(alias="W")
    losses: int = Field(alias="L")
    w_pct: float = Field(alias="W_PCT")
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

    # Fantasy-specific columns.
    dd2: int = Field(alias="DD2")
    td3: int = Field(alias="TD3")
    fan_duel_pts: float | None = Field(default=None, alias="FAN_DUEL_PTS")
    nba_fantasy_pts: float | None = Field(default=None, alias="NBA_FANTASY_PTS")


class PlayerFantasyProfileResponse(FrozenResponse):
    """Response from the player fantasy profile endpoint.

    Fantasy production split five ways: overall, home/road, last-N-games,
    days of rest, and per opponent. Complements ``PlayerFantasyProfileBarGraph``
    (which only carries season and last-five averages).
    """

    overall: FantasyProfileStats | None = None
    by_location: list[FantasyProfileStats] = Field(
        default_factory=list[FantasyProfileStats]
    )
    last_n_games: list[FantasyProfileStats] = Field(
        default_factory=list[FantasyProfileStats]
    )
    by_days_rest: list[FantasyProfileStats] = Field(
        default_factory=list[FantasyProfileStats]
    )
    by_opponent: list[FantasyProfileStats] = Field(
        default_factory=list[FantasyProfileStats]
    )

    from_result_sets = model_validator(mode="before")(
        named_result_sets_validator(
            {
                "overall": ("Overall", True),
                "by_location": "Location",
                "last_n_games": "LastNGames",
                "by_days_rest": "DaysRestModified",
                "by_opponent": "Opponent",
            }
        )
    )
