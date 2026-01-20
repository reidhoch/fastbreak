from abc import ABC, abstractmethod

from pydantic import BaseModel

from fastbreak.models import JSON


class Endpoint[T: BaseModel](ABC):
    """Base class for NBA API endpoints.

    Each endpoint defines:
    - path: The URL path segment (e.g., "gravityleaders")
    - response_model: The Pydantic model to parse the response
    - params(): Method returning the query parameters
    """

    path: str
    response_model: type[T]

    @abstractmethod
    def params(self) -> dict[str, str]:
        """Return the query parameters for this endpoint."""
        ...

    def parse_response(self, data: JSON) -> T:
        """Parse the API response into the response model."""
        return self.response_model.model_validate(data)


class GameEndpoint[T: BaseModel](Endpoint[T]):
    """Base class for endpoints that accept a game_id parameter.

    This simplifies endpoints that only need a game ID by providing
    a common __init__ and params implementation.
    """

    def __init__(self, game_id: str) -> None:
        self.game_id = game_id

    def params(self) -> dict[str, str]:
        return {"GameID": self.game_id}
