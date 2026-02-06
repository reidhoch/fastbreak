"""Base class for API response models."""

import logging
from typing import Any, Self

from pydantic import BaseModel, ConfigDict, model_validator

logger = logging.getLogger(__name__)


class FrozenResponse(BaseModel):
    """Base class for API response models.

    Provides:
    - frozen=True: Prevents accidental mutation of response data
    - extra='ignore': Ignores extra fields from API (forward-compatible)
    - Warnings: Logs when unknown fields are received (detect API changes)

    For strict validation in tests, use the `strict()` classmethod:
        StrictModel = MyResponse.strict()
        StrictModel.model_validate(data)  # Raises on extra fields
    """

    model_config = ConfigDict(frozen=True, extra="ignore")

    @model_validator(mode="before")
    @classmethod
    def _warn_on_extra_fields(cls, data: dict[str, Any]) -> dict[str, Any]:
        """Log a warning if the API returns fields we don't have defined."""
        if not isinstance(data, dict):
            return data
        model_fields = set(cls.model_fields.keys())
        extra_fields = set(data.keys()) - model_fields
        if extra_fields:
            logger.warning(
                "%s received unknown fields: %s. "
                "Consider updating the model to capture new API data.",
                cls.__name__,
                sorted(extra_fields),
            )
        return data

    @classmethod
    def strict(cls) -> type[Self]:
        """Return a strict version of this model that rejects extra fields.

        Use in tests to detect API schema changes:
            def test_api_schema():
                StrictResponse = MyResponse.strict()
                StrictResponse.model_validate(api_data)  # Fails on extra fields
        """
        return type(
            f"Strict{cls.__name__}",
            (cls,),
            {"model_config": ConfigDict(frozen=True, extra="forbid")},
        )
