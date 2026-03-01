from typing import Self

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin


class MatchupStatistics(PandasMixin, PolarsMixin, BaseModel):
    """Statistics for a specific player-vs-player defensive matchup."""

    matchup_minutes: str = Field(alias="matchupMinutes")
    matchup_minutes_sort: float = Field(ge=0.0, alias="matchupMinutesSort")
    partial_possessions: float = Field(ge=0.0, alias="partialPossessions")
    percentage_defender_total_time: float = Field(
        ge=0.0, alias="percentageDefenderTotalTime"
    )
    percentage_offensive_total_time: float = Field(
        ge=0.0, alias="percentageOffensiveTotalTime"
    )
    percentage_total_time_both_on: float = Field(
        ge=0.0, alias="percentageTotalTimeBothOn"
    )
    switches_on: int = Field(ge=0, alias="switchesOn")
    player_points: int = Field(ge=0, alias="playerPoints")
    team_points: int = Field(ge=0, alias="teamPoints")
    matchup_assists: int = Field(ge=0, alias="matchupAssists")
    matchup_potential_assists: int = Field(ge=0, alias="matchupPotentialAssists")
    matchup_turnovers: int = Field(ge=0, alias="matchupTurnovers")
    matchup_blocks: int = Field(ge=0, alias="matchupBlocks")
    matchup_field_goals_made: int = Field(ge=0, alias="matchupFieldGoalsMade")
    matchup_field_goals_attempted: int = Field(ge=0, alias="matchupFieldGoalsAttempted")
    matchup_field_goals_percentage: float = Field(
        ge=0.0, le=1.0, alias="matchupFieldGoalsPercentage"
    )
    matchup_three_pointers_made: int = Field(ge=0, alias="matchupThreePointersMade")
    matchup_three_pointers_attempted: int = Field(
        ge=0, alias="matchupThreePointersAttempted"
    )
    matchup_three_pointers_percentage: float = Field(
        ge=0.0, le=1.0, alias="matchupThreePointersPercentage"
    )
    help_blocks: int = Field(ge=0, alias="helpBlocks")
    help_field_goals_made: int = Field(ge=0, alias="helpFieldGoalsMade")
    help_field_goals_attempted: int = Field(ge=0, alias="helpFieldGoalsAttempted")
    help_field_goals_percentage: float = Field(
        ge=0.0, le=1.0, alias="helpFieldGoalsPercentage"
    )
    matchup_free_throws_made: int = Field(ge=0, alias="matchupFreeThrowsMade")
    matchup_free_throws_attempted: int = Field(ge=0, alias="matchupFreeThrowsAttempted")
    shooting_fouls: int = Field(ge=0, alias="shootingFouls")

    @model_validator(mode="after")
    def check_made_not_exceeding_attempted(self) -> Self:
        """Validate made shots do not exceed attempted, and 3P stats are subsets of FG stats."""
        pairs = [
            ("matchup_field_goals_made", "matchup_field_goals_attempted"),
            ("matchup_three_pointers_made", "matchup_three_pointers_attempted"),
            ("matchup_three_pointers_attempted", "matchup_field_goals_attempted"),
            ("matchup_three_pointers_made", "matchup_field_goals_made"),
            ("help_field_goals_made", "help_field_goals_attempted"),
            ("matchup_free_throws_made", "matchup_free_throws_attempted"),
        ]
        for lower_name, upper_name in pairs:
            lower_val = getattr(self, lower_name)
            upper_val = getattr(self, upper_name)
            if lower_val > upper_val:
                msg = f"{lower_name} ({lower_val}) > {upper_name} ({upper_val})"
                raise ValueError(msg)
        return self
