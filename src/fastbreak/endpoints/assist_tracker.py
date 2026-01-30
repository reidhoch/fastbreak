"""Assist tracker endpoint."""

from typing import ClassVar

from fastbreak.endpoints.base import Endpoint
from fastbreak.models.assist_tracker import AssistTrackerResponse
from fastbreak.types import (
    Conference,
    Date,
    Division,
    LeagueID,
    Location,
    Outcome,
    PerMode,
    PlayerExperience,
    PlayerPosition,
    Season,
    SeasonSegment,
    SeasonType,
    StarterBench,
)


class AssistTracker(Endpoint[AssistTrackerResponse]):
    """Fetch aggregate assist count with optional filters.

    Args:
        league_id: League identifier ("00" for NBA)
        season: Season in YYYY-YY format (e.g., "2024-25")
        season_type: Type of season ("Regular Season", "Playoffs", "Pre Season")
        per_mode: Stat mode ("Totals", "PerGame", "Per36", etc.)
        po_round: Playoff round filter
        outcome: Filter by game outcome ("W", "L")
        location: Filter by game location ("Home", "Road")
        month: Filter by month (1-12)
        season_segment: Filter by season segment ("Pre All-Star", "Post All-Star")
        date_from: Filter games from date (MM/DD/YYYY)
        date_to: Filter games to date (MM/DD/YYYY)
        opponent_team_id: Filter by opponent team ID
        vs_conference: Filter by opponent conference ("East", "West")
        vs_division: Filter by opponent division
        team_id: Filter by team ID
        conference: Filter by conference ("East", "West")
        division: Filter by division
        last_n_games: Filter to last N games
        game_scope: Filter by game scope
        player_experience: Filter by experience ("Rookie", "Sophomore", "Veteran")
        player_position: Filter by position ("G", "F", "C", "G-F", "F-C", etc.)
        starter_bench: Filter by starter/bench ("Starters", "Bench")
        draft_year: Filter by draft year
        draft_pick: Filter by draft pick
        college: Filter by college
        country: Filter by country
        height: Filter by height
        weight: Filter by weight

    """

    path: ClassVar[str] = "assisttracker"
    response_model: ClassVar[type[AssistTrackerResponse]] = AssistTrackerResponse

    # Required parameters
    league_id: LeagueID = "00"
    season: Season = "2024-25"
    season_type: SeasonType = "Regular Season"
    per_mode: PerMode = "Totals"

    # Optional filters
    po_round: str | None = None
    outcome: Outcome | None = None
    location: Location | None = None
    month: str | None = None
    season_segment: SeasonSegment | None = None
    date_from: Date | None = None
    date_to: Date | None = None
    opponent_team_id: str | None = None
    vs_conference: Conference | None = None
    vs_division: Division | None = None
    team_id: str | None = None
    conference: Conference | None = None
    division: Division | None = None
    last_n_games: str | None = None
    game_scope: str | None = None
    player_experience: PlayerExperience | None = None
    player_position: PlayerPosition | None = None
    starter_bench: StarterBench | None = None
    draft_year: str | None = None
    draft_pick: str | None = None
    college: str | None = None
    country: str | None = None
    height: str | None = None
    weight: str | None = None

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        result: dict[str, str] = {
            "LeagueID": self.league_id,
            "Season": self.season,
            "SeasonType": self.season_type,
            "PerMode": self.per_mode,
        }

        # Map of optional attributes to API parameter names
        optional_params = {
            "po_round": "PORound",
            "outcome": "Outcome",
            "location": "Location",
            "month": "Month",
            "season_segment": "SeasonSegment",
            "date_from": "DateFrom",
            "date_to": "DateTo",
            "opponent_team_id": "OpponentTeamID",
            "vs_conference": "VsConference",
            "vs_division": "VsDivision",
            "team_id": "TeamID",
            "conference": "Conference",
            "division": "Division",
            "last_n_games": "LastNGames",
            "game_scope": "GameScope",
            "player_experience": "PlayerExperience",
            "player_position": "PlayerPosition",
            "starter_bench": "StarterBench",
            "draft_year": "DraftYear",
            "draft_pick": "DraftPick",
            "college": "College",
            "country": "Country",
            "height": "Height",
            "weight": "Weight",
        }

        for attr, param_name in optional_params.items():
            value = getattr(self, attr)
            if value is not None:
                result[param_name] = value

        return result
