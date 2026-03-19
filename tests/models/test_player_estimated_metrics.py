"""Tests for PlayerEstimatedMetricsResponse validator branches."""

import pytest
from pydantic import ValidationError

from fastbreak.models.player_estimated_metrics import PlayerEstimatedMetricsResponse


def _make_valid_result_set_data():
    """Build a minimal valid resultSet payload for player estimated metrics."""
    return {
        "resultSet": {
            "headers": [
                "PLAYER_ID",
                "PLAYER_NAME",
                "GP",
                "W",
                "L",
                "W_PCT",
                "MIN",
                "E_OFF_RATING",
                "E_DEF_RATING",
                "E_NET_RATING",
                "E_AST_RATIO",
                "E_OREB_PCT",
                "E_DREB_PCT",
                "E_REB_PCT",
                "E_TOV_PCT",
                "E_USG_PCT",
                "E_PACE",
                "GP_RANK",
                "W_RANK",
                "L_RANK",
                "W_PCT_RANK",
                "MIN_RANK",
                "E_OFF_RATING_RANK",
                "E_DEF_RATING_RANK",
                "E_NET_RATING_RANK",
                "E_AST_RATIO_RANK",
                "E_OREB_PCT_RANK",
                "E_DREB_PCT_RANK",
                "E_REB_PCT_RANK",
                "E_TOV_PCT_RANK",
                "E_USG_PCT_RANK",
                "E_PACE_RANK",
            ],
            "rowSet": [
                [
                    201939,
                    "Stephen Curry",
                    74,
                    50,
                    24,
                    0.676,
                    32.5,
                    120.1,
                    112.3,
                    7.8,
                    0.35,
                    0.03,
                    0.12,
                    0.15,
                    0.08,
                    0.30,
                    101.2,
                    1,
                    2,
                    15,
                    3,
                    5,
                    2,
                    20,
                    5,
                    10,
                    40,
                    8,
                    12,
                    25,
                    15,
                    7,
                ],
            ],
        }
    }


class TestPlayerEstimatedMetricsValidatorPassthrough:
    """Tests for from_result_set validator passthrough branches."""

    def test_non_dict_data_returns_data(self):
        """Validator returns non-dict data unchanged (early return branch)."""
        raw = [1, 2, 3]
        func = PlayerEstimatedMetricsResponse.from_result_set.__func__
        result = func(PlayerEstimatedMetricsResponse, raw)
        assert result is raw

    def test_non_dict_string_returns_data(self):
        """Validator returns string data unchanged."""
        raw = "not a dict"
        func = PlayerEstimatedMetricsResponse.from_result_set.__func__
        result = func(PlayerEstimatedMetricsResponse, raw)
        assert result is raw

    def test_non_dict_int_returns_data(self):
        """Validator returns int data unchanged."""
        raw = 42
        func = PlayerEstimatedMetricsResponse.from_result_set.__func__
        result = func(PlayerEstimatedMetricsResponse, raw)
        assert result is raw

    def test_missing_result_set_key_returns_data(self):
        """Validator returns data when 'resultSet' key is missing (early return branch)."""
        raw = {"players": [], "other_key": "value"}
        func = PlayerEstimatedMetricsResponse.from_result_set.__func__
        result = func(PlayerEstimatedMetricsResponse, raw)
        assert result is raw

    def test_result_set_is_none_returns_data(self):
        """Validator returns data when resultSet is None (falsy value, first guard)."""
        raw = {"resultSet": None}
        func = PlayerEstimatedMetricsResponse.from_result_set.__func__
        result = func(PlayerEstimatedMetricsResponse, raw)
        assert result is raw

    def test_result_set_is_empty_list_returns_data(self):
        """Validator returns data when resultSet is [] (falsy value, first guard)."""
        raw = {"resultSet": []}
        func = PlayerEstimatedMetricsResponse.from_result_set.__func__
        result = func(PlayerEstimatedMetricsResponse, raw)
        assert result is raw

    def test_result_set_is_not_dict_returns_data(self):
        """Validator returns data when resultSet is not a dict (isinstance guard)."""
        raw = {"resultSet": "string_value"}
        func = PlayerEstimatedMetricsResponse.from_result_set.__func__
        result = func(PlayerEstimatedMetricsResponse, raw)
        assert result is raw

    def test_result_set_is_list_returns_data(self):
        """Validator returns data when resultSet is a list instead of dict."""
        raw = {"resultSet": [{"headers": [], "rowSet": []}]}
        func = PlayerEstimatedMetricsResponse.from_result_set.__func__
        result = func(PlayerEstimatedMetricsResponse, raw)
        assert result is raw

    def test_result_set_is_truthy_non_dict_returns_data(self):
        """Validator returns data when resultSet is truthy but not a dict (isinstance guard)."""
        raw = {"resultSet": 42}
        func = PlayerEstimatedMetricsResponse.from_result_set.__func__
        result = func(PlayerEstimatedMetricsResponse, raw)
        assert result is raw


class TestPlayerEstimatedMetricsValidParsing:
    """Tests for successful parsing through the validator."""

    def test_valid_result_set_parses_players(self):
        """Valid resultSet data is parsed into players list."""
        data = _make_valid_result_set_data()
        response = PlayerEstimatedMetricsResponse.model_validate(data)
        assert len(response.players) == 1
        assert response.players[0].player_name == "Stephen Curry"
        assert response.players[0].player_id == 201939

    def test_mismatched_header_row_lengths_raises(self):
        """Strict zip raises when row has different length than headers."""
        data = {
            "resultSet": {
                "headers": ["PLAYER_ID", "PLAYER_NAME"],
                "rowSet": [[201939, "Curry", "extra_col"]],
            }
        }
        with pytest.raises((ValidationError, ValueError)):
            PlayerEstimatedMetricsResponse.model_validate(data)
