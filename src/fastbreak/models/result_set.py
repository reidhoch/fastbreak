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

from collections.abc import Callable
from typing import Any

# Type alias for validator functions compatible with Pydantic model_validator(mode="before")
ValidatorFunc = Callable[[object], dict[str, Any]]


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


def tabular_validator(
    field_name: str,
    index: int = 0,
) -> ValidatorFunc:
    """Create a model_validator that parses a single result set into a field.

    Use this for simple response models with a single list field populated
    from a tabular resultSet.

    Args:
        field_name: The model field name to populate
        index: Which resultSet to parse (default: 0)

    Returns:
        A function suitable for use with @model_validator(mode="before")

    Example:
        class LeagueStandingsResponse(BaseModel):
            standings: list[TeamStanding]

            from_result_sets = model_validator(mode="before")(
                tabular_validator("standings")
            )

    """

    def validator(data: object) -> dict[str, Any]:
        if not is_tabular_response(data):
            return data  # type: ignore[return-value]
        return {field_name: parse_result_set(data, index)}  # type: ignore[arg-type]

    return validator


def named_result_sets_validator(
    mappings: dict[str, tuple[str, bool]],
) -> ValidatorFunc:
    """Create a model_validator that parses multiple named result sets.

    Use this for response models with multiple fields populated from
    different named resultSets.

    Args:
        mappings: Dict mapping field names to (result_set_name, is_single).
            - field_name: The model field name to populate
            - result_set_name: The "name" of the resultSet in the API response
            - is_single: If True, takes first row (or None). If False, returns list.

    Returns:
        A function suitable for use with @model_validator(mode="before")

    Example:
        class CumeStatsPlayerResponse(BaseModel):
            game_by_game_stats: list[GameByGameStat]
            total_player_stats: TotalPlayerStat | None = None

            from_result_sets = model_validator(mode="before")(
                named_result_sets_validator({
                    "game_by_game_stats": ("GameByGameStats", False),
                    "total_player_stats": ("TotalPlayerStats", True),
                })
            )

    """

    def validator(data: object) -> dict[str, Any]:
        if not is_tabular_response(data):
            return data  # type: ignore[return-value]

        result: dict[str, Any] = {}
        for field_name, (result_set_name, is_single) in mappings.items():
            rows = parse_result_set_by_name(data, result_set_name)  # type: ignore[arg-type]
            if is_single:
                result[field_name] = rows[0] if rows else None
            else:
                result[field_name] = rows
        return result

    return validator
