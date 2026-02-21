from abc import abstractmethod
from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict, Field

from fastbreak.models import JSON
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
    SeasonSegment,
    SeasonType,
    ShotClockRange,
    YesNo,
)
from fastbreak.utils import get_season_from_date


class Endpoint[T: BaseModel](BaseModel):
    """Base class for NBA API endpoints.

    Subclasses should define:
    - path: ClassVar[str] - The URL path segment (e.g., "gravityleaders")
    - response_model: ClassVar - The Pydantic model to parse the response
    - Instance fields for query parameters
    - params(): Method returning the query parameters dict

    All endpoints are frozen (immutable) and validate parameters at runtime.
    """

    model_config = ConfigDict(frozen=True)

    path: ClassVar[str]
    response_model: ClassVar[type[T]]
    _is_base_endpoint: ClassVar[bool] = False

    def __init_subclass__(cls, **kwargs: Any) -> None:  # noqa: ANN401
        """Validate that concrete subclasses define required ClassVars."""
        super().__init_subclass__(**kwargs)
        # Skip validation for intermediate base classes
        if cls.__dict__.get("_is_base_endpoint", False):
            return
        # Skip validation for Pydantic's internal generic submodels (names contain "[")
        if "[" in cls.__name__:
            return
        # Check class hierarchy for actual values (not just annotations)
        has_path = any("path" in c.__dict__ for c in cls.__mro__ if c is not Endpoint)
        has_model = any(
            "response_model" in c.__dict__ for c in cls.__mro__ if c is not Endpoint
        )
        if not has_path:
            msg = f"{cls.__name__} must define 'path' ClassVar"
            raise TypeError(msg)
        if not has_model:
            msg = f"{cls.__name__} must define 'response_model' ClassVar"
            raise TypeError(msg)

    @abstractmethod
    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        ...

    def parse_response(self, data: JSON) -> T:
        """Parse the API response into the response model."""
        return self.response_model.model_validate(data)


class GameIdEndpoint[T: BaseModel](Endpoint[T]):
    """Base class for endpoints that only require a game_id parameter.

    This covers all box score endpoints and similar single-game queries.
    Subclasses only need to define path and response_model.
    """

    _is_base_endpoint: ClassVar[bool] = True

    game_id: str

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {"GameID": self.game_id}


class DraftCombineEndpoint[T: BaseModel](Endpoint[T]):
    """Base class for draft combine endpoints with common parameters.

    This covers all draft combine endpoints (stats, drill results, anthro, shooting).
    Subclasses only need to define path and response_model.

    Args:
        league_id: League identifier ("00" for NBA)
        season_year: Season in YYYY-YY format (e.g., "2024-25")

    """

    _is_base_endpoint: ClassVar[bool] = True

    league_id: LeagueID = "00"
    season_year: str = Field(default_factory=get_season_from_date)

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {
            "LeagueID": self.league_id,
            "SeasonYear": self.season_year,
        }


class DashboardEndpoint[T: BaseModel](Endpoint[T]):
    """Base class for dashboard endpoints with common parameters.

    This covers player and team dashboard endpoints that share common filtering
    and stat parameters. Subclasses should inherit from PlayerDashboardEndpoint
    or TeamDashboardEndpoint rather than this class directly.
    """

    _is_base_endpoint: ClassVar[bool] = True

    # Common stat parameters
    league_id: LeagueID = "00"
    season: Season = Field(default_factory=get_season_from_date)
    season_type: SeasonType = "Regular Season"
    per_mode: PerMode = "PerGame"
    measure_type: MeasureType = "Base"
    pace_adjust: YesNo = "N"
    plus_minus: YesNo = "N"
    rank: YesNo = "N"

    # Always-sent filters with defaults
    po_round: int = 0
    month: int = 0
    opponent_team_id: int = 0
    period: Period = 0
    last_n_games: int = 0

    # Optional filters
    outcome: Outcome | None = None
    location: Location | None = None
    season_segment: SeasonSegment | None = None
    date_from: Date | None = None
    date_to: Date | None = None
    vs_conference: Conference | None = None
    vs_division: Division | None = None
    game_segment: GameSegment | None = None
    shot_clock_range: ShotClockRange | None = None

    def _base_params(self) -> dict[str, str]:
        """Build common parameters shared by all dashboard endpoints."""
        result: dict[str, str] = {
            "LeagueID": self.league_id,
            "Season": self.season,
            "SeasonType": self.season_type,
            "PerMode": self.per_mode,
            "MeasureType": self.measure_type,
            "PaceAdjust": self.pace_adjust,
            "PlusMinus": self.plus_minus,
            "Rank": self.rank,
            "PORound": str(self.po_round),
            "Month": str(self.month),
            "OpponentTeamID": str(self.opponent_team_id),
            "Period": str(self.period),
            "LastNGames": str(self.last_n_games),
        }

        # Map of optional attributes to API parameter names
        optional_params = {
            "outcome": "Outcome",
            "location": "Location",
            "season_segment": "SeasonSegment",
            "date_from": "DateFrom",
            "date_to": "DateTo",
            "vs_conference": "VsConference",
            "vs_division": "VsDivision",
            "game_segment": "GameSegment",
            "shot_clock_range": "ShotClockRange",
        }

        for attr, param_name in optional_params.items():
            value = getattr(self, attr)
            if value is not None:
                result[param_name] = value

        return result


class PlayerDashboardEndpoint[T: BaseModel](DashboardEndpoint[T]):
    """Base class for player dashboard endpoints.

    Adds player_id and ist_round parameters to the common dashboard parameters.
    Subclasses only need to define path and response_model.

    Args:
        player_id: NBA player ID (required)
        ist_round: In-Season Tournament round filter (optional)

    """

    _is_base_endpoint: ClassVar[bool] = True

    player_id: int
    ist_round: str | None = None

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        result = self._base_params()
        result["PlayerID"] = str(self.player_id)
        if self.ist_round is not None:
            result["ISTRound"] = self.ist_round
        return result


class TeamDashboardEndpoint[T: BaseModel](DashboardEndpoint[T]):
    """Base class for team dashboard endpoints.

    Adds team_id parameter to the common dashboard parameters.
    Subclasses only need to define path and response_model.

    Args:
        team_id: NBA team ID (required)

    """

    _is_base_endpoint: ClassVar[bool] = True

    team_id: int

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        result = self._base_params()
        result["TeamID"] = str(self.team_id)
        return result


class PlayerIdEndpoint[T: BaseModel](Endpoint[T]):
    """Base class for endpoints that only require a player_id parameter.

    This is the simplest player endpoint base class.
    Subclasses only need to define path and response_model.

    Args:
        player_id: NBA player ID (required)

    """

    _is_base_endpoint: ClassVar[bool] = True

    player_id: int

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {"PlayerID": str(self.player_id)}


class SimplePlayerEndpoint[T: BaseModel](PlayerIdEndpoint[T]):
    """Base class for player endpoints with league_id parameter.

    Extends PlayerIdEndpoint with league_id.
    Subclasses only need to define path and response_model.

    Args:
        player_id: NBA player ID (required)
        league_id: League identifier ("00" for NBA)

    """

    _is_base_endpoint: ClassVar[bool] = True

    league_id: LeagueID = "00"

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {
            "PlayerID": str(self.player_id),
            "LeagueID": self.league_id,
        }


class PlayerPerModeEndpoint[T: BaseModel](SimplePlayerEndpoint[T]):
    """Base class for player endpoints with per_mode parameter.

    Extends SimplePlayerEndpoint with per_mode for stat aggregation.
    Subclasses only need to define path and response_model.

    Args:
        player_id: NBA player ID (required)
        league_id: League identifier ("00" for NBA)
        per_mode: Stat aggregation mode ("PerGame", "Per36", "Totals", etc.)

    """

    _is_base_endpoint: ClassVar[bool] = True

    per_mode: PerMode = "PerGame"

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {
            "PlayerID": str(self.player_id),
            "LeagueID": self.league_id,
            "PerMode": self.per_mode,
        }


class PlayerSeasonEndpoint[T: BaseModel](SimplePlayerEndpoint[T]):
    """Base class for player endpoints with season parameters.

    Extends SimplePlayerEndpoint with season and season_type.
    Subclasses only need to define path and response_model.

    Args:
        player_id: NBA player ID (required)
        league_id: League identifier ("00" for NBA)
        season: Season in YYYY-YY format (e.g., "2024-25")
        season_type: Type of season ("Regular Season", "Playoffs", "Pre Season")

    """

    _is_base_endpoint: ClassVar[bool] = True

    season: Season = Field(default_factory=get_season_from_date)
    season_type: SeasonType = "Regular Season"

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {
            "PlayerID": str(self.player_id),
            "LeagueID": self.league_id,
            "Season": self.season,
            "SeasonType": self.season_type,
        }


class TeamSeasonEndpoint[T: BaseModel](Endpoint[T]):
    """Base class for team endpoints with season parameters.

    Subclasses only need to define path and response_model.

    Args:
        team_id: NBA team ID (required)
        season: Season in YYYY-YY format (e.g., "2024-25")
        season_type: Type of season ("Regular Season", "Playoffs", "Pre Season")
        league_id: League identifier ("00" for NBA)

    """

    _is_base_endpoint: ClassVar[bool] = True

    team_id: int
    season: Season = Field(default_factory=get_season_from_date)
    season_type: SeasonType = "Regular Season"
    league_id: LeagueID = "00"

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {
            "TeamID": str(self.team_id),
            "Season": self.season,
            "SeasonType": self.season_type,
            "LeagueID": self.league_id,
        }
