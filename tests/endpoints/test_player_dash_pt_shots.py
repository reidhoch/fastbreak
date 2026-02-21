"""Tests for PlayerDashPtShots endpoint."""

import pytest
from pydantic import ValidationError

from fastbreak.endpoints import PlayerDashPtShots
from fastbreak.models import PlayerDashPtShotsResponse
from fastbreak.utils import get_season_from_date


class TestPlayerDashPtShots:
    """Tests for PlayerDashPtShots endpoint."""

    def test_init_with_defaults(self):
        """PlayerDashPtShots uses sensible defaults."""
        endpoint = PlayerDashPtShots(player_id="2544")

        assert endpoint.player_id == "2544"
        assert endpoint.league_id == "00"
        assert endpoint.season == get_season_from_date()
        assert endpoint.per_mode == "PerGame"

    def test_init_with_player_id(self):
        """PlayerDashPtShots accepts player_id."""
        endpoint = PlayerDashPtShots(player_id="203999")

        assert endpoint.player_id == "203999"

    def test_params_with_required_only(self):
        """params() returns all parameters including defaults."""
        endpoint = PlayerDashPtShots(player_id="203999")

        params = endpoint.params()

        assert params["PlayerID"] == "203999"
        assert params["LeagueID"] == "00"
        assert params["TeamID"] == "0"
        assert params["Period"] == "0"

    def test_path_is_correct(self):
        """PlayerDashPtShots has correct API path."""
        endpoint = PlayerDashPtShots(player_id="2544")

        assert endpoint.path == "playerdashptshots"

    def test_response_model_is_correct(self):
        """PlayerDashPtShots uses correct response model."""
        endpoint = PlayerDashPtShots(player_id="2544")

        assert endpoint.response_model is PlayerDashPtShotsResponse

    def test_endpoint_is_frozen(self):
        """PlayerDashPtShots is immutable (frozen dataclass)."""
        endpoint = PlayerDashPtShots(player_id="2544")

        with pytest.raises((AttributeError, ValidationError)):
            endpoint.season = "2023-24"  # type: ignore[misc]


class TestPlayerDashPtShotsResponse:
    """Tests for PlayerDashPtShotsResponse model."""

    @staticmethod
    def _make_base_headers() -> list[str]:
        """Return common headers (first 5 + last 13)."""
        return [
            "PLAYER_ID",
            "PLAYER_NAME_LAST_FIRST",
            "SORT_ORDER",
            "GP",
            "G",
        ]

    @staticmethod
    def _make_stat_headers() -> list[str]:
        """Return stat headers (last 13)."""
        return [
            "FGA_FREQUENCY",
            "FGM",
            "FGA",
            "FG_PCT",
            "EFG_PCT",
            "FG2A_FREQUENCY",
            "FG2M",
            "FG2A",
            "FG2_PCT",
            "FG3A_FREQUENCY",
            "FG3M",
            "FG3A",
            "FG3_PCT",
        ]

    @staticmethod
    def _make_base_row(player_id: int, games: int) -> list:
        """Create base values for a row."""
        return [player_id, "Player, Test", 1, games, games]

    @staticmethod
    def _make_stat_row() -> list:
        """Create stat values for a row."""
        return [1.0, 5.0, 10.0, 0.5, 0.55, 0.6, 3.0, 5.0, 0.6, 0.4, 2.0, 5.0, 0.4]

    def test_parse_tabular_response(self):
        """Response parses NBA's tabular format correctly."""
        base = self._make_base_headers()
        stats = self._make_stat_headers()

        raw_response = {
            "resultSets": [
                {
                    "name": "Overall",
                    "headers": base + ["SHOT_TYPE"] + stats,
                    "rowSet": [
                        self._make_base_row(203999, 70)
                        + ["Overall"]
                        + self._make_stat_row(),
                    ],
                },
                {
                    "name": "GeneralShooting",
                    "headers": base + ["SHOT_TYPE"] + stats,
                    "rowSet": [
                        self._make_base_row(203999, 70)
                        + ["Pullup"]
                        + self._make_stat_row(),
                        self._make_base_row(203999, 70)
                        + ["Catch and Shoot"]
                        + self._make_stat_row(),
                    ],
                },
                {
                    "name": "ShotClockShooting",
                    "headers": base + ["SHOT_CLOCK_RANGE"] + stats,
                    "rowSet": [
                        self._make_base_row(203999, 70)
                        + ["24-22"]
                        + self._make_stat_row(),
                    ],
                },
                {
                    "name": "DribbleShooting",
                    "headers": base + ["DRIBBLE_RANGE"] + stats,
                    "rowSet": [
                        self._make_base_row(203999, 70)
                        + ["0 Dribbles"]
                        + self._make_stat_row(),
                    ],
                },
                {
                    "name": "ClosestDefenderShooting",
                    "headers": base + ["CLOSE_DEF_DIST_RANGE"] + stats,
                    "rowSet": [
                        self._make_base_row(203999, 70)
                        + ["0-2 Feet - Very Tight"]
                        + self._make_stat_row(),
                    ],
                },
                {
                    "name": "ClosestDefender10ftPlusShooting",
                    "headers": base + ["CLOSE_DEF_DIST_RANGE"] + stats,
                    "rowSet": [
                        self._make_base_row(203999, 70)
                        + ["4-6 Feet - Open"]
                        + self._make_stat_row(),
                    ],
                },
                {
                    "name": "TouchTimeShooting",
                    "headers": base + ["TOUCH_TIME_RANGE"] + stats,
                    "rowSet": [
                        self._make_base_row(203999, 70)
                        + ["Touch < 2 Seconds"]
                        + self._make_stat_row(),
                    ],
                },
            ]
        }

        response = PlayerDashPtShotsResponse.model_validate(raw_response)

        # Check overall
        assert len(response.overall) == 1
        assert response.overall[0].shot_type == "Overall"
        assert response.overall[0].player_id == 203999

        # Check general shooting
        assert len(response.general_shooting) == 2
        assert response.general_shooting[0].shot_type == "Pullup"
        assert response.general_shooting[1].shot_type == "Catch and Shoot"

        # Check shot clock
        assert len(response.shot_clock_shooting) == 1
        assert response.shot_clock_shooting[0].shot_clock_range == "24-22"

        # Check dribble
        assert len(response.dribble_shooting) == 1
        assert response.dribble_shooting[0].dribble_range == "0 Dribbles"

        # Check closest defender
        assert len(response.closest_defender_shooting) == 1
        assert (
            response.closest_defender_shooting[0].close_def_dist_range
            == "0-2 Feet - Very Tight"
        )

        # Check closest defender 10ft+
        assert len(response.closest_defender_10ft_plus_shooting) == 1
        assert (
            response.closest_defender_10ft_plus_shooting[0].close_def_dist_range
            == "4-6 Feet - Open"
        )

        # Check touch time
        assert len(response.touch_time_shooting) == 1
        assert response.touch_time_shooting[0].touch_time_range == "Touch < 2 Seconds"

    def test_parse_empty_result_sets(self):
        """Response handles empty result sets."""
        base = self._make_base_headers()
        stats = self._make_stat_headers()

        raw_response = {
            "resultSets": [
                {
                    "name": "Overall",
                    "headers": base + ["SHOT_TYPE"] + stats,
                    "rowSet": [],
                },
                {
                    "name": "GeneralShooting",
                    "headers": base + ["SHOT_TYPE"] + stats,
                    "rowSet": [],
                },
                {
                    "name": "ShotClockShooting",
                    "headers": base + ["SHOT_CLOCK_RANGE"] + stats,
                    "rowSet": [],
                },
                {
                    "name": "DribbleShooting",
                    "headers": base + ["DRIBBLE_RANGE"] + stats,
                    "rowSet": [],
                },
                {
                    "name": "ClosestDefenderShooting",
                    "headers": base + ["CLOSE_DEF_DIST_RANGE"] + stats,
                    "rowSet": [],
                },
                {
                    "name": "ClosestDefender10ftPlusShooting",
                    "headers": base + ["CLOSE_DEF_DIST_RANGE"] + stats,
                    "rowSet": [],
                },
                {
                    "name": "TouchTimeShooting",
                    "headers": base + ["TOUCH_TIME_RANGE"] + stats,
                    "rowSet": [],
                },
            ]
        }

        response = PlayerDashPtShotsResponse.model_validate(raw_response)

        assert response.overall == []
        assert response.general_shooting == []
        assert response.shot_clock_shooting == []
        assert response.dribble_shooting == []
        assert response.closest_defender_shooting == []
        assert response.closest_defender_10ft_plus_shooting == []
        assert response.touch_time_shooting == []
