"""Endpoint for fetching Synergy play type statistics."""

from dataclasses import dataclass
from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.synergy_playtypes import SynergyPlaytypesResponse


@dataclass(frozen=True)
class SynergyPlaytypes(Endpoint[SynergyPlaytypesResponse]):
    """Fetch Synergy play type statistics for players or teams.

    Returns offensive or defensive efficiency metrics broken down by play type
    (Isolation, Transition, Post Up, Pick & Roll, etc.).

    Args:
        league_id: League identifier ("00" for NBA)
        season_year: Season in YYYY-YY format (e.g., "2024-25")
        season_type: Type of season ("Regular Season", "Playoffs", "Pre Season")
        per_mode: Stat aggregation mode ("PerGame", "Totals")
        player_or_team: Whether to return player or team stats ("P", "T")
        play_type: Filter by play type ("Isolation", "Transition", "Post Up",
                   "PRBallHandler", "PRRollman", "Spotup", "Handoff", "Cut",
                   "OffScreen", "OffRebound", "Misc")
        type_grouping: Filter by offensive or defensive ("offensive", "defensive")

    """

    path: ClassVar[str] = "synergyplaytypes"
    response_model: ClassVar[type[SynergyPlaytypesResponse]] = SynergyPlaytypesResponse

    league_id: str = "00"
    season_year: str = "2024-25"
    season_type: str = "Regular Season"
    per_mode: str = "PerGame"
    player_or_team: str = "P"

    # Optional filters
    play_type: str | None = None
    type_grouping: str | None = None

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        result: dict[str, str] = {
            "LeagueID": self.league_id,
            "SeasonYear": self.season_year,
            "SeasonType": self.season_type,
            "PerMode": self.per_mode,
            "PlayerOrTeam": self.player_or_team,
        }

        if self.play_type is not None:
            result["PlayType"] = self.play_type
        if self.type_grouping is not None:
            result["TypeGrouping"] = self.type_grouping

        return result
