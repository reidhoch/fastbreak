"""Tests for LeagueDashPlayerPtShot endpoint."""

import pytest
from pydantic import ValidationError

from fastbreak.endpoints import LeagueDashPlayerPtShot
from fastbreak.models import LeagueDashPlayerPtShotResponse


class TestLeagueDashPlayerPtShot:
    """Tests for LeagueDashPlayerPtShot endpoint."""

    def test_init_with_defaults(self):
        """LeagueDashPlayerPtShot uses sensible defaults."""
        endpoint = LeagueDashPlayerPtShot()

        assert endpoint.league_id == "00"
        assert endpoint.season is None
        assert endpoint.season_type == "Regular Season"
        assert endpoint.per_mode == "Totals"

    def test_params_with_required_only(self):
        """params() returns the required parameters."""
        endpoint = LeagueDashPlayerPtShot(season="2025-26")

        params = endpoint.params()

        assert params["LeagueID"] == "00"
        assert params["SeasonType"] == "Regular Season"
        assert params["PerMode"] == "Totals"
        assert params["Season"] == "2025-26"

    def test_params_omits_season_when_none(self):
        """Season is omitted from params when not set."""
        endpoint = LeagueDashPlayerPtShot()

        assert "Season" not in endpoint.params()

    def test_optional_shot_filters_included_when_set(self):
        """Tracking-shot filters appear in params only when provided."""
        endpoint = LeagueDashPlayerPtShot(
            season="2025-26",
            close_def_dist_range="0-2 Feet - Very Tight",
            dribble_range="0 Dribbles",
            touch_time_range="Touch < 2 Seconds",
            shot_clock_range="24-22",
            general_range="Overall",
        )

        params = endpoint.params()

        assert params["CloseDefDistRange"] == "0-2 Feet - Very Tight"
        assert params["DribbleRange"] == "0 Dribbles"
        assert params["TouchTimeRange"] == "Touch < 2 Seconds"
        assert params["ShotClockRange"] == "24-22"
        assert params["GeneralRange"] == "Overall"

    def test_optional_shot_filters_omitted_when_unset(self):
        """Unset tracking-shot filters are absent from params."""
        params = LeagueDashPlayerPtShot(season="2025-26").params()

        for key in (
            "CloseDefDistRange",
            "DribbleRange",
            "TouchTimeRange",
            "ShotClockRange",
            "GeneralRange",
        ):
            assert key not in params

    def test_path_is_correct(self):
        """LeagueDashPlayerPtShot has correct API path."""
        assert LeagueDashPlayerPtShot().path == "leaguedashplayerptshot"

    def test_response_model_is_correct(self):
        """LeagueDashPlayerPtShot uses correct response model."""
        assert LeagueDashPlayerPtShot().response_model is LeagueDashPlayerPtShotResponse

    def test_endpoint_is_frozen(self):
        """LeagueDashPlayerPtShot is immutable (frozen)."""
        endpoint = LeagueDashPlayerPtShot()

        with pytest.raises((AttributeError, ValidationError)):
            endpoint.season = "2023-24"  # type: ignore[misc]


class TestLeagueDashPlayerPtShotResponse:
    """Tests for LeagueDashPlayerPtShotResponse model."""

    @staticmethod
    def _headers() -> list[str]:
        return [
            "PLAYER_ID",
            "PLAYER_NAME",
            "PLAYER_LAST_TEAM_ID",
            "PLAYER_LAST_TEAM_ABBREVIATION",
            "AGE",
            "GP",
            "G",
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
    def _row() -> list:
        return [
            201939,
            "Stephen Curry",
            1610612744,
            "GSW",
            37.0,
            70,
            70,
            1.0,
            9.0,
            20.0,
            0.45,
            0.60,
            0.4,
            4.0,
            8.0,
            0.5,
            0.6,
            5.0,
            12.0,
            0.417,
        ]

    def test_parse_tabular_response(self):
        """Response parses the LeagueDashPTShots result set."""
        raw = {
            "resultSets": [
                {
                    "name": "LeagueDashPTShots",
                    "headers": self._headers(),
                    "rowSet": [self._row()],
                }
            ]
        }

        response = LeagueDashPlayerPtShotResponse.model_validate(raw)

        assert len(response.players) == 1
        player = response.players[0]
        assert player.player_id == 201939
        assert player.player_name == "Stephen Curry"
        assert player.fg3m == 5.0
        assert player.fg3_pct == pytest.approx(0.417)

    def test_parse_empty_result_set(self):
        """Empty rowSet yields no players."""
        raw = {
            "resultSets": [
                {
                    "name": "LeagueDashPTShots",
                    "headers": self._headers(),
                    "rowSet": [],
                }
            ]
        }

        response = LeagueDashPlayerPtShotResponse.model_validate(raw)

        assert response.players == []
