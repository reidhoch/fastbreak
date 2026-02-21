"""Endpoint for fetching league lineup visualization data."""

from typing import ClassVar

from pydantic import Field

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.league_lineup_viz import LeagueLineupVizResponse
from fastbreak.types import (
    Conference,
    Date,
    Division,
    GameSegment,
    LeagueID,
    Location,
    MeasureType,
    Outcome,
    PerMode,
    Season,
    SeasonSegment,
    SeasonType,
    ShotClockRange,
    YesNo,
)
from fastbreak.utils import get_season_from_date


class LeagueLineupViz(Endpoint[LeagueLineupVizResponse]):
    """Fetch lineup visualization statistics for player combinations.

    Returns offensive/defensive ratings, pace, and shot distribution
    for lineups across the league.

    Args:
        season: Season in YYYY-YY format (e.g., "2024-25")
        season_type: Type of season ("Regular Season", "Playoffs")
        per_mode: Stat aggregation mode ("Totals", "PerGame", "Per100Possessions")
        measure_type: Type of stats ("Base", "Advanced", "Misc", "Scoring")
        group_quantity: Number of players in lineup (2-5)
        minutes_min: Minimum minutes played filter
        league_id: League identifier ("00" for NBA)
        team_id: Filter by specific team (0 for all)
        pace_adjust: Pace-adjusted stats ("Y", "N")
        plus_minus: Plus/minus stats ("Y", "N")
        rank: Include rankings ("Y", "N")

    """

    path: ClassVar[str] = "leaguelineupviz"
    response_model: ClassVar[type[LeagueLineupVizResponse]] = LeagueLineupVizResponse

    team_id: int
    season: Season = Field(default_factory=get_season_from_date)
    season_type: SeasonType = "Regular Season"
    per_mode: PerMode = "Totals"
    measure_type: MeasureType = "Base"
    group_quantity: int = 5
    minutes_min: int = 10
    league_id: LeagueID = "00"
    pace_adjust: YesNo = "N"
    plus_minus: YesNo = "N"
    rank: YesNo = "N"
    conference: Conference | None = None
    division: Division | None = None
    game_segment: GameSegment | None = None
    last_n_games: int = 0
    location: Location | None = None
    month: int = 0
    opponent_team_id: int = 0
    outcome: Outcome | None = None
    po_round: int = 0
    period: int = 0
    season_segment: SeasonSegment | None = None
    shot_clock_range: ShotClockRange | None = None
    vs_conference: Conference | None = None
    vs_division: Division | None = None
    date_from: Date | None = None
    date_to: Date | None = None

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {
            "Season": self.season,
            "SeasonType": self.season_type,
            "PerMode": self.per_mode,
            "MeasureType": self.measure_type,
            "GroupQuantity": str(self.group_quantity),
            "MinutesMin": str(self.minutes_min),
            "LeagueID": self.league_id,
            "TeamID": str(self.team_id),
            "PaceAdjust": self.pace_adjust,
            "PlusMinus": self.plus_minus,
            "Rank": self.rank,
            "Conference": self.conference or "",
            "Division": self.division or "",
            "GameSegment": self.game_segment or "",
            "LastNGames": str(self.last_n_games),
            "Location": self.location or "",
            "Month": str(self.month),
            "OpponentTeamID": str(self.opponent_team_id),
            "Outcome": self.outcome or "",
            "PORound": str(self.po_round),
            "Period": str(self.period),
            "SeasonSegment": self.season_segment or "",
            "ShotClockRange": self.shot_clock_range or "",
            "VsConference": self.vs_conference or "",
            "VsDivision": self.vs_division or "",
            "DateFrom": self.date_from or "",
            "DateTo": self.date_to or "",
        }
