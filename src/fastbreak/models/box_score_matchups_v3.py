"""Models for the box score matchups v3 endpoint."""

from pydantic import BaseModel, Field

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.meta import Meta
from fastbreak.models.common.response import FrozenResponse


class MatchupStatistics(BaseModel):
    """Detailed matchup statistics between two players."""

    matchup_minutes: str = Field(alias="matchupMinutes")
    matchup_minutes_sort: float = Field(alias="matchupMinutesSort")
    partial_possessions: float = Field(alias="partialPossessions")
    percentage_defender_total_time: float = Field(alias="percentageDefenderTotalTime")
    percentage_offensive_total_time: float = Field(alias="percentageOffensiveTotalTime")
    percentage_total_time_both_on: float = Field(alias="percentageTotalTimeBothOn")
    switches_on: int = Field(alias="switchesOn")
    player_points: int = Field(alias="playerPoints")
    team_points: int = Field(alias="teamPoints")
    matchup_assists: int = Field(alias="matchupAssists")
    matchup_potential_assists: int = Field(alias="matchupPotentialAssists")
    matchup_turnovers: int = Field(alias="matchupTurnovers")
    matchup_blocks: int = Field(alias="matchupBlocks")
    matchup_field_goals_made: int = Field(alias="matchupFieldGoalsMade")
    matchup_field_goals_attempted: int = Field(alias="matchupFieldGoalsAttempted")
    matchup_field_goals_percentage: float = Field(alias="matchupFieldGoalsPercentage")
    matchup_three_pointers_made: int = Field(alias="matchupThreePointersMade")
    matchup_three_pointers_attempted: int = Field(alias="matchupThreePointersAttempted")
    matchup_three_pointers_percentage: float = Field(
        alias="matchupThreePointersPercentage"
    )
    help_blocks: int = Field(alias="helpBlocks")
    help_field_goals_made: int = Field(alias="helpFieldGoalsMade")
    help_field_goals_attempted: int = Field(alias="helpFieldGoalsAttempted")
    help_field_goals_percentage: float = Field(alias="helpFieldGoalsPercentage")
    matchup_free_throws_made: int = Field(alias="matchupFreeThrowsMade")
    matchup_free_throws_attempted: int = Field(alias="matchupFreeThrowsAttempted")
    shooting_fouls: int = Field(alias="shootingFouls")


class MatchupOpponentV3(BaseModel):
    """An opponent in a player's matchup list."""

    person_id: int = Field(alias="personId")
    first_name: str = Field(alias="firstName")
    family_name: str = Field(alias="familyName")
    name_i: str = Field(alias="nameI")
    player_slug: str = Field(alias="playerSlug")
    jersey_num: str = Field(alias="jerseyNum")
    statistics: MatchupStatistics


class MatchupsPlayerV3(PandasMixin, PolarsMixin, BaseModel):
    """A player with their matchup data in V3 format."""

    person_id: int = Field(alias="personId")
    first_name: str = Field(alias="firstName")
    family_name: str = Field(alias="familyName")
    name_i: str = Field(alias="nameI")
    player_slug: str = Field(alias="playerSlug")
    position: str
    comment: str
    jersey_num: str = Field(alias="jerseyNum")
    matchups: list[MatchupOpponentV3]


class MatchupsTeamV3(PandasMixin, PolarsMixin, BaseModel):
    """A team with player matchup data in V3 format."""

    team_id: int = Field(alias="teamId")
    team_city: str = Field(alias="teamCity")
    team_name: str = Field(alias="teamName")
    team_tricode: str = Field(alias="teamTricode")
    team_slug: str = Field(alias="teamSlug")
    players: list[MatchupsPlayerV3]


class BoxScoreMatchupsV3Data(BaseModel):
    """Box score matchups data for V3 format."""

    game_id: str = Field(alias="gameId")
    away_team_id: int = Field(alias="awayTeamId")
    home_team_id: int = Field(alias="homeTeamId")
    home_team: MatchupsTeamV3 = Field(alias="homeTeam")
    away_team: MatchupsTeamV3 = Field(alias="awayTeam")


class BoxScoreMatchupsV3Response(FrozenResponse):
    """Response from the box score matchups v3 endpoint.

    Contains detailed player-vs-player matchup data in modern nested
    JSON format. Shows who guarded whom and with what results, including
    shooting percentages, assists, turnovers, and help defense stats.

    This is the V3 format with richer data than the traditional
    BoxScoreMatchups endpoint.
    """

    meta: Meta
    box_score_matchups: BoxScoreMatchupsV3Data = Field(alias="boxScoreMatchups")
