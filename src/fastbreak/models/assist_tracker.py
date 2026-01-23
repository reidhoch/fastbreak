"""Models for the assist tracker endpoint."""

from typing import Any

from pydantic import BaseModel, model_validator

from fastbreak.models.result_set import is_tabular_response, parse_result_set


class AssistTrackerResponse(BaseModel):
    """Response from the assist tracker endpoint."""

    assists: int

    @model_validator(mode="before")
    @classmethod
    def from_result_sets(cls, data: object) -> dict[str, Any]:
        """Transform NBA's tabular resultSets format into structured data."""
        if not is_tabular_response(data):
            return data  # type: ignore[return-value]

        rows = parse_result_set(data)
        if rows:
            return {"assists": rows[0]["ASSISTS"]}
        return {"assists": 0}
