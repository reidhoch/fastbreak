"""Models for the Team Dashboard Passing endpoint response."""

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.response import FrozenResponse
from fastbreak.models.common.result_set import named_result_sets_validator


class TeamPassMade(PandasMixin, PolarsMixin, BaseModel):
    """Statistics for passes made by a team player to teammates.

    Contains passing and shooting efficiency data for passes from a player.
    """

    team_id: int = Field(alias="TEAM_ID")
    team_name: str = Field(alias="TEAM_NAME")
    pass_type: str = Field(alias="PASS_TYPE")
    games: int = Field(alias="G")
    pass_from: str = Field(alias="PASS_FROM")
    pass_teammate_player_id: int = Field(alias="PASS_TEAMMATE_PLAYER_ID")
    frequency: float = Field(alias="FREQUENCY")
    passes: float = Field(alias="PASS")
    ast: float = Field(alias="AST")
    fgm: float = Field(alias="FGM")
    fga: float = Field(alias="FGA")
    fg_pct: float | None = Field(alias="FG_PCT")
    fg2m: float = Field(alias="FG2M")
    fg2a: float = Field(alias="FG2A")
    fg2_pct: float | None = Field(alias="FG2_PCT")
    fg3m: float = Field(alias="FG3M")
    fg3a: float = Field(alias="FG3A")
    fg3_pct: float | None = Field(alias="FG3_PCT")


class TeamPassReceived(PandasMixin, PolarsMixin, BaseModel):
    """Statistics for passes received by a team player from teammates.

    Contains passing and shooting efficiency data for passes to a player.
    """

    team_id: int = Field(alias="TEAM_ID")
    team_name: str = Field(alias="TEAM_NAME")
    pass_type: str = Field(alias="PASS_TYPE")
    games: int = Field(alias="G")
    pass_to: str = Field(alias="PASS_TO")
    pass_teammate_player_id: int = Field(alias="PASS_TEAMMATE_PLAYER_ID")
    frequency: float = Field(alias="FREQUENCY")
    passes: float = Field(alias="PASS")
    ast: float = Field(alias="AST")
    fgm: float = Field(alias="FGM")
    fga: float = Field(alias="FGA")
    fg_pct: float | None = Field(alias="FG_PCT")
    fg2m: float = Field(alias="FG2M")
    fg2a: float = Field(alias="FG2A")
    fg2_pct: float | None = Field(alias="FG2_PCT")
    fg3m: float = Field(alias="FG3M")
    fg3a: float = Field(alias="FG3A")
    fg3_pct: float | None = Field(alias="FG3_PCT")


class TeamDashPtPassResponse(FrozenResponse):
    """Response from the team dashboard passing endpoint.

    Contains pass statistics for all team players:
    - passes_made: Passes made by each player to teammates
    - passes_received: Passes received by each player from teammates
    """

    passes_made: list[TeamPassMade] = Field(default_factory=list)
    passes_received: list[TeamPassReceived] = Field(default_factory=list)

    from_result_sets = model_validator(mode="before")(
        named_result_sets_validator(
            {
                "passes_made": "PassesMade",
                "passes_received": "PassesReceived",
            }
        )
    )
