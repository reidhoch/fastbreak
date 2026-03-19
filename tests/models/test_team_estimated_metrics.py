"""Tests for TeamEstimatedMetricsResponse validator branches."""

import pytest
from pydantic import ValidationError

from fastbreak.models.team_estimated_metrics import TeamEstimatedMetricsResponse


def _make_valid_result_set_data():
    """Build a minimal valid resultSet payload for team estimated metrics."""
    return {
        "resultSet": {
            "headers": [
                "TEAM_NAME",
                "TEAM_ID",
                "GP",
                "W",
                "L",
                "W_PCT",
                "MIN",
                "E_OFF_RATING",
                "E_DEF_RATING",
                "E_NET_RATING",
                "E_PACE",
                "E_AST_RATIO",
                "E_OREB_PCT",
                "E_DREB_PCT",
                "E_REB_PCT",
                "E_TM_TOV_PCT",
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
                "E_TM_TOV_PCT_RANK",
                "E_PACE_RANK",
            ],
            "rowSet": [
                [
                    "Thunder",
                    1610612760,
                    82,
                    60,
                    22,
                    0.732,
                    48.0,
                    118.5,
                    108.2,
                    10.3,
                    100.5,
                    0.22,
                    0.28,
                    0.75,
                    0.52,
                    0.13,
                    1,
                    1,
                    25,
                    1,
                    1,
                    1,
                    5,
                    1,
                    3,
                    2,
                    8,
                    5,
                    10,
                    7,
                ],
            ],
        }
    }


class TestTeamEstimatedMetricsValidatorPassthrough:
    """Tests for from_result_set validator passthrough branches."""

    def test_non_dict_data_returns_data(self):
        """Validator returns non-dict data unchanged (early return branch)."""
        raw = [1, 2, 3]
        func = TeamEstimatedMetricsResponse.from_result_set.__func__
        result = func(TeamEstimatedMetricsResponse, raw)
        assert result is raw

    def test_non_dict_string_returns_data(self):
        """Validator returns string data unchanged."""
        raw = "not a dict"
        func = TeamEstimatedMetricsResponse.from_result_set.__func__
        result = func(TeamEstimatedMetricsResponse, raw)
        assert result is raw

    def test_missing_result_set_key_returns_data(self):
        """Validator returns data when 'resultSet' key is missing (early return branch)."""
        raw = {"teams": [], "other_key": "value"}
        func = TeamEstimatedMetricsResponse.from_result_set.__func__
        result = func(TeamEstimatedMetricsResponse, raw)
        assert result is raw

    def test_result_set_is_none_returns_data(self):
        """Validator returns data when resultSet is None (falsy value, first guard)."""
        raw = {"resultSet": None}
        func = TeamEstimatedMetricsResponse.from_result_set.__func__
        result = func(TeamEstimatedMetricsResponse, raw)
        assert result is raw

    def test_result_set_is_empty_list_returns_data(self):
        """Validator returns data when resultSet is [] (falsy value, first guard)."""
        raw = {"resultSet": []}
        func = TeamEstimatedMetricsResponse.from_result_set.__func__
        result = func(TeamEstimatedMetricsResponse, raw)
        assert result is raw

    def test_result_set_is_not_dict_returns_data(self):
        """Validator returns data when resultSet is not a dict (isinstance guard)."""
        raw = {"resultSet": "string_value"}
        func = TeamEstimatedMetricsResponse.from_result_set.__func__
        result = func(TeamEstimatedMetricsResponse, raw)
        assert result is raw

    def test_result_set_is_list_returns_data(self):
        """Validator returns data when resultSet is a list instead of dict."""
        raw = {"resultSet": [{"headers": [], "rowSet": []}]}
        func = TeamEstimatedMetricsResponse.from_result_set.__func__
        result = func(TeamEstimatedMetricsResponse, raw)
        assert result is raw

    def test_result_set_is_truthy_non_dict_returns_data(self):
        """Validator returns data when resultSet is truthy but not a dict (isinstance guard)."""
        raw = {"resultSet": 42}
        func = TeamEstimatedMetricsResponse.from_result_set.__func__
        result = func(TeamEstimatedMetricsResponse, raw)
        assert result is raw


class TestTeamEstimatedMetricsValidParsing:
    """Tests for successful parsing through the validator."""

    def test_valid_result_set_parses_teams(self):
        """Valid resultSet data is parsed into teams list."""
        data = _make_valid_result_set_data()
        response = TeamEstimatedMetricsResponse.model_validate(data)
        assert len(response.teams) == 1
        assert response.teams[0].team_name == "Thunder"
        assert response.teams[0].team_id == 1610612760

    def test_mismatched_header_row_lengths_raises(self):
        """Strict zip raises when row has different length than headers."""
        data = {
            "resultSet": {
                "headers": ["TEAM_NAME", "TEAM_ID"],
                "rowSet": [["Thunder", 1610612760, "extra"]],
            }
        }
        with pytest.raises((ValidationError, ValueError)):
            TeamEstimatedMetricsResponse.model_validate(data)
