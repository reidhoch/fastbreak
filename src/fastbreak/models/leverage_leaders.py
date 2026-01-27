"""Models for the leverage leaders endpoint."""

from pydantic import BaseModel, Field

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin


class LeverageLeader(PandasMixin, PolarsMixin, BaseModel):
    """
    Leverage Score measures the impact each play has on a team's chance to win the
    game and distributes the credit for those plays to the offensive and defensive
    players involved using the NBA's real-time defensive matchups and expected
    field goal percentage to quantify each player's contributions.
    """

    player_id: int = Field(alias="PLAYERID")
    first_name: str = Field(alias="FIRSTNAME")
    last_name: str = Field(alias="LASTNAME")
    team_id: int = Field(alias="TEAMID")
    team_abbreviation: str = Field(alias="TEAMABBREVIATION")
    team_name: str = Field(alias="TEAMNAME")
    team_city: str = Field(alias="TEAMCITY")
    offense: float = Field(alias="OFFENSE")
    defense: float = Field(alias="DEFENSE")
    full: float = Field(alias="FULL")
    shooting: float = Field(alias="SHOOTING")
    turnovers: float = Field(alias="TURNOVERS")
    rebounds: float = Field(alias="REBOUNDS")
    creation: float = Field(alias="CREATION")
    on_ball_def: float = Field(alias="ONBALLDEF")
    games_played: int = Field(alias="GAMESPLAYED")
    minutes: float = Field(alias="MINUTES")
    pts: float = Field(alias="PTS")
    reb: float = Field(alias="REB")
    ast: float = Field(alias="AST")


class LeverageLeadersResponse(BaseModel):
    """Response from the leverage leaders endpoint."""

    params: dict[str, str]
    leaders: list[LeverageLeader]
