"""Tests for PlayerDashboardByShootingSplits endpoint."""

import pytest
from pydantic import ValidationError

from fastbreak.endpoints import PlayerDashboardByShootingSplits
from fastbreak.models import PlayerDashboardByShootingSplitsResponse
from fastbreak.utils import get_season_from_date


class TestPlayerDashboardByShootingSplits:
    """Tests for PlayerDashboardByShootingSplits endpoint."""

    def test_init_with_defaults(self):
        """PlayerDashboardByShootingSplits uses sensible defaults."""
        endpoint = PlayerDashboardByShootingSplits(player_id=2544)

        assert endpoint.player_id == 2544
        assert endpoint.league_id == "00"
        assert endpoint.season == get_season_from_date()
        assert endpoint.season_type == "Regular Season"
        assert endpoint.per_mode == "PerGame"
        assert endpoint.measure_type == "Base"
        # Always-sent params have default 0
        assert endpoint.po_round == 0
        assert endpoint.month == 0
        assert endpoint.opponent_team_id == 0
        assert endpoint.period == 0
        assert endpoint.last_n_games == 0
        assert endpoint.ist_round is None

    def test_init_with_player_id(self):
        """PlayerDashboardByShootingSplits accepts player_id."""
        endpoint = PlayerDashboardByShootingSplits(player_id=203999)

        assert endpoint.player_id == 203999

    def test_init_with_optional_filters(self):
        """PlayerDashboardByShootingSplits accepts optional filters."""
        endpoint = PlayerDashboardByShootingSplits(
            player_id=203999,
            season="2023-24",
            last_n_games=10,
            outcome="W",
        )

        assert endpoint.season == "2023-24"
        assert endpoint.last_n_games == 10
        assert endpoint.outcome == "W"

    def test_params_with_required_only(self):
        """params() returns required and always-sent parameters."""
        endpoint = PlayerDashboardByShootingSplits(player_id=203999)

        params = endpoint.params()

        assert params == {
            "PlayerID": "203999",
            "LeagueID": "00",
            "Season": get_season_from_date(),
            "SeasonType": "Regular Season",
            "PerMode": "PerGame",
            "MeasureType": "Base",
            "PaceAdjust": "N",
            "PlusMinus": "N",
            "Rank": "N",
            "PORound": "0",
            "Month": "0",
            "OpponentTeamID": "0",
            "Period": "0",
            "LastNGames": "0",
        }

    def test_params_with_filters(self):
        """params() includes optional filters when set."""
        endpoint = PlayerDashboardByShootingSplits(
            player_id=203999,
            last_n_games=10,
            outcome="W",
            location="Home",
        )

        params = endpoint.params()

        assert params["PlayerID"] == "203999"
        assert params["LastNGames"] == "10"
        assert params["Outcome"] == "W"
        assert params["Location"] == "Home"

    def test_path_is_correct(self):
        """PlayerDashboardByShootingSplits has correct API path."""
        endpoint = PlayerDashboardByShootingSplits(player_id=2544)

        assert endpoint.path == "playerdashboardbyshootingsplits"

    def test_response_model_is_correct(self):
        """PlayerDashboardByShootingSplits uses correct response model."""
        endpoint = PlayerDashboardByShootingSplits(player_id=2544)

        assert endpoint.response_model is PlayerDashboardByShootingSplitsResponse

    def test_endpoint_is_frozen(self):
        """PlayerDashboardByShootingSplits is immutable (frozen dataclass)."""
        endpoint = PlayerDashboardByShootingSplits(player_id=2544)

        with pytest.raises((AttributeError, ValidationError)):
            endpoint.season = "2023-24"  # type: ignore[misc]


class TestPlayerDashboardByShootingSplitsResponse:
    """Tests for PlayerDashboardByShootingSplitsResponse model."""

    @staticmethod
    def _make_headers_with_rank() -> list[str]:
        """Return headers with rank columns."""
        return [
            "GROUP_SET",
            "GROUP_VALUE",
            "FGM",
            "FGA",
            "FG_PCT",
            "FG3M",
            "FG3A",
            "FG3_PCT",
            "EFG_PCT",
            "BLKA",
            "PCT_AST_2PM",
            "PCT_UAST_2PM",
            "PCT_AST_3PM",
            "PCT_UAST_3PM",
            "PCT_AST_FGM",
            "PCT_UAST_FGM",
            "FGM_RANK",
            "FGA_RANK",
            "FG_PCT_RANK",
            "FG3M_RANK",
            "FG3A_RANK",
            "FG3_PCT_RANK",
            "EFG_PCT_RANK",
            "BLKA_RANK",
            "PCT_AST_2PM_RANK",
            "PCT_UAST_2PM_RANK",
            "PCT_AST_3PM_RANK",
            "PCT_UAST_3PM_RANK",
            "PCT_AST_FGM_RANK",
            "PCT_UAST_FGM_RANK",
        ]

    @staticmethod
    def _make_headers_no_rank() -> list[str]:
        """Return headers without rank columns (for shot type summary)."""
        return [
            "GROUP_SET",
            "GROUP_VALUE",
            "FGM",
            "FGA",
            "FG_PCT",
            "FG3M",
            "FG3A",
            "FG3_PCT",
            "EFG_PCT",
            "BLKA",
            "PCT_AST_2PM",
            "PCT_UAST_2PM",
            "PCT_AST_3PM",
            "PCT_UAST_3PM",
            "PCT_AST_FGM",
            "PCT_UAST_FGM",
        ]

    @staticmethod
    def _make_assisted_by_headers() -> list[str]:
        """Return headers for assisted_by result set."""
        return [
            "GROUP_SET",
            "PLAYER_ID",
            "PLAYER_NAME",
            "FGM",
            "FGA",
            "FG_PCT",
            "FG3M",
            "FG3A",
            "FG3_PCT",
            "EFG_PCT",
            "BLKA",
            "PCT_AST_2PM",
            "PCT_UAST_2PM",
            "PCT_AST_3PM",
            "PCT_UAST_3PM",
            "PCT_AST_FGM",
            "PCT_UAST_FGM",
            "FGM_RANK",
            "FGA_RANK",
            "FG_PCT_RANK",
            "FG3M_RANK",
            "FG3A_RANK",
            "FG3_PCT_RANK",
            "EFG_PCT_RANK",
            "BLKA_RANK",
            "PCT_AST_2PM_RANK",
            "PCT_UAST_2PM_RANK",
            "PCT_AST_3PM_RANK",
            "PCT_UAST_3PM_RANK",
            "PCT_AST_FGM_RANK",
            "PCT_UAST_FGM_RANK",
        ]

    @staticmethod
    def _make_row_with_rank(
        group_set: str, group_value: str, fgm: int, fga: int
    ) -> list:
        """Create a test row with rank columns."""
        fg_pct = fgm / fga if fga > 0 else 0.0
        return [
            group_set,
            group_value,
            fgm,
            fga,
            fg_pct,
            0,
            0,
            0.0,
            fg_pct,
            0,
            0.5,
            0.5,
            0.0,
            0.0,
            0.5,
            0.5,
            *[1] * 14,  # rank columns
        ]

    @staticmethod
    def _make_row_no_rank(group_set: str, group_value: str, fgm: int, fga: int) -> list:
        """Create a test row without rank columns."""
        fg_pct = fgm / fga if fga > 0 else 0.0
        return [
            group_set,
            group_value,
            fgm,
            fga,
            fg_pct,
            0,
            0,
            0.0,
            fg_pct,
            0,
            0.5,
            0.5,
            0.0,
            0.0,
            0.5,
            0.5,
        ]

    @staticmethod
    def _make_assisted_by_row(player_id: int, player_name: str, fgm: int) -> list:
        """Create a test row for assisted_by."""
        return [
            "Assisted By",
            player_id,
            player_name,
            fgm,
            fgm,
            1.0,
            0,
            0,
            0.0,
            1.0,
            0,
            1.0,
            0.0,
            0.0,
            0.0,
            1.0,
            0.0,
            *[1] * 14,
        ]

    def test_parse_tabular_response(self):
        """Response parses NBA's tabular format correctly."""
        headers_rank = self._make_headers_with_rank()
        headers_no_rank = self._make_headers_no_rank()
        headers_assisted = self._make_assisted_by_headers()

        raw_response = {
            "resultSets": [
                {
                    "name": "OverallPlayerDashboard",
                    "headers": headers_rank,
                    "rowSet": [self._make_row_with_rank("Overall", "2024-25", 96, 163)],
                },
                {
                    "name": "Shot5FTPlayerDashboard",
                    "headers": headers_rank,
                    "rowSet": [
                        self._make_row_with_rank(
                            "Shot Distance (5ft)", "Less Than 5 ft.", 37, 51
                        ),
                        self._make_row_with_rank(
                            "Shot Distance (5ft)", "5-9 ft.", 27, 45
                        ),
                    ],
                },
                {
                    "name": "Shot8FTPlayerDashboard",
                    "headers": headers_rank,
                    "rowSet": [
                        self._make_row_with_rank(
                            "Shot Distance (8ft)", "Less Than 8 ft.", 54, 82
                        ),
                    ],
                },
                {
                    "name": "ShotAreaPlayerDashboard",
                    "headers": headers_rank,
                    "rowSet": [
                        self._make_row_with_rank(
                            "Shot Area", "Restricted Area", 32, 44
                        ),
                        self._make_row_with_rank("Shot Area", "Mid-Range", 7, 14),
                    ],
                },
                {
                    "name": "AssitedShotPlayerDashboard",  # Note: API typo
                    "headers": headers_rank,
                    "rowSet": [
                        self._make_row_with_rank("Assisted Shot", "Assisted", 62, 62),
                        self._make_row_with_rank("Assisted Shot", "Unassisted", 34, 34),
                    ],
                },
                {
                    "name": "ShotTypeSummaryPlayerDashboard",
                    "headers": headers_no_rank,
                    "rowSet": [
                        self._make_row_no_rank(
                            "Shot Type Summary", "Jump Shot", 50, 99
                        ),
                        self._make_row_no_rank("Shot Type Summary", "Layup", 30, 40),
                    ],
                },
                {
                    "name": "ShotTypePlayerDashboard",
                    "headers": headers_rank,
                    "rowSet": [
                        self._make_row_with_rank(
                            "Shot Type Detail", "Cutting Dunk Shot", 2, 2
                        ),
                    ],
                },
                {
                    "name": "AssistedBy",
                    "headers": headers_assisted,
                    "rowSet": [
                        self._make_assisted_by_row(1631128, "Braun, Christian", 18),
                        self._make_assisted_by_row(203932, "Gordon, Aaron", 8),
                    ],
                },
            ]
        }

        response = PlayerDashboardByShootingSplitsResponse.model_validate(raw_response)

        # Check overall
        assert response.overall is not None
        assert response.overall.fgm == 96
        assert response.overall.fga == 163

        # Check shot distance 5ft
        assert len(response.by_shot_distance_5ft) == 2
        assert response.by_shot_distance_5ft[0].group_value == "Less Than 5 ft."
        assert response.by_shot_distance_5ft[0].fgm == 37

        # Check shot distance 8ft
        assert len(response.by_shot_distance_8ft) == 1
        assert response.by_shot_distance_8ft[0].group_value == "Less Than 8 ft."

        # Check shot area
        assert len(response.by_shot_area) == 2
        assert response.by_shot_area[0].group_value == "Restricted Area"
        assert response.by_shot_area[1].group_value == "Mid-Range"

        # Check assisted (note: using API's typo in result set name)
        assert len(response.by_assisted) == 2
        assert response.by_assisted[0].group_value == "Assisted"
        assert response.by_assisted[1].group_value == "Unassisted"

        # Check shot type summary (no rank columns)
        assert len(response.by_shot_type_summary) == 2
        assert response.by_shot_type_summary[0].group_value == "Jump Shot"
        assert response.by_shot_type_summary[0].fgm == 50

        # Check shot type detail
        assert len(response.by_shot_type_detail) == 1
        assert response.by_shot_type_detail[0].group_value == "Cutting Dunk Shot"

        # Check assisted by
        assert len(response.assisted_by) == 2
        assert response.assisted_by[0].player_name == "Braun, Christian"
        assert response.assisted_by[0].player_id == 1631128
        assert response.assisted_by[0].fgm == 18

    def test_parse_empty_result_sets(self):
        """Response handles empty result sets."""
        headers_rank = self._make_headers_with_rank()
        headers_no_rank = self._make_headers_no_rank()
        headers_assisted = self._make_assisted_by_headers()

        raw_response = {
            "resultSets": [
                {
                    "name": "OverallPlayerDashboard",
                    "headers": headers_rank,
                    "rowSet": [],
                },
                {
                    "name": "Shot5FTPlayerDashboard",
                    "headers": headers_rank,
                    "rowSet": [],
                },
                {
                    "name": "Shot8FTPlayerDashboard",
                    "headers": headers_rank,
                    "rowSet": [],
                },
                {
                    "name": "ShotAreaPlayerDashboard",
                    "headers": headers_rank,
                    "rowSet": [],
                },
                {
                    "name": "AssitedShotPlayerDashboard",
                    "headers": headers_rank,
                    "rowSet": [],
                },
                {
                    "name": "ShotTypeSummaryPlayerDashboard",
                    "headers": headers_no_rank,
                    "rowSet": [],
                },
                {
                    "name": "ShotTypePlayerDashboard",
                    "headers": headers_rank,
                    "rowSet": [],
                },
                {"name": "AssistedBy", "headers": headers_assisted, "rowSet": []},
            ]
        }

        response = PlayerDashboardByShootingSplitsResponse.model_validate(raw_response)

        assert response.overall is None
        assert response.by_shot_distance_5ft == []
        assert response.by_shot_distance_8ft == []
        assert response.by_shot_area == []
        assert response.by_assisted == []
        assert response.by_shot_type_summary == []
        assert response.by_shot_type_detail == []
        assert response.assisted_by == []
