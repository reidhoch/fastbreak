from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import ClassVar

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

    league_id: str = "00"
    season_year: str = "2024-25"

    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        return {
            "LeagueID": self.league_id,
            "SeasonYear": self.season_year,
        }
