"""Utilities for parsing NBA Stats API tabular resultSets format.

The NBA Stats API returns data in two formats:
1. Structured JSON (newer v3 endpoints like playbyplayv3)
2. Tabular format with headers + rowSet (most endpoints)

This module provides helpers for parsing the tabular format into
dictionaries that Pydantic can validate.

Example API response in tabular format:
    {
        "resultSets": [
            {
                "name": "Standings",
                "headers": ["TeamID", "TeamName", "WINS", ...],
                "rowSet": [
                    [1610612760, "Thunder", 36, ...],
                    [1610612765, "Pistons", 31, ...],
                ]
            }
        ]
    }

Usage in a Pydantic model:
    class MyResponse(BaseModel):
        teams: list[TeamModel]

        @model_validator(mode="before")
        @classmethod
        def from_result_sets(cls, data: JSON) -> dict[str, Any]:
            if not is_tabular_response(data):
                return data
            return {"teams": parse_result_set(data)}

"""

from typing import Any


def is_tabular_response(data: object) -> bool:
    """Check if data is in NBA's tabular resultSets format."""
    return isinstance(data, dict) and "resultSets" in data


def parse_result_set(
    data: dict[str, Any],
    index: int = 0,
) -> list[dict[str, Any]]:
    """Parse a single resultSet from tabular format into list of dicts.

    Args:
        data: Raw API response containing resultSets
        index: Which resultSet to parse (default: 0, the first one)

    Returns:
        List of dictionaries, one per row, with headers as keys

    Example:
        >>> data = {
        ...     "resultSets": [{
        ...         "headers": ["id", "name"],
        ...         "rowSet": [[1, "Alice"], [2, "Bob"]]
        ...     }]
        ... }
        >>> parse_result_set(data)
        [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]

    """
    result_set = data["resultSets"][index]
    headers: list[str] = result_set["headers"]
    rows: list[list[Any]] = result_set["rowSet"]

    return [dict(zip(headers, row, strict=True)) for row in rows]


def parse_result_set_by_name(
    data: dict[str, Any],
    name: str,
) -> list[dict[str, Any]]:
    """Parse a resultSet by its name.

    Args:
        data: Raw API response containing resultSets
        name: The "name" field of the resultSet to parse

    Returns:
        List of dictionaries, one per row, with headers as keys

    Raises:
        ValueError: If no resultSet with the given name is found

    """
    for result_set in data["resultSets"]:
        if result_set.get("name") == name:
            headers: list[str] = result_set["headers"]
            rows: list[list[Any]] = result_set["rowSet"]
            return [dict(zip(headers, row, strict=True)) for row in rows]

    available = [rs.get("name") for rs in data["resultSets"]]
    msg = f"No resultSet named '{name}'. Available: {available}"
    raise ValueError(msg)
