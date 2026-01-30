"""Endpoint for fetching games a player has participated in."""

from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.cume_stats_player_games import CumeStatsPlayerGamesResponse
from fastbreak.types import (
    Conference,
    Division,
    LeagueID,
    Location,
    Outcome,
    SeasonType,
)


class CumeStatsPlayerGames(Endpoint[CumeStatsPlayerGamesResponse]):
    """Fetch list of games a player has participated in.

    Args:
        league_id: League identifier ("00" for NBA)
        season: Season in YYYY format (e.g., "2025")
        season_type: Type of season ("Regular Season", "Playoffs", "Pre Season")
        player_id: The player's unique identifier
        location: Filter by game location ("Home", "Road")
        outcome: Filter by game outcome ("W", "L")
        vs_team_id: Filter by opponent team ID
        vs_division: Filter by opponent division
        vs_conference: Filter by opponent conference ("East", "West")

    """

    path: ClassVar[str] = "cumestatsplayergames"
    response_model: ClassVar[type[CumeStatsPlayerGamesResponse]] = (
        CumeStatsPlayerGamesResponse
    )

    # Required parameters
    player_id: int
    league_id: LeagueID = "00"
    season: str = "2025"
    season_type: SeasonType = "Regular Season"

    # Optional filters
    location: Location | None = None
    outcome: Outcome | None = None
    vs_team_id: int | None = None
    vs_division: Division | None = None
    vs_conference: Conference | None = None

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        result: dict[str, str] = {
            "LeagueID": self.league_id,
            "Season": self.season,
            "SeasonType": self.season_type,
            "PlayerID": str(self.player_id),
        }

        if self.location is not None:
            result["Location"] = self.location
        if self.outcome is not None:
            result["Outcome"] = self.outcome
        if self.vs_team_id is not None:
            result["VsTeamID"] = str(self.vs_team_id)
        if self.vs_division is not None:
            result["VsDivision"] = self.vs_division
        if self.vs_conference is not None:
            result["VsConference"] = self.vs_conference

        return result
