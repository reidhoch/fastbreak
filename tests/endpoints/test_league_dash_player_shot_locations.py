"""Tests for LeagueDashPlayerShotLocations endpoint (player shot zones)."""

import pytest
from pydantic import ValidationError

from fastbreak.endpoints import LeagueDashPlayerShotLocations
from fastbreak.models import LeagueDashPlayerShotLocationsResponse


class TestLeagueDashPlayerShotLocations:
    """Tests for LeagueDashPlayerShotLocations endpoint."""

    def test_init_with_defaults(self):
        """Defaults target the qualitative By Zone breakdown."""
        endpoint = LeagueDashPlayerShotLocations()

        assert endpoint.league_id == "00"
        assert endpoint.distance_range == "By Zone"
        assert endpoint.measure_type == "Base"
        assert endpoint.per_mode == "PerGame"

    def test_params_present(self):
        """params() carries the required keys including DistanceRange."""
        params = LeagueDashPlayerShotLocations(season="2025-26").params()

        assert params["LeagueID"] == "00"
        assert params["Season"] == "2025-26"
        assert params["DistanceRange"] == "By Zone"
        assert params["MeasureType"] == "Base"
        assert params["PerMode"] == "PerGame"

    def test_path_is_correct(self):
        """LeagueDashPlayerShotLocations has correct API path."""
        assert LeagueDashPlayerShotLocations().path == "leaguedashplayershotlocations"

    def test_response_model_is_correct(self):
        """Uses the correct response model."""
        assert (
            LeagueDashPlayerShotLocations().response_model
            is LeagueDashPlayerShotLocationsResponse
        )

    def test_endpoint_is_frozen(self):
        """LeagueDashPlayerShotLocations is immutable (frozen)."""
        endpoint = LeagueDashPlayerShotLocations()

        with pytest.raises((AttributeError, ValidationError)):
            endpoint.season = "2023-24"  # type: ignore[misc]


class TestLeagueDashPlayerShotLocationsResponse:
    """Tests for the nested-header By Zone parse."""

    # Real By Zone layout captured from the live API (2024-25): 6 identity
    # columns including NICKNAME, and 8 zones (Backcourt + a combined Corner 3).
    @staticmethod
    def _by_zone_response(rows: list[list]) -> dict:
        columns = [
            "PLAYER_ID",
            "PLAYER_NAME",
            "TEAM_ID",
            "TEAM_ABBREVIATION",
            "AGE",
            "NICKNAME",
        ]
        for _ in range(8):  # 8 zones × FGM/FGA/FG_PCT
            columns += ["FGM", "FGA", "FG_PCT"]
        return {
            "resultSets": {
                "headers": [
                    {
                        "name": "SHOT_CATEGORY",
                        "columnsToSkip": 6,
                        "columnSpan": 3,
                        "columnNames": [
                            "Restricted Area",
                            "In The Paint (Non-RA)",
                            "Mid-Range",
                            "Left Corner 3",
                            "Right Corner 3",
                            "Above the Break 3",
                            "Backcourt",
                            "Corner 3",
                        ],
                    },
                    {"name": "columns", "columnSpan": 1, "columnNames": columns},
                ],
                "rowSet": rows,
            }
        }

    @staticmethod
    def _row() -> list:
        # 6 identity cols + 8 zones of (fgm, fga, fg_pct)
        identity = [201939, "Stephen Curry", 1610612744, "GSW", 37.0, "Steph"]
        zones = [
            5.0,
            8.0,
            0.625,  # Restricted Area
            2.0,
            6.0,
            0.333,  # In The Paint (Non-RA)
            3.0,
            7.0,
            0.429,  # Mid-Range
            1.0,
            2.0,
            0.500,  # Left Corner 3
            1.0,
            3.0,
            0.333,  # Right Corner 3
            4.0,
            11.0,
            0.364,  # Above the Break 3
            0.0,
            0.0,
            None,  # Backcourt
            2.0,
            5.0,
            0.400,  # Corner 3 (combined)
        ]
        return identity + zones

    def test_parse_by_zone(self):
        """A By Zone row parses 6 identity cols + all 8 per-zone triplets."""
        raw = self._by_zone_response([self._row()])

        response = LeagueDashPlayerShotLocationsResponse.model_validate(raw)

        assert len(response.players) == 1
        p = response.players[0]
        assert p.player_id == 201939
        assert p.player_name == "Stephen Curry"
        assert p.team_abbreviation == "GSW"
        assert p.nickname == "Steph"
        # Identity must NOT bleed into the first zone (the original bug).
        assert p.restricted_area.fgm == 5.0
        assert p.restricted_area.fga == 8.0
        assert p.restricted_area.fg_pct == pytest.approx(0.625)
        assert p.above_the_break_3.fga == 11.0
        assert p.backcourt.fg_pct is None
        assert p.corner_3.fgm == 2.0
        assert p.corner_3.fg_pct == pytest.approx(0.400)

    def test_parse_empty(self):
        """Empty rowSet yields no players."""
        raw = self._by_zone_response([])

        response = LeagueDashPlayerShotLocationsResponse.model_validate(raw)

        assert response.players == []

    def test_unknown_zone_label_falls_back_to_default_layout(self):
        """An unknown SHOT_CATEGORY label must not shift the known zone triplets.

        Regression: dropping an unrecognized label from the field list while the
        row still carries that label's three columns would misalign every
        subsequent (FGM, FGA, FG_PCT) triplet -- exactly the column misalignment
        this parser exists to prevent. When any label is unknown the
        label->column correspondence is untrustworthy, so the parser falls back
        to the known default layout, which the row's physical column count still
        matches.
        """
        # API inserts an unknown "Deep 3" zone in the MIDDLE of the layout.
        labels = [
            "Restricted Area",
            "Deep 3",  # unknown -- not in _ZONE_LABEL_TO_FIELD
            "Mid-Range",
            "Left Corner 3",
            "Right Corner 3",
            "Above the Break 3",
            "Backcourt",
            "Corner 3",
        ]
        identity = [201939, "Stephen Curry", 1610612744, "GSW", 37.0, "Steph"]
        # Eight triplets laid out in the SAME order as ``labels`` above.
        zones = [
            5.0, 8.0, 0.625,  # Restricted Area
            9.0, 9.0, 1.000,  # Deep 3 (unknown)
            3.0, 7.0, 0.429,  # Mid-Range
            1.0, 2.0, 0.500,  # Left Corner 3
            1.0, 3.0, 0.333,  # Right Corner 3
            4.0, 11.0, 0.364,  # Above the Break 3
            0.0, 0.0, None,  # Backcourt
            2.0, 5.0, 0.400,  # Corner 3
        ]  # fmt: skip
        raw = {
            "resultSets": {
                "headers": [
                    {
                        "name": "SHOT_CATEGORY",
                        "columnsToSkip": 6,
                        "columnSpan": 3,
                        "columnNames": labels,
                    },
                    {
                        "name": "columns",
                        "columnSpan": 1,
                        "columnNames": ["x"] * (6 + 3 * 8),
                    },
                ],
                "rowSet": [identity + zones],
            }
        }

        response = LeagueDashPlayerShotLocationsResponse.model_validate(raw)

        assert len(response.players) == 1
        p = response.players[0]
        # Falls back to the default 8-zone layout: the row's physical triplets
        # map positionally, so restricted_area is correct and mid_range takes
        # the SECOND physical triplet (the "Deep 3" columns) -- but crucially the
        # known zones stay in their default positions rather than being silently
        # dropped and re-packed.
        assert p.restricted_area.fgm == 5.0
        assert p.restricted_area.fga == 8.0
        # The default layout keeps consuming three columns per known zone in
        # order, so downstream zones remain positionally aligned with the row.
        assert p.corner_3.fgm == 2.0
        assert p.corner_3.fga == 5.0
        assert p.corner_3.fg_pct == pytest.approx(0.400)
