"""Leaders tiles endpoint."""

from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.leaders_tiles import LeadersTilesResponse
from fastbreak.types import LeagueID, PlayerOrTeam, Season, SeasonType


class LeadersTiles(Endpoint[LeadersTilesResponse]):
    """Fetch leader tiles with historical comparisons.

    Returns current stat leaders along with all-time season high records
    and last season's leader for comparison. Designed for dashboard tiles
    that show how current leaders compare to historical records.

    Args:
        stat: Stat abbreviation to rank by ("PTS", "REB", "AST", etc.)
        league_id: League identifier ("00" for NBA)
        season: Season in YYYY-YY format (e.g., "2024-25")
        season_type: Type of season (e.g., "Regular Season", "Playoffs")
        player_or_team: "Player" or "Team" scope
        scope: Scope filter ("S" for season)

    Example:
        >>> async with NBAClient() as client:
        ...     tiles = await client.get(LeadersTiles(
        ...         stat="PTS",
        ...         season="2024-25"
        ...     ))
        ...     print(f"Current leader: {tiles.leaders[0].player}")
        ...     if tiles.all_time_season_high:
        ...         record = tiles.all_time_season_high[0]
        ...         print(f"All-time record: {record.player_name} ({record.pts} in {record.season_year})")

    """

    path: ClassVar[str] = "leaderstiles"
    response_model: ClassVar[type[LeadersTilesResponse]] = LeadersTilesResponse

    stat: str = "PTS"
    league_id: LeagueID = "00"
    season: Season | None = None
    season_type: SeasonType = "Regular Season"
    player_or_team: PlayerOrTeam = "Player"
    scope: str = "S"

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        result: dict[str, str] = {
            "Stat": self.stat,
            "LeagueID": self.league_id,
            "SeasonType": self.season_type,
            "PlayerOrTeam": self.player_or_team,
            "Scope": self.scope,
        }
        if self.season is not None:
            result["Season"] = self.season
        return result
