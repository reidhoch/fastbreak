"""League dash pt defend endpoint (player defensive tracking)."""

from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.endpoints.league_dash_pt_team_defend import DefenseCategory
from fastbreak.models.league_dash_pt_defend import LeagueDashPtDefendResponse
from fastbreak.types import LeagueID, PerMode, Season, SeasonType


class LeagueDashPtDefend(Endpoint[LeagueDashPtDefendResponse]):
    """Fetch player defensive tracking statistics.

    Returns how well each defender holds opponents below their normal FG% by
    shot category (overall, 3-pointers, rim protection, etc.) — the league-wide
    per-player leaderboard for rim protectors and perimeter defenders.

    Negative ``pct_plusminus`` indicates better defense (opponents shoot worse
    than their normal percentage).

    This is the player-level counterpart to :class:`LeagueDashPtTeamDefend`.

    Args:
        league_id: League identifier ("00" for NBA)
        season: Season in YYYY-YY format (e.g., "2025-26")
        season_type: Type of season (e.g., "Regular Season", "Playoffs")
        per_mode: Stats mode ("Totals", "PerGame", etc.)
        defense_category: Type of shots to analyze (required by the API)

    Example:
        >>> async with NBAClient() as client:
        ...     defense = await client.get(LeagueDashPtDefend(
        ...         season="2025-26",
        ...         defense_category="3 Pointers",
        ...     ))
        ...     for player in defense.players[:5]:
        ...         print(f"{player.player_name}: {player.pct_plusminus:+.1%} vs normal")

    """

    path: ClassVar[str] = "leaguedashptdefend"
    response_model: ClassVar[type[LeagueDashPtDefendResponse]] = (
        LeagueDashPtDefendResponse
    )

    league_id: LeagueID = "00"
    season: Season | None = None
    season_type: SeasonType = "Regular Season"
    per_mode: PerMode = "Totals"
    defense_category: DefenseCategory = "Overall"

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        result: dict[str, str] = {
            "LeagueID": self.league_id,
            "SeasonType": self.season_type,
            "PerMode": self.per_mode,
            "DefenseCategory": self.defense_category,
        }
        if self.season is not None:
            result["Season"] = self.season
        return result
