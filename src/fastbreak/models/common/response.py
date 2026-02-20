"""Base class for API response models."""

from typing import Any, Self

from pydantic import BaseModel, ConfigDict, model_validator

from fastbreak.logging import logger

# Standard NBA API wrapper fields that are handled by transformation validators
# and should not trigger unknown field warnings
_API_WRAPPER_FIELDS: frozenset[str] = frozenset(
    {
        "resource",  # Endpoint name
        "parameters",  # Request parameters echoed back
        "resultSet",  # Single result set (tabular format)
        "resultSets",  # Multiple result sets (tabular format)
    }
)


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

        # Collect both field names and their aliases
        known_keys: set[str] = set(_API_WRAPPER_FIELDS)
        for field_name, field_info in cls.model_fields.items():
            known_keys.add(field_name)
            if field_info.alias:
                known_keys.add(field_info.alias)

        extra_fields = set(data.keys()) - known_keys
        if extra_fields:
            logger.warning(
                "unknown_fields_received",
                model=cls.__name__,
                fields=sorted(extra_fields),
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
