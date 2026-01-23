"""League game finder endpoint."""

from dataclasses import dataclass
from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.league_game_finder import LeagueGameFinderResponse


@dataclass(frozen=True)
class LeagueGameFinder(Endpoint[LeagueGameFinderResponse]):
    """Search for games by team, player, date range, or stat thresholds.

    A powerful search endpoint that returns game-level box scores matching
    the specified criteria.

    Args:
        player_or_team: Search mode - "P" for player games, "T" for team games
        league_id: League identifier ("00" for NBA)
        season: Season in YYYY-YY format (e.g., "2024-25")
        season_type: Type of season ("Regular Season", "Playoffs", etc.)
        team_id: Filter by team ID
        player_id: Filter by player ID (when player_or_team="P")
        vs_team_id: Filter by opponent team ID
        date_from: Filter games from date (MM/DD/YYYY)
        date_to: Filter games to date (MM/DD/YYYY)
        outcome: Filter by game outcome ("W" or "L")
        location: Filter by game location ("Home" or "Road")
        gt_pts: Filter games with points greater than this value
        gt_reb: Filter games with rebounds greater than this value
        gt_ast: Filter games with assists greater than this value

    """

    path: ClassVar[str] = "leaguegamefinder"
    response_model: ClassVar[type[LeagueGameFinderResponse]] = LeagueGameFinderResponse

    # Required parameter
    player_or_team: str = "T"

    # Common filters
    league_id: str | None = None
    season: str | None = None
    season_type: str | None = None
    team_id: str | None = None
    player_id: str | None = None
    vs_team_id: str | None = None
    date_from: str | None = None
    date_to: str | None = None
    outcome: str | None = None
    location: str | None = None

    # Stat threshold filters (greater than)
    gt_pts: str | None = None
    gt_reb: str | None = None
    gt_ast: str | None = None
    gt_stl: str | None = None
    gt_blk: str | None = None

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        result: dict[str, str] = {
            "PlayerOrTeam": self.player_or_team,
        }

        optional_params = {
            "league_id": "LeagueID",
            "season": "Season",
            "season_type": "SeasonType",
            "team_id": "TeamID",
            "player_id": "PlayerID",
            "vs_team_id": "VsTeamID",
            "date_from": "DateFrom",
            "date_to": "DateTo",
            "outcome": "Outcome",
            "location": "Location",
            "gt_pts": "GtPts",
            "gt_reb": "GtReb",
            "gt_ast": "GtAst",
            "gt_stl": "GtStl",
            "gt_blk": "GtBlk",
        }

        for attr, param_name in optional_params.items():
            value = getattr(self, attr)
            if value is not None:
                result[param_name] = value

        return result
