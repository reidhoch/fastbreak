"""League dash pt team defend endpoint."""

from typing import ClassVar, Literal

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.league_dash_pt_team_defend import LeagueDashPtTeamDefendResponse
from fastbreak.types import LeagueID, PerMode, Season, SeasonType

DefenseCategory = Literal[
    "Overall",
    "3 Pointers",
    "2 Pointers",
    "Less Than 6Ft",
    "Less Than 10Ft",
    "Greater Than 15Ft",
]


class LeagueDashPtTeamDefend(Endpoint[LeagueDashPtTeamDefendResponse]):
    """Fetch team defensive tracking statistics.

    Returns how well teams defend shots by category (overall, 3-pointers,
    rim protection, etc.). Shows opponent FG% vs normal FG% to measure
    defensive impact.

    Negative PCT_PLUSMINUS indicates better defense (opponents shoot
    worse than their normal percentage).

    Args:
        league_id: League identifier ("00" for NBA)
        season: Season in YYYY-YY format (e.g., "2024-25")
        season_type: Type of season (e.g., "Regular Season", "Playoffs")
        per_mode: Stats mode ("Totals", "PerGame", etc.)
        defense_category: Type of shots to analyze

    Example:
        >>> async with NBAClient() as client:
        ...     defense = await client.get(LeagueDashPtTeamDefend(
        ...         season="2024-25",
        ...         defense_category="3 Pointers"
        ...     ))
        ...     for team in defense.teams[:5]:
        ...         print(f"{team.team_abbreviation}: {team.pct_plusminus:+.1%} vs normal")

    """

    path: ClassVar[str] = "leaguedashptteamdefend"
    response_model: ClassVar[type[LeagueDashPtTeamDefendResponse]] = (
        LeagueDashPtTeamDefendResponse
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
