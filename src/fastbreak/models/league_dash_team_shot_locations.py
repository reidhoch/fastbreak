"""Models for the League Dashboard Team Shot Locations endpoint response.

This endpoint has a special structure where the headers contain nested column
groups for each distance range. Each range has FGM, FGA, and FG_PCT columns.
"""

from typing import Any

from pydantic import BaseModel, Field, model_validator

from fastbreak.logging import logger
from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.response import FrozenResponse
from fastbreak.models.common.result_set import is_tabular_response


class ShotRange(PandasMixin, PolarsMixin, BaseModel):
    """Shot statistics for a specific distance range."""

    fgm: float = 0.0
    fga: float = 0.0
    fg_pct: float | None = None


class TeamShotLocations(PandasMixin, PolarsMixin, BaseModel):
    """Shot location statistics for a single team.

    Contains shooting stats broken down by distance ranges.
    The exact ranges depend on the DistanceRange parameter used.
    """

    team_id: int
    team_name: str

    # Shot ranges (5ft Range mode) - each has FGM, FGA, FG_PCT
    range_less_than_5ft: ShotRange = Field(default_factory=ShotRange)
    range_5_9ft: ShotRange = Field(default_factory=ShotRange)
    range_10_14ft: ShotRange = Field(default_factory=ShotRange)
    range_15_19ft: ShotRange = Field(default_factory=ShotRange)
    range_20_24ft: ShotRange = Field(default_factory=ShotRange)
    range_25_29ft: ShotRange = Field(default_factory=ShotRange)
    range_back_court: ShotRange = Field(default_factory=ShotRange)


def _get_result_set(data: dict[str, Any]) -> dict[str, Any] | None:
    """Extract the result set from the API response.

    Returns None if the expected structure is not found, logging a warning
    to help diagnose API schema changes or malformed responses.
    """
    result_sets = data.get("resultSets")
    if result_sets is None:
        logger.warning(
            "shot_locations_missing_result_sets",
            data_keys=list(data.keys()),
            hint="Expected 'resultSets' key in response",
        )
        return None

    # Handle list format: extract first element
    if isinstance(result_sets, list):
        if not result_sets:
            logger.debug(
                "shot_locations_empty_result_sets",
                hint="resultSets is an empty list - no data returned from API",
            )
            return None
        first = result_sets[0]
        if isinstance(first, dict):
            return first
        logger.warning(
            "shot_locations_invalid_result_set_type",
            actual_type=type(first).__name__,
            hint="Expected dict as first element of resultSets list",
        )
    elif isinstance(result_sets, dict):
        # Handle dict format: extract ShotLocations or use entire dict
        result = result_sets.get("ShotLocations", result_sets)
        if isinstance(result, dict):
            return result
        logger.warning(
            "shot_locations_invalid_structure",
            actual_type=type(result).__name__,
            hint="Expected dict for ShotLocations result",
        )
    else:
        logger.warning(
            "shot_locations_unexpected_result_sets_type",
            actual_type=type(result_sets).__name__,
            hint="Expected list or dict for resultSets",
        )

    return None


def _parse_team_row(row: list[Any]) -> dict[str, Any]:
    """Parse a single team row into shot location data."""
    team_data: dict[str, Any] = {
        "team_id": row[0],
        "team_name": row[1],
    }

    # Parse shot ranges from remaining columns
    # Structure: FGM, FGA, FG_PCT for each range, starting at index 2
    # Note: This endpoint does not include team_abbreviation
    ranges = [
        "range_less_than_5ft",
        "range_5_9ft",
        "range_10_14ft",
        "range_15_19ft",
        "range_20_24ft",
        "range_25_29ft",
        "range_back_court",
    ]

    idx = 2
    for range_name in ranges:
        if idx + 2 < len(row):
            team_data[range_name] = {
                "fgm": row[idx] or 0.0,
                "fga": row[idx + 1] or 0.0,
                "fg_pct": row[idx + 2],
            }
            idx += 3
        else:
            logger.warning(
                "shot_locations_truncated_row",
                team_id=team_data.get("team_id"),
                team_name=team_data.get("team_name"),
                missing_range=range_name,
                row_length=len(row),
                expected_min_length=idx + 3,
                hint="Row has fewer columns than expected; some shot ranges missing",
            )
            break

    return team_data


def _parse_shot_locations(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Parse the special nested header structure of shot locations.

    The NBA API returns headers in a nested format with rowSet containing
    flat arrays where columns are grouped by distance.

    Returns an empty list if parsing fails, with warnings logged to help
    diagnose the issue.
    """
    result_set = _get_result_set(data)
    if result_set is None:
        # Warning already logged by _get_result_set
        return []

    rows = result_set.get("rowSet")
    if rows is None:
        logger.warning(
            "shot_locations_missing_row_set",
            result_set_keys=list(result_set.keys()),
            hint="Expected 'rowSet' key in result set",
        )
        return []

    if not isinstance(rows, list):
        logger.warning(
            "shot_locations_invalid_row_set_type",
            actual_type=type(rows).__name__,
            hint="Expected list for rowSet",
        )
        return []

    # Empty rowSet is valid - no teams matched the query
    if not rows:
        return []

    return [_parse_team_row(row) for row in rows]


class LeagueDashTeamShotLocationsResponse(FrozenResponse):
    """Response from the league dashboard team shot locations endpoint.

    Contains shot statistics by distance range for all teams.
    """

    teams: list[TeamShotLocations] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def from_result_sets(cls, data: object) -> dict[str, Any]:
        """Transform NBA's special shot locations format into structured data."""
        if not is_tabular_response(data):
            return data  # type: ignore[return-value]

        # is_tabular_response is a TypeGuard that narrows data to dict[str, Any]
        return {"teams": _parse_shot_locations(data)}
