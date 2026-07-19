"""Endpoint for fetching league-wide player shot location statistics."""

from typing import ClassVar

from pydantic import Field

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.league_dash_player_shot_locations import (
    LeagueDashPlayerShotLocationsResponse,
)
from fastbreak.seasons import get_season_from_date
from fastbreak.types import (
    Conference,
    Date,
    DistanceRange,
    Division,
    GameSegment,
    LeagueID,
    Location,
    MeasureType,
    Outcome,
    Period,
    PerMode,
    Season,
    SeasonSegment,
    SeasonType,
    YesNo,
)


class LeagueDashPlayerShotLocations(Endpoint[LeagueDashPlayerShotLocationsResponse]):
    """Fetch league-wide player shot statistics by zone/distance.

    The player-level counterpart to :class:`LeagueDashTeamShotLocations`.
    Defaults to the ``By Zone`` breakdown (Restricted Area, In The Paint
    (Non-RA), Mid-Range, corner 3s, Above the Break 3, Backcourt) — the
    per-player complement to :func:`fastbreak.shots.zone_breakdown` and the
    standard source for cross-league shot-profile comparisons.

    Args:
        season: Season in YYYY-YY format (e.g., "2025-26")
        season_type: Type of season ("Regular Season", "Playoffs")
        per_mode: Stat mode ("Totals", "PerGame")
        measure_type: "Base" for the player's own shots, "Opponent" for shots
            allowed
        distance_range: Shot grouping ("By Zone", "5ft Range", "8ft Range").
            The model parses the ``By Zone`` layout.
        league_id: League identifier ("00" for NBA)
        team_id: Filter by specific team (0 for all)
        month: Filter by month (0 for all)
        period: Filter by period (0 for all)
        opponent_team_id: Filter by opponent (0 for all)
        last_n_games: Filter to last N games (0 for all)
        po_round: Playoff round filter (0 for all)
        pace_adjust / plus_minus / rank: NBA dashboard flags ("Y"/"N")
        outcome, location, date_from, date_to, vs_conference, vs_division,
        game_segment, conference, division, season_segment: optional filters

    Example:
        >>> async with NBAClient() as client:
        ...     locs = await client.get(
        ...         LeagueDashPlayerShotLocations(season="2025-26")
        ...     )
        ...     for p in locs.players[:5]:
        ...         ra = p.restricted_area
        ...         print(f"{p.player_name}: {ra.fgm}/{ra.fga} at rim")

    """

    path: ClassVar[str] = "leaguedashplayershotlocations"
    response_model: ClassVar[type[LeagueDashPlayerShotLocationsResponse]] = (
        LeagueDashPlayerShotLocationsResponse
    )

    # Core parameters
    team_id: int = 0
    season: Season = Field(default_factory=get_season_from_date)
    season_type: SeasonType = "Regular Season"
    per_mode: PerMode = "PerGame"
    measure_type: MeasureType = "Base"
    distance_range: DistanceRange = "By Zone"
    league_id: LeagueID = "00"
    pace_adjust: YesNo = "N"
    plus_minus: YesNo = "N"
    rank: YesNo = "N"

    # Numeric filters with defaults
    month: int = 0
    period: Period = 0
    opponent_team_id: int = 0
    last_n_games: int = 0
    po_round: int = 0

    # Optional filters
    outcome: Outcome | None = None
    location: Location | None = None
    date_from: Date | None = None
    date_to: Date | None = None
    vs_conference: Conference | None = None
    vs_division: Division | None = None
    game_segment: GameSegment | None = None
    conference: Conference | None = None
    division: Division | None = None
    season_segment: SeasonSegment | None = None

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        result: dict[str, str] = {
            "Season": self.season,
            "SeasonType": self.season_type,
            "PerMode": self.per_mode,
            "MeasureType": self.measure_type,
            "DistanceRange": self.distance_range,
            "LeagueID": self.league_id,
            "TeamID": str(self.team_id),
            "PaceAdjust": self.pace_adjust,
            "PlusMinus": self.plus_minus,
            "Rank": self.rank,
            "Month": str(self.month),
            "Period": str(self.period),
            "OpponentTeamID": str(self.opponent_team_id),
            "LastNGames": str(self.last_n_games),
            "PORound": str(self.po_round),
        }

        optional_params = {
            "outcome": "Outcome",
            "location": "Location",
            "date_from": "DateFrom",
            "date_to": "DateTo",
            "vs_conference": "VsConference",
            "vs_division": "VsDivision",
            "game_segment": "GameSegment",
            "conference": "Conference",
            "division": "Division",
            "season_segment": "SeasonSegment",
        }
        for attr, param_name in optional_params.items():
            value = getattr(self, attr)
            if value is not None:
                result[param_name] = value

        return result
