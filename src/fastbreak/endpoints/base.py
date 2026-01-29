from abc import ABC, abstractmethod
from dataclasses import dataclass
from inspect import isabstract
from typing import Any, ClassVar

from pydantic import BaseModel

from fastbreak.models import JSON


class Endpoint[T: BaseModel](ABC):
    """Base class for NBA API endpoints.

    Subclasses should be decorated with @dataclass and define:
    - path: ClassVar[str] - The URL path segment (e.g., "gravityleaders")
    - response_model: ClassVar - The Pydantic model to parse the response
    - Instance fields for query parameters
    - params(): Method returning the query parameters dict
    """

    path: ClassVar[str]
    response_model: ClassVar[type[T]]
    _is_base_endpoint: ClassVar[bool] = False

    def __init_subclass__(cls, **kwargs: Any) -> None:  # noqa: ANN401
        """Validate that concrete subclasses define required ClassVars."""
        super().__init_subclass__(**kwargs)
        # Skip validation for abstract or intermediate base classes
        if isabstract(cls) or cls.__dict__.get("_is_base_endpoint", False):
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


@dataclass(frozen=True)
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


@dataclass(frozen=True)
class DraftCombineEndpoint[T: BaseModel](Endpoint[T]):
    """Base class for draft combine endpoints with common parameters.

    This covers all draft combine endpoints (stats, drill results, anthro, shooting).
    Subclasses only need to define path and response_model.
    """

    _is_base_endpoint: ClassVar[bool] = True

    league_id: str = "00"
    season_year: str = "2024-25"

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {
            "LeagueID": self.league_id,
            "SeasonYear": self.season_year,
        }
