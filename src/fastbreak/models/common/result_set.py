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
from typing import Any, TypeGuard

from fastbreak.logging import logger

# Type alias for validator functions compatible with Pydantic model_validator(mode="before")
ValidatorFunc = Callable[[object], dict[str, Any]]


def is_tabular_response(data: object) -> TypeGuard[dict[str, Any]]:
    """Check if data is in NBA's tabular resultSets format.

    Used by model validators to determine whether to transform data
    or pass it through unchanged.
    """
    if isinstance(data, dict) and "resultSets" in data:
        return True

    # Log at debug level to help diagnose passthrough scenarios
    if isinstance(data, dict):
        logger.debug(
            "validator_passthrough_missing_key",
            keys=list(data.keys())[:10],
            hint="Expected 'resultSets' key for tabular format",
        )
    else:
        logger.debug(
            "validator_passthrough_wrong_type",
            actual_type=type(data).__name__,
            hint="Expected dict with 'resultSets' key",
        )
    return False


def _parse_result_set_rows(result_set: dict[str, Any]) -> list[dict[str, Any]]:
    headers: list[str] = result_set["headers"]
    rows: list[list[Any]] = result_set["rowSet"]
    return [dict(zip(headers, row, strict=True)) for row in rows]


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
    return _parse_result_set_rows(data["resultSets"][index])


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
            return _parse_result_set_rows(result_set)

    available = [rs.get("name") for rs in data["resultSets"]]
    msg = f"No resultSet named '{name}'. Available: {available}"
    raise ValueError(msg)


def parse_single_result_set(
    data: dict[str, Any],
    name: str,
) -> dict[str, Any] | None:
    """Parse a single-row result set, returning the first row or None.

    This is a convenience wrapper around parse_result_set_by_name for
    result sets that are expected to contain at most one row.

    Args:
        data: Raw API response containing resultSets
        name: The "name" field of the resultSet to parse

    Returns:
        The first row as a dictionary, or None if the result set is empty

    Raises:
        ValueError: If no resultSet with the given name is found

    """
    rows = parse_result_set_by_name(data, name)
    return rows[0] if rows else None


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
        return {field_name: parse_result_set(data, index)}

    return validator


def named_tabular_validator(
    field_name: str,
    result_set_name: str,
) -> ValidatorFunc:
    """Create a model_validator that parses a named result set into a field.

    Like tabular_validator, but looks up the result set by name instead of index.
    Raises ValueError if the named result set is not present in the response.
    Use named_result_sets_validator with ignore_missing=True for result sets
    that are legitimately optional.

    Args:
        field_name: The model field name to populate
        result_set_name: The "name" field of the resultSet to parse

    Returns:
        A function suitable for use with @model_validator(mode="before")

    Raises:
        ValueError: If no resultSet with the given name exists in the response.

    Example:
        class LeagueDashResponse(BaseModel):
            teams: list[TeamStats]

            from_result_sets = model_validator(mode="before")(
                named_tabular_validator("teams", "LeagueDashPTShots")
            )

    """

    def validator(data: object) -> dict[str, Any]:
        if not is_tabular_response(data):
            return data  # type: ignore[return-value]
        rows = parse_result_set_by_name(data, result_set_name)
        return {field_name: rows}

    return validator


def _parse_mapping_value(
    data: dict[str, Any],
    result_set_name: str,
    *,
    is_single: bool,
    ignore_missing: bool,
) -> list[dict[str, Any]] | dict[str, Any] | None:
    """Parse a single result set mapping, handling missing result sets."""
    try:
        rows = parse_result_set_by_name(data, result_set_name)
    except ValueError:
        if not ignore_missing:
            raise
        rows = []

    if is_single:
        return rows[0] if rows else None
    return rows


def named_result_sets_validator(
    mappings: dict[str, tuple[str, bool] | str],
    *,
    ignore_missing: bool = False,
) -> ValidatorFunc:
    """Create a model_validator that parses multiple named result sets.

    Use this for response models with multiple fields populated from
    different named resultSets.

    Args:
        mappings: Dict mapping field names to result set configuration.
            - field_name: The model field name to populate
            - value: Either a result_set_name string (returns list), or a tuple of
              (result_set_name, is_single) where is_single=True takes first row or None.
        ignore_missing: If True, missing result sets return empty list/None instead
            of raising ValueError. Useful for APIs that may omit result sets.

    Returns:
        A function suitable for use with @model_validator(mode="before")

    Example:
        class CumeStatsPlayerResponse(BaseModel):
            game_by_game_stats: list[GameByGameStat]
            total_player_stats: TotalPlayerStat | None = None

            from_result_sets = model_validator(mode="before")(
                named_result_sets_validator({
                    "game_by_game_stats": "GameByGameStats",
                    "total_player_stats": ("TotalPlayerStats", True),
                })
            )

    """

    def validator(data: object) -> dict[str, Any]:
        if not is_tabular_response(data):
            return data  # type: ignore[return-value]

        result: dict[str, Any] = {}
        for field_name, mapping in mappings.items():
            result_set_name, is_single = (
                (mapping, False) if isinstance(mapping, str) else mapping
            )
            result[field_name] = _parse_mapping_value(
                data,
                result_set_name,
                is_single=is_single,
                ignore_missing=ignore_missing,
            )
        return result

    return validator


def singular_result_set_validator(
    mappings: dict[str, str],
) -> ValidatorFunc:
    """Create a model_validator for APIs using 'resultSet' (singular) format.

    Some NBA API endpoints return 'resultSet' (singular) instead of 'resultSets'
    (plural). This validator handles that format.

    Args:
        mappings: Dict mapping field names to result set names.
            Each result set is expected to return a list.

    Returns:
        A function suitable for use with @model_validator(mode="before")

    Example:
        class LeadersTilesResponse(BaseModel):
            leaders: list[LeaderTile]
            all_time_high: list[AllTimeHigh]

            from_result_set = model_validator(mode="before")(
                singular_result_set_validator({
                    "leaders": "LeadersTiles",
                    "all_time_high": "AllTimeSeasonHigh",
                })
            )

    """

    def validator(data: object) -> dict[str, Any]:
        if not isinstance(data, dict) or "resultSet" not in data:
            return data  # type: ignore[return-value]

        # Convert singular to plural format for parsing
        wrapped_data: dict[str, Any] = {"resultSets": data["resultSet"]}

        result: dict[str, Any] = {}
        for field_name, result_set_name in mappings.items():
            rows = parse_result_set_by_name(wrapped_data, result_set_name)
            result[field_name] = rows
        return result

    return validator
