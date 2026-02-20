from pydantic import BaseModel

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin


class Meta(PandasMixin, PolarsMixin, BaseModel):
    """Metadata about an API request.

    This is a common structure returned by v3-style NBA Stats API endpoints
    containing request diagnostics.
    """

    version: int | None = None
    request: str | None = None
    time: str | None = None
