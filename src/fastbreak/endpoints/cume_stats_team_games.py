"""Endpoint for fetching games a team has participated in."""

from dataclasses import dataclass
from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.cume_stats_team_games import CumeStatsTeamGamesResponse


@dataclass(frozen=True)
class CumeStatsTeamGames(Endpoint[CumeStatsTeamGamesResponse]):
    """Fetch list of games a team has participated in.

    Args:
        league_id: League identifier ("00" for NBA)
        season: Season in YYYY format (e.g., "2025")
        season_type: Type of season ("Regular Season", "Playoffs", "Pre Season")
        team_id: The team's unique identifier
        location: Filter by game location ("Home", "Road")
        outcome: Filter by game outcome ("W", "L")
        vs_team_id: Filter by opponent team ID
        vs_division: Filter by opponent division
        vs_conference: Filter by opponent conference ("East", "West")

    """

    path: ClassVar[str] = "cumestatsteamgames"
    response_model: ClassVar[type[CumeStatsTeamGamesResponse]] = (
        CumeStatsTeamGamesResponse
    )

    # Required parameters
    league_id: str = "00"
    season: str = "2025"
    season_type: str = "Regular Season"
    team_id: int = 0

    # Optional filters
    location: str | None = None
    outcome: str | None = None
    vs_team_id: int = 0
    vs_division: str | None = None
    vs_conference: str | None = None

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        result: dict[str, str] = {
            "LeagueID": self.league_id,
            "Season": self.season,
            "SeasonType": self.season_type,
            "TeamID": str(self.team_id),
            "VsTeamID": str(self.vs_team_id),
        }

        if self.location is not None:
            result["Location"] = self.location
        if self.outcome is not None:
            result["Outcome"] = self.outcome
        if self.vs_division is not None:
            result["VsDivision"] = self.vs_division
        if self.vs_conference is not None:
            result["VsConference"] = self.vs_conference

        return result
