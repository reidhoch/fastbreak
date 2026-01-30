"""Endpoint for fetching league-wide player tracking statistics."""

from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.league_dash_pt_stats import LeagueDashPtStatsResponse
from fastbreak.types import (
    Conference,
    Date,
    Division,
    LeagueID,
    Location,
    Outcome,
    Period,
    PerMode,
    PlayerExperience,
    PlayerOrTeam,
    PlayerPosition,
    PtMeasureType,
    Season,
    SeasonType,
    StarterBench,
)


class LeagueDashPtStats(Endpoint[LeagueDashPtStatsResponse]):
    """Fetch league-wide player tracking statistics.

    Returns player tracking stats for teams or players across the league.
    The specific stats returned depend on the PtMeasureType parameter.

    Args:
        pt_measure_type: Type of player tracking stat to fetch:
            - "Drives": Drive statistics (drives, drive FG%, drive points, etc.)
            - "Defense": Defensive stats
            - "CatchShoot": Catch and shoot stats
            - "Passing": Passing stats
            - "Possessions": Possession stats
            - "PullUpShot": Pull-up shooting stats
            - "Rebounding": Rebounding stats
            - "Efficiency": Efficiency stats
            - "SpeedDistance": Speed and distance tracking
            - "ElbowTouch": Elbow touch stats
            - "PostTouch": Post touch stats
            - "PaintTouch": Paint touch stats
        player_or_team: "Player" or "Team" to get individual or team stats
        season: Season in YYYY-YY format (e.g., "2024-25")
        season_type: Type of season ("Regular Season", "Playoffs")
        per_mode: Stat mode ("Totals", "PerGame")
        league_id: League identifier ("00" for NBA)
        team_id: Filter by specific team (0 for all teams)
        month: Filter by month (0 for all)
        period: Filter by period (0 for all)
        opponent_team_id: Filter by opponent (0 for all)
        last_n_games: Filter to last N games (0 for all)
        po_round: Playoff round filter (0 for all)
        outcome: Filter by game outcome ("W", "L")
        location: Filter by game location ("Home", "Road")
        date_from: Filter games from date (MM/DD/YYYY)
        date_to: Filter games to date (MM/DD/YYYY)
        vs_conference: Filter by opponent conference
        vs_division: Filter by opponent division
        game_scope: Game scope filter
        player_experience: Player experience filter
        player_position: Player position filter
        starter_bench: Filter by starter/bench status
        conference: Filter by team conference
        division: Filter by team division

    """

    path: ClassVar[str] = "leaguedashptstats"
    response_model: ClassVar[type[LeagueDashPtStatsResponse]] = (
        LeagueDashPtStatsResponse
    )

    # Core parameters
    team_id: int
    pt_measure_type: PtMeasureType = "Drives"
    player_or_team: PlayerOrTeam = "Team"
    season: Season = "2024-25"
    season_type: SeasonType = "Regular Season"
    per_mode: PerMode = "PerGame"
    league_id: LeagueID = "00"

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
    game_scope: str | None = None
    player_experience: PlayerExperience | None = None
    player_position: PlayerPosition | None = None
    starter_bench: StarterBench | None = None
    conference: Conference | None = None
    division: Division | None = None

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        result: dict[str, str] = {
            "PtMeasureType": self.pt_measure_type,
            "PlayerOrTeam": self.player_or_team,
            "Season": self.season,
            "SeasonType": self.season_type,
            "PerMode": self.per_mode,
            "LeagueID": self.league_id,
            "TeamID": str(self.team_id),
            "Month": str(self.month),
            "Period": str(self.period),
            "OpponentTeamID": str(self.opponent_team_id),
            "LastNGames": str(self.last_n_games),
            "PORound": str(self.po_round),
        }

        # Optional parameters - only include if set
        optional_params = {
            "outcome": "Outcome",
            "location": "Location",
            "date_from": "DateFrom",
            "date_to": "DateTo",
            "vs_conference": "VsConference",
            "vs_division": "VsDivision",
            "game_scope": "GameScope",
            "player_experience": "PlayerExperience",
            "player_position": "PlayerPosition",
            "starter_bench": "StarterBench",
            "conference": "Conference",
            "division": "Division",
        }

        for attr, param_name in optional_params.items():
            value = getattr(self, attr)
            if value is not None:
                result[param_name] = value

        return result
