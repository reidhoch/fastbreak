"""League game log endpoint."""

from dataclasses import dataclass
from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.league_game_log import LeagueGameLogResponse


@dataclass(frozen=True)
class LeagueGameLog(Endpoint[LeagueGameLogResponse]):
    """Browse and sort game logs across the league.

    Returns game-level box scores sorted by a specified stat, useful for
    finding league-wide extremes (highest/lowest scoring games, etc.).

    Args:
        league_id: League identifier ("00" for NBA)
        season: Season in YYYY-YY format (e.g., "2024-25")
        season_type: Type of season ("Regular Season", "Playoffs", etc.)
        player_or_team: Log type - "P" for player games, "T" for team games
        counter: Number of results to return
        sorter: Stat field to sort by (e.g., "PTS", "REB", "AST")
        direction: Sort direction ("ASC" or "DESC")
        date_from: Filter games from date (MM/DD/YYYY)
        date_to: Filter games to date (MM/DD/YYYY)

    """

    path: ClassVar[str] = "leaguegamelog"
    response_model: ClassVar[type[LeagueGameLogResponse]] = LeagueGameLogResponse

    # Required parameters
    league_id: str = "00"
    season: str = "2024-25"
    season_type: str = "Regular Season"
    player_or_team: str = "T"

    # Sorting and pagination
    counter: int = 1000
    sorter: str = "PTS"
    direction: str = "DESC"

    # Optional date filters
    date_from: str | None = None
    date_to: str | None = None

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        result: dict[str, str] = {
            "LeagueID": self.league_id,
            "Season": self.season,
            "SeasonType": self.season_type,
            "PlayerOrTeam": self.player_or_team,
            "Counter": str(self.counter),
            "Sorter": self.sorter,
            "Direction": self.direction,
        }

        if self.date_from is not None:
            result["DateFrom"] = self.date_from
        if self.date_to is not None:
            result["DateTo"] = self.date_to

        return result
