"""Models for the box score defensive v2 endpoint."""

from pydantic import BaseModel, Field

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.meta import Meta
from fastbreak.models.common.response import FrozenResponse


class DefensiveStatistics(BaseModel):
    """Defensive statistics for a player.

    These are matchup-based stats tracking how opponents performed
    while being guarded by this player.
    """

    matchup_minutes: str = Field(alias="matchupMinutes")
    partial_possessions: float = Field(alias="partialPossessions")
    switches_on: int = Field(alias="switchesOn")
    player_points: int = Field(alias="playerPoints")
    defensive_rebounds: int = Field(alias="defensiveRebounds")
    matchup_assists: int = Field(alias="matchupAssists")
    matchup_turnovers: int = Field(alias="matchupTurnovers")
    steals: int
    blocks: int
    matchup_field_goals_made: int = Field(alias="matchupFieldGoalsMade")
    matchup_field_goals_attempted: int = Field(alias="matchupFieldGoalsAttempted")
    matchup_field_goal_percentage: float = Field(alias="matchupFieldGoalPercentage")
    matchup_three_pointers_made: int = Field(alias="matchupThreePointersMade")
    matchup_three_pointers_attempted: int = Field(alias="matchupThreePointersAttempted")
    matchup_three_pointer_percentage: float = Field(
        alias="matchupThreePointerPercentage"
    )


class DefensiveTeamStatistics(BaseModel):
    """Team-level defensive statistics (minimal in v2 API)."""

    minutes: str | None = None


class DefensivePlayer(PandasMixin, PolarsMixin, BaseModel):
    """Player with defensive statistics from a box score."""

    person_id: int = Field(alias="personId")
    first_name: str = Field(alias="firstName")
    family_name: str = Field(alias="familyName")
    name_i: str = Field(alias="nameI")
    player_slug: str = Field(alias="playerSlug")
    position: str
    comment: str
    jersey_num: str = Field(alias="jerseyNum")
    statistics: DefensiveStatistics


class DefensiveTeam(PandasMixin, PolarsMixin, BaseModel):
    """Team with defensive statistics from a box score."""

    team_id: int = Field(alias="teamId")
    team_city: str = Field(alias="teamCity")
    team_name: str = Field(alias="teamName")
    team_tricode: str = Field(alias="teamTricode")
    team_slug: str = Field(alias="teamSlug")
    players: list[DefensivePlayer]
    statistics: DefensiveTeamStatistics


class BoxScoreDefensiveData(BaseModel):
    """Box score defensive data containing both teams."""

    game_id: str = Field(alias="gameId")
    away_team_id: int = Field(alias="awayTeamId")
    home_team_id: int = Field(alias="homeTeamId")
    home_team: DefensiveTeam = Field(alias="homeTeam")
    away_team: DefensiveTeam = Field(alias="awayTeam")


class BoxScoreDefensiveResponse(FrozenResponse):
    """Response from the box score defensive v2 endpoint.

    Contains matchup-based defensive statistics for all players in a game,
    organized by home and away team with nested player data.

    The defensive statistics track opponent performance while being guarded
    by each player, including matchup field goals, assists allowed, and
    partial possessions defended.
    """

    meta: Meta
    box_score_defensive: BoxScoreDefensiveData = Field(alias="boxScoreDefensive")
