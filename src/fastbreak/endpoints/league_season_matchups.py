"""League season matchups endpoint."""

from dataclasses import dataclass
from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.league_season_matchups import LeagueSeasonMatchupsResponse


@dataclass(frozen=True)
class LeagueSeasonMatchups(Endpoint[LeagueSeasonMatchupsResponse]):
    """Fetch player-vs-player matchup statistics for the season.

    Args:
        league_id: League identifier ("00" for NBA)
        season: Season in YYYY-YY format (e.g., "2024-25")
        season_type: Type of season ("Regular Season", "Playoffs")
        per_mode: Stat aggregation mode ("PerGame", "Totals")
        off_team_id: Filter by offensive team ID (optional)
        def_team_id: Filter by defensive team ID (optional)
        off_player_id: Filter by offensive player ID (optional)
        def_player_id: Filter by defensive player ID (optional)

    """

    path: ClassVar[str] = "leagueseasonmatchups"
    response_model: ClassVar[type[LeagueSeasonMatchupsResponse]] = (
        LeagueSeasonMatchupsResponse
    )

    league_id: str = "00"
    season: str = "2024-25"
    season_type: str = "Regular Season"
    per_mode: str = "PerGame"
    off_team_id: str | None = None
    def_team_id: str | None = None
    off_player_id: str | None = None
    def_player_id: str | None = None

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        result = {
            "LeagueID": self.league_id,
            "Season": self.season,
            "SeasonType": self.season_type,
            "PerMode": self.per_mode,
        }
        if self.off_team_id is not None:
            result["OffTeamID"] = self.off_team_id
        if self.def_team_id is not None:
            result["DefTeamID"] = self.def_team_id
        if self.off_player_id is not None:
            result["OffPlayerID"] = self.off_player_id
        if self.def_player_id is not None:
            result["DefPlayerID"] = self.def_player_id
        return result
