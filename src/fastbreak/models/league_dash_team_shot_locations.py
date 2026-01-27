"""Models for the League Dashboard Team Shot Locations endpoint response.

This endpoint has a special structure where the headers contain nested column
groups for each distance range. Each range has FGM, FGA, and FG_PCT columns.
"""

from typing import Any

from pydantic import BaseModel, Field, model_validator

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
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
    """Extract the result set from the API response."""
    result_sets = data.get("resultSets", {})
    if isinstance(result_sets, list) and result_sets:
        first = result_sets[0]
        return first if isinstance(first, dict) else None
    if isinstance(result_sets, dict):
        result = result_sets.get("ShotLocations", result_sets)
        return result if isinstance(result, dict) else None
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
            break

    return team_data


def _parse_shot_locations(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Parse the special nested header structure of shot locations.

    The NBA API returns headers in a nested format with rowSet containing
    flat arrays where columns are grouped by distance.
    """
    result_set = _get_result_set(data)
    if result_set is None:
        return []

    rows = result_set.get("rowSet", [])
    if not rows:
        return []

    return [_parse_team_row(row) for row in rows]


class LeagueDashTeamShotLocationsResponse(BaseModel):
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
