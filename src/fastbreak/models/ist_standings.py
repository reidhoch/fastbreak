"""Models for the IST (In-Season Tournament) standings endpoint."""

from pydantic import BaseModel, Field

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin


class IstGame(PandasMixin, PolarsMixin, BaseModel):
    """Individual IST game result for a team."""

    game_id: str = Field(alias="gameId")
    game_number: int = Field(alias="gameNumber")
    opponent_team_abbreviation: str = Field(alias="opponentTeamAbbreviation")
    location: str = Field(alias="location")
    game_status: int = Field(alias="gameStatus")
    game_status_text: str = Field(alias="gameStatusText")
    outcome: str = Field(alias="outcome")


class IstTeamStanding(PandasMixin, PolarsMixin, BaseModel):
    """Team standing in the IST (In-Season Tournament / NBA Cup)."""

    team_id: int = Field(alias="teamId")
    team_city: str = Field(alias="teamCity")
    team_name: str = Field(alias="teamName")
    team_abbreviation: str = Field(alias="teamAbbreviation")
    team_slug: str = Field(alias="teamSlug")
    conference: str = Field(alias="conference")
    ist_group: str = Field(alias="istGroup")
    clinch_indicator: str = Field(alias="clinchIndicator")
    clinched_ist_knockout: int = Field(alias="clinchedIstKnockout")
    clinched_ist_group: int = Field(alias="clinchedIstGroup")
    clinched_ist_wildcard: int = Field(alias="clinchedIstWildcard")
    ist_wildcard_rank: int | None = Field(alias="istWildcardRank")
    ist_group_rank: int | None = Field(alias="istGroupRank")
    ist_knockout_rank: int | None = Field(alias="istKnockoutRank")
    wins: int = Field(alias="wins")
    losses: int = Field(alias="losses")
    pct: float = Field(alias="pct")
    ist_group_gb: float | None = Field(alias="istGroupGb")
    ist_wildcard_gb: float | None = Field(alias="istWildcardGb")
    diff: int = Field(alias="diff")
    pts: int = Field(alias="pts")
    opp_pts: int = Field(alias="oppPts")
    games: list[IstGame] = Field(alias="games")


class IstStandingsResponse(BaseModel):
    """Response from the IST standings endpoint.

    Contains standings for all teams in the In-Season Tournament (NBA Cup),
    including group rankings, clinch status, and individual game results.
    """

    league_id: str = Field(alias="leagueId")
    season_year: str = Field(alias="seasonYear")
    unix_time_stamp: int = Field(alias="unixTimeStamp")
    time_stamp_utc: str = Field(alias="timeStampUtc")
    teams: list[IstTeamStanding] = Field(alias="teams")
