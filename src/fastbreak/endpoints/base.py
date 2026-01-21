from abc import ABC, abstractmethod
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
