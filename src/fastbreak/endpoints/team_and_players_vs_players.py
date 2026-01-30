"""Endpoint for comparing teams and players against specific opponents."""

from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.team_and_players_vs_players import (
    TeamAndPlayersVsPlayersResponse,
)
from fastbreak.types import (
    Conference,
    Date,
    Division,
    GameSegment,
    LeagueID,
    Location,
    MeasureType,
    Outcome,
    Period,
    PerMode,
    Season,
    SeasonType,
    YesNo,
)


class TeamAndPlayersVsPlayers(Endpoint[TeamAndPlayersVsPlayersResponse]):
    """Compare a team and its players against a specific opponent team and players.

    Returns detailed comparison stats showing how a team and its individual
    players perform when matched up against specific opponents.

    Args:
        league_id: League identifier ("00" for NBA)
        team_id: ID of the team to analyze
        vs_team_id: ID of the opponent team
        season: Season in YYYY-YY format (e.g., "2024-25")
        season_type: Type of season ("Regular Season", "Playoffs", "Pre Season")
        per_mode: Stat mode ("Totals", "PerGame", "Per36", etc.)
        measure_type: Measure type ("Base", "Advanced", "Misc", etc.)
        pace_adjust: Whether to pace adjust ("Y", "N")
        plus_minus: Whether to include plus/minus ("Y", "N")
        rank: Whether to include rank ("Y", "N")
        player_id1-5: Filter by specific player IDs from team
        vs_player_id1-5: Filter by specific player IDs from opponent
        conference: Filter by conference ("East", "West")
        division: Filter by division
        game_segment: Filter by game segment ("First Half", "Second Half", "Overtime")
        last_n_games: Filter to last N games
        location: Filter by game location ("Home", "Road")
        month: Filter by month (1-12)
        opponent_team_id: Additional opponent filter
        outcome: Filter by game outcome ("W", "L")
        period: Filter by period (0 for all)
        date_from: Filter games from date (MM/DD/YYYY)
        date_to: Filter games to date (MM/DD/YYYY)
        vs_conference: Filter by opponent conference ("East", "West")
        vs_division: Filter by opponent division

    """

    path: ClassVar[str] = "teamandplayersvsplayers"
    response_model: ClassVar[type[TeamAndPlayersVsPlayersResponse]] = (
        TeamAndPlayersVsPlayersResponse
    )

    # Required parameters
    team_id: int
    vs_team_id: int
    league_id: LeagueID = "00"
    season: Season = "2024-25"
    season_type: SeasonType = "Regular Season"
    per_mode: PerMode = "PerGame"
    measure_type: MeasureType = "Base"
    pace_adjust: YesNo = "N"
    plus_minus: YesNo = "N"
    rank: YesNo = "N"

    # Player filters (0 means no filter)
    player_id1: int = 0
    player_id2: int = 0
    player_id3: int = 0
    player_id4: int = 0
    player_id5: int = 0
    vs_player_id1: int = 0
    vs_player_id2: int = 0
    vs_player_id3: int = 0
    vs_player_id4: int = 0
    vs_player_id5: int = 0

    # Optional filters
    conference: Conference | None = None
    division: Division | None = None
    game_segment: GameSegment | None = None
    last_n_games: int = 0
    location: Location | None = None
    month: int = 0
    opponent_team_id: int = 0
    outcome: Outcome | None = None
    period: Period = 0
    date_from: Date | None = None
    date_to: Date | None = None
    vs_conference: Conference | None = None
    vs_division: Division | None = None

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        result: dict[str, str] = {
            "LeagueID": self.league_id,
            "TeamID": str(self.team_id),
            "VsTeamID": str(self.vs_team_id),
            "Season": self.season,
            "SeasonType": self.season_type,
            "PerMode": self.per_mode,
            "MeasureType": self.measure_type,
            "PaceAdjust": self.pace_adjust,
            "PlusMinus": self.plus_minus,
            "Rank": self.rank,
            "PlayerID1": str(self.player_id1),
            "PlayerID2": str(self.player_id2),
            "PlayerID3": str(self.player_id3),
            "PlayerID4": str(self.player_id4),
            "PlayerID5": str(self.player_id5),
            "VsPlayerID1": str(self.vs_player_id1),
            "VsPlayerID2": str(self.vs_player_id2),
            "VsPlayerID3": str(self.vs_player_id3),
            "VsPlayerID4": str(self.vs_player_id4),
            "VsPlayerID5": str(self.vs_player_id5),
            "LastNGames": str(self.last_n_games),
            "Month": str(self.month),
            "OpponentTeamID": str(self.opponent_team_id),
            "Period": str(self.period),
        }

        # Map of optional attributes to API parameter names
        optional_params = {
            "conference": "Conference",
            "division": "Division",
            "game_segment": "GameSegment",
            "location": "Location",
            "outcome": "Outcome",
            "date_from": "DateFrom",
            "date_to": "DateTo",
            "vs_conference": "VsConference",
            "vs_division": "VsDivision",
        }

        for attr, param_name in optional_params.items():
            value = getattr(self, attr)
            if value is not None:
                result[param_name] = value
            else:
                result[param_name] = ""

        return result
