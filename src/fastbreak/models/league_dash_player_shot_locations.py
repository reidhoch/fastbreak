"""Models for the League Dashboard Player Shot Locations endpoint response.

Like the team variant, this endpoint uses the special nested column-header
format. This player model targets the ``By Zone`` DistanceRange, which yields
qualitative shot zones (Restricted Area, Mid-Range, corner 3s, etc.) — the
per-player complement to ``shots.zone_breakdown`` and the team distance-bucket
model in ``league_dash_team_shot_locations``.
"""

from typing import Any

from pydantic import BaseModel, Field, model_validator

from fastbreak.logging import logger
from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.response import FrozenResponse


class ShotZone(PandasMixin, PolarsMixin, BaseModel):
    """FGM/FGA/FG_PCT for a single qualitative shot zone."""

    fgm: float = 0.0
    fga: float = 0.0
    fg_pct: float | None = None


class PlayerShotLocations(PandasMixin, PolarsMixin, BaseModel):
    """Shot location statistics for a single player, by qualitative zone.

    Assumes the ``By Zone`` DistanceRange. The live API returns eight zones —
    the seven exclusive ones plus a combined ``corner_3`` (left + right).
    """

    player_id: int
    player_name: str
    team_id: int
    team_abbreviation: str
    age: float | None = None
    nickname: str | None = None

    restricted_area: ShotZone = Field(default_factory=ShotZone)
    in_the_paint_non_ra: ShotZone = Field(default_factory=ShotZone)
    mid_range: ShotZone = Field(default_factory=ShotZone)
    left_corner_3: ShotZone = Field(default_factory=ShotZone)
    right_corner_3: ShotZone = Field(default_factory=ShotZone)
    above_the_break_3: ShotZone = Field(default_factory=ShotZone)
    backcourt: ShotZone = Field(default_factory=ShotZone)
    corner_3: ShotZone = Field(default_factory=ShotZone)


# Map the API's SHOT_CATEGORY zone labels to model field names. Zones are matched
# by label (data-driven) so a change in count/order can't silently misalign them.
_ZONE_LABEL_TO_FIELD = {
    "Restricted Area": "restricted_area",
    "In The Paint (Non-RA)": "in_the_paint_non_ra",
    "Mid-Range": "mid_range",
    "Left Corner 3": "left_corner_3",
    "Right Corner 3": "right_corner_3",
    "Above the Break 3": "above_the_break_3",
    "Backcourt": "backcourt",
    "Corner 3": "corner_3",
}
# Fallback identity-column count if the header omits columnsToSkip. The live API
# sends PLAYER_ID, PLAYER_NAME, TEAM_ID, TEAM_ABBREVIATION, AGE, NICKNAME.
_DEFAULT_IDENTITY_COLUMN_COUNT = 6


def _get_result_set(data: dict[str, Any]) -> dict[str, Any] | None:
    """Extract the result set from the response (list or dict resultSets)."""
    result_sets = data.get("resultSets")
    if result_sets is None:
        logger.warning(
            "player_shot_locations_missing_result_sets",
            data_keys=list(data.keys()),
            hint="Expected 'resultSets' key in response",
        )
        return None
    if isinstance(result_sets, list):
        if not result_sets:
            return None
        first = result_sets[0]
        return first if isinstance(first, dict) else None
    if isinstance(result_sets, dict):
        return result_sets
    logger.warning(
        "player_shot_locations_unexpected_result_sets_type",
        actual_type=type(result_sets).__name__,
        hint="Expected list or dict for resultSets",
    )
    return None


_IDENTITY_FIELDS = (
    "player_id",
    "player_name",
    "team_id",
    "team_abbreviation",
    "age",
    "nickname",
)


def _category_header(result_set: dict[str, Any]) -> dict[str, Any] | None:
    """Return the SHOT_CATEGORY grouping header (first header entry), if present."""
    headers = result_set.get("headers")
    if not isinstance(headers, list) or not headers:
        return None
    first = headers[0]
    return first if isinstance(first, dict) else None


def _identity_count(category: dict[str, Any] | None) -> int:
    """Number of identity columns before the zone triplets (API columnsToSkip)."""
    if category is None:
        return _DEFAULT_IDENTITY_COLUMN_COUNT
    skip = category.get("columnsToSkip")
    if isinstance(skip, int) and skip > 0:
        return skip
    return _DEFAULT_IDENTITY_COLUMN_COUNT


def _zone_fields_from_labels(category: dict[str, Any] | None) -> list[str]:
    """Map the header's SHOT_CATEGORY labels to model field names (in order)."""
    default = list(_ZONE_LABEL_TO_FIELD.values())
    if category is None:
        return default
    labels = category.get("columnNames")
    if not isinstance(labels, list) or not labels:
        return default
    unknown = [label for label in labels if label not in _ZONE_LABEL_TO_FIELD]
    if unknown:
        # An unknown label means the label->column correspondence can no longer
        # be trusted: dropping it from the field list while its three columns
        # remain in the row would shift every subsequent (FGM, FGA, FG_PCT)
        # triplet -- the exact misalignment this parser exists to prevent. Fall
        # back to the known default layout, which the row's column count still
        # matches, rather than parsing a corrupted subset.
        logger.warning(
            "player_shot_locations_unknown_zone_label",
            labels=unknown,
            hint="Unknown zone label(s); falling back to default layout",
        )
        return default
    mapped = [_ZONE_LABEL_TO_FIELD[label] for label in labels]
    return mapped or default


def _zone_layout(result_set: dict[str, Any]) -> tuple[int, list[str]]:
    """Return (identity_column_count, zone_field_names) from the nested header.

    Reads the API's own ``columnsToSkip`` and ``SHOT_CATEGORY`` labels so the
    parser follows the live layout rather than a hardcoded assumption.
    """
    category = _category_header(result_set)
    return _identity_count(category), _zone_fields_from_labels(category)


def _parse_player_row(
    row: list[Any], identity_count: int, zone_fields: list[str]
) -> dict[str, Any] | None:
    """Parse one flat By Zone row into player + per-zone dicts."""
    min_len = identity_count + 3 * len(zone_fields)
    if len(row) < min_len:
        logger.warning(
            "player_shot_locations_truncated_row",
            row_length=len(row),
            expected_min_length=min_len,
            hint="Row has fewer columns than the By Zone layout requires",
        )
        return None

    player: dict[str, Any] = {
        name: row[i] for i, name in enumerate(_IDENTITY_FIELDS) if i < identity_count
    }
    idx = identity_count
    for zone in zone_fields:
        player[zone] = {
            "fgm": row[idx] or 0.0,
            "fga": row[idx + 1] or 0.0,
            "fg_pct": row[idx + 2],
        }
        idx += 3
    return player


def _parse_shot_locations(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Parse the nested By Zone header structure into player dicts."""
    result_set = _get_result_set(data)
    if result_set is None:
        return []
    rows = result_set.get("rowSet")
    if not isinstance(rows, list):
        if rows is not None:
            logger.warning(
                "player_shot_locations_invalid_row_set_type",
                actual_type=type(rows).__name__,
                hint="Expected list for rowSet",
            )
        return []
    identity_count, zone_fields = _zone_layout(result_set)
    parsed = [_parse_player_row(row, identity_count, zone_fields) for row in rows]
    return [p for p in parsed if p is not None]


class LeagueDashPlayerShotLocationsResponse(FrozenResponse):
    """Response from the league dashboard player shot locations endpoint.

    Contains per-player shot statistics by qualitative zone (By Zone mode).
    """

    players: list[PlayerShotLocations] = Field(
        default_factory=list[PlayerShotLocations]
    )

    @model_validator(mode="before")
    @classmethod
    def from_result_sets(cls, data: object) -> dict[str, Any]:
        """Transform NBA's nested shot-locations format into structured data."""
        if not isinstance(data, dict) or "resultSets" not in data:
            return data  # type: ignore[return-value]
        return {"players": _parse_shot_locations(data)}
