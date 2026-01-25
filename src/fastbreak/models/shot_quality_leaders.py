"""Models for the shot quality leaders endpoint."""

from pydantic import BaseModel, Field


class ShotQualityLeader(BaseModel):
    """
    Shot Quality measures the expected field goal percentage of a shot based on
    factors like defender distance, shot clock, shooter speed, and shot location.
    This model captures both the quality of shots taken and performance relative
    to expectation.
    """

    # Player identification
    player_id: int = Field(alias="PLAYERID")
    first_name: str = Field(alias="FIRSTNAME")
    last_name: str = Field(alias="LASTNAME")
    player_name: str = Field(alias="PLAYERNAME")
    team_id: int = Field(alias="TEAMID")
    team_city: str = Field(alias="TEAMCITY")
    team_name: str = Field(alias="TEAMNAME")
    team_abbreviation: str = Field(alias="TEAMABBREVIATION")

    # Overall shot quality metrics
    avg_shot_quality: float = Field(alias="AVGSHOTQUALITY")
    avg_made_shot_quality: float = Field(alias="AVGMADESHOTQUALITY")
    avg_missed_shot_quality: float = Field(alias="AVGMISSEDSHOTQUALITY")
    min_shot_quality_on_make: float = Field(alias="MINSHOTQUALITYONMAKE")

    # 2PT shot quality
    avg_shot_quality_2pt: float = Field(alias="AVGSHOTQUALITY2PT")
    avg_made_shot_quality_2pt: float = Field(alias="AVGMADESHOTQUALITY2PT")
    avg_missed_shot_quality_2pt: float = Field(alias="AVGMISSEDSHOTQUALITY2PT")

    # 3PT shot quality
    avg_shot_quality_3pt: float = Field(alias="AVGSHOTQUALITY3PT")
    avg_made_shot_quality_3pt: float = Field(alias="AVGMADESHOTQUALITY3PT")
    avg_missed_shot_quality_3pt: float = Field(alias="AVGMISSEDSHOTQUALITY3PT")

    # Field goal stats
    fg2m: int = Field(alias="FG2M")
    fg2m_rank: int = Field(alias="FG2M_RANK")
    fg2a: int = Field(alias="FG2A")
    fg2a_rank: int = Field(alias="FG2A_RANK")
    fg3m: int = Field(alias="FG3M")
    fg3m_rank: int = Field(alias="FG3M_RANK")
    fg3a: int = Field(alias="FG3A")
    fg3a_rank: int = Field(alias="FG3A_RANK")
    fgm: int = Field(alias="FGM")
    fgm_rank: int = Field(alias="FGM_RANK")
    fga: int = Field(alias="FGA")
    fga_rank: int = Field(alias="FGA_RANK")

    # Field goal percentages
    fg_pct: float = Field(alias="FGPCT")
    fg_pct_above_expected: float = Field(alias="FGPCTABOVEEXPECTED")
    fg3_pct: float = Field(alias="FG3PCT")
    fg3_pct_above_expected: float = Field(alias="FG3PCTABOVEEXPECTED")

    # Defender metrics
    avg_defensive_hand_height: float = Field(alias="AVGDEFENSIVEHANDHEIGHT")
    avg_defender_ball_distance: float = Field(alias="AVGDEFENDERBALLDISTANCE")
    avg_shooter_speed: float = Field(alias="AVGSHOOTERSPEED")
    avg_rotation_degrees: float = Field(alias="AVGROTATIONDEGREES")
    avg_defender_pressure_score: float = Field(alias="AVGDEFENDERPRESSURESCORE")

    # Shot quality ranks
    avg_shot_quality_rank: int = Field(alias="AVGSHOTQUALITY_RANK")
    avg_made_shot_quality_rank: int = Field(alias="AVGMADESHOTQUALITY_RANK")
    avg_missed_shot_quality_rank: int = Field(alias="AVGMISSEDSHOTQUALITY_RANK")
    min_shot_quality_on_make_rank: int = Field(alias="MINSHOTQUALITYONMAKE_RANK")

    # 2PT shot quality ranks
    avg_shot_quality_2pt_rank: int = Field(alias="AVGSHOTQUALITY2PT_RANK")
    avg_made_shot_quality_2pt_rank: int = Field(alias="AVGMADESHOTQUALITY2PT_RANK")
    avg_missed_shot_quality_2pt_rank: int = Field(alias="AVGMISSEDSHOTQUALITY2PT_RANK")

    # 3PT shot quality ranks
    avg_shot_quality_3pt_rank: int = Field(alias="AVGSHOTQUALITY3PT_RANK")
    avg_made_shot_quality_3pt_rank: int = Field(alias="AVGMADESHOTQUALITY3PT_RANK")
    avg_missed_shot_quality_3pt_rank: int = Field(alias="AVGMISSEDSHOTQUALITY3PT_RANK")

    # FG percentage ranks
    fg_pct_rank: int = Field(alias="FGPCT_RANK")
    fg_pct_above_expected_rank: int = Field(alias="FGPCTABOVEEXPECTED_RANK")
    fg3_pct_rank: int = Field(alias="FG3PCT_RANK")
    fg3_pct_above_expected_rank: int = Field(alias="FG3PCTABOVEEXPECTED_RANK")

    # Defender metric ranks
    avg_defensive_hand_height_rank: int = Field(alias="AVGDEFENSIVEHANDHEIGHT_RANK")
    avg_defender_ball_distance_rank: int = Field(alias="AVGDEFENDERBALLDISTANCE_RANK")
    avg_shooter_speed_rank: int = Field(alias="AVGSHOOTERSPEED_RANK")
    avg_rotation_degrees_rank: int = Field(alias="AVGROTATIONDEGREES_RANK")
    avg_defender_pressure_score_rank: int = Field(alias="AVGDEFENDERPRESSURESCORE_RANK")


class ShotQualityLeadersResponse(BaseModel):
    """Response from the shot quality leaders endpoint."""

    params: dict[str, str]
    shots: list[ShotQualityLeader]
