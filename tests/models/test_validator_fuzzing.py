"""Hypothesis-based fuzzing tests for model validators.

These tests use property-based testing to ensure validators handle
arbitrary input types gracefully without crashing.
"""

import pytest
from hypothesis import given, settings, strategies as st
from pydantic import ValidationError

from fastbreak.models.common.result_set import (
    is_tabular_response,
    named_result_sets_validator,
    tabular_validator,
)
from fastbreak.models.league_dash_team_shot_locations import (
    LeagueDashTeamShotLocationsResponse,
    _get_result_set,
    _parse_shot_locations,
)
from fastbreak.models.player_estimated_metrics import PlayerEstimatedMetricsResponse
from fastbreak.models.team_estimated_metrics import TeamEstimatedMetricsResponse

# =============================================================================
# Strategies for generating test data
# =============================================================================

# Strategy for arbitrary JSON-like values (excluding extremely deep nesting)
json_primitives = st.one_of(
    st.none(),
    st.booleans(),
    st.integers(),
    st.floats(allow_nan=False, allow_infinity=False),
    st.text(max_size=100),
)

# Recursive strategy for JSON-like structures
json_values = st.recursive(
    json_primitives,
    lambda children: st.one_of(
        st.lists(children, max_size=5),
        st.dictionaries(st.text(max_size=20), children, max_size=5),
    ),
    max_leaves=10,
)

# Strategy for dict-like data with random keys
random_dicts = st.dictionaries(
    st.text(min_size=1, max_size=20),
    json_values,
    max_size=10,
)


# =============================================================================
# Tests for is_tabular_response
# =============================================================================


class TestIsTabularResponseFuzzing:
    """Fuzz tests for is_tabular_response type guard."""

    @given(data=json_values)
    @settings(max_examples=200)
    def test_never_crashes_on_arbitrary_input(self, data):
        """is_tabular_response should never raise on any input type."""
        result = is_tabular_response(data)
        assert isinstance(result, bool)

    @given(
        data=st.one_of(st.none(), st.integers(), st.floats(), st.text(), st.binary())
    )
    def test_returns_false_for_non_dict_primitives(self, data):
        """Returns False for all primitive non-dict types."""
        assert is_tabular_response(data) is False

    @given(data=st.lists(json_values, max_size=10))
    def test_returns_false_for_lists(self, data):
        """Returns False for any list, even if it contains dicts."""
        assert is_tabular_response(data) is False

    @given(keys=st.lists(st.text(min_size=1, max_size=20), min_size=1, max_size=10))
    def test_returns_false_for_dicts_without_result_sets(self, keys):
        """Returns False for dicts that don't have 'resultSets' key."""
        # Filter out the key we're testing for
        filtered_keys = [k for k in keys if k != "resultSets"]
        if not filtered_keys:
            return  # Skip if all keys were 'resultSets'

        data = {k: "value" for k in filtered_keys}
        assert is_tabular_response(data) is False

    @given(value=json_values)
    def test_returns_true_when_result_sets_key_present(self, value):
        """Returns True for any dict with 'resultSets' key, regardless of value."""
        data = {"resultSets": value}
        assert is_tabular_response(data) is True


# =============================================================================
# Tests for tabular_validator
# =============================================================================


class TestTabularValidatorFuzzing:
    """Fuzz tests for tabular_validator factory."""

    @given(data=json_values)
    @settings(max_examples=200)
    def test_passthrough_never_crashes(self, data):
        """Validator passthrough should never crash on any input."""
        validator = tabular_validator("items")

        # Should not raise - either parses or passes through
        try:
            result = validator(data)
            # If it didn't raise, result should be dict-like or the original
            assert result is not None or data is None
        except (KeyError, TypeError, ValueError):
            # These are acceptable errors when data has resultSets but wrong structure
            pass

    @given(
        field_name=st.text(min_size=1, max_size=20).filter(lambda x: x.isidentifier()),
        index=st.integers(min_value=0, max_value=10),
    )
    def test_validator_creation_with_various_params(self, field_name, index):
        """Validator can be created with various field names and indices."""
        validator = tabular_validator(field_name, index=index)
        assert callable(validator)

    @given(data=random_dicts)
    def test_passthrough_returns_original_for_non_tabular(self, data):
        """Non-tabular data passes through unchanged."""
        if "resultSets" in data:
            return  # Skip tabular-like data

        validator = tabular_validator("items")
        result = validator(data)
        assert result == data


# =============================================================================
# Tests for named_result_sets_validator
# =============================================================================


class TestNamedResultSetsValidatorFuzzing:
    """Fuzz tests for named_result_sets_validator factory."""

    @given(data=json_values)
    @settings(max_examples=200)
    def test_passthrough_never_crashes_on_non_tabular(self, data):
        """Validator should not crash when passing through non-tabular data."""
        if isinstance(data, dict) and "resultSets" in data:
            return  # Skip - tabular data may raise ValueError for missing names

        validator = named_result_sets_validator({"items": "Items"})
        result = validator(data)
        # Non-tabular data should pass through unchanged
        assert result == data

    @given(
        mappings=st.dictionaries(
            st.text(min_size=1, max_size=20).filter(lambda x: x.isidentifier()),
            st.text(min_size=1, max_size=20),
            min_size=1,
            max_size=5,
        )
    )
    def test_validator_creation_with_various_mappings(self, mappings):
        """Validator can be created with various field mappings."""
        validator = named_result_sets_validator(mappings)
        assert callable(validator)


# =============================================================================
# Tests for shot locations parser
# =============================================================================


class TestShotLocationsParserFuzzing:
    """Fuzz tests for shot locations parsing functions."""

    @given(data=random_dicts)
    @settings(max_examples=200)
    def test_get_result_set_never_crashes(self, data):
        """_get_result_set should handle any dict without crashing."""
        result = _get_result_set(data)
        assert result is None or isinstance(result, dict)

    @given(data=random_dicts)
    @settings(max_examples=200)
    def test_parse_shot_locations_never_crashes(self, data):
        """_parse_shot_locations should handle any dict without crashing."""
        result = _parse_shot_locations(data)
        assert isinstance(result, list)

    @given(data=json_values)
    @settings(max_examples=200)
    def test_response_model_handles_arbitrary_input(self, data):
        """Response model should handle arbitrary input gracefully."""
        try:
            response = LeagueDashTeamShotLocationsResponse.model_validate(data)
            # If validation succeeds, teams should be a list
            assert isinstance(response.teams, list)
        except ValidationError:
            # Validation errors are expected for invalid data
            pass


# =============================================================================
# Tests for estimated metrics validators
# =============================================================================


class TestEstimatedMetricsValidatorsFuzzing:
    """Fuzz tests for estimated metrics response models."""

    @given(data=json_values)
    @settings(max_examples=200)
    def test_player_estimated_metrics_handles_arbitrary_input(self, data):
        """PlayerEstimatedMetricsResponse should handle arbitrary input."""
        try:
            response = PlayerEstimatedMetricsResponse.model_validate(data)
            assert isinstance(response.players, list)
        except ValidationError:
            # Validation errors are expected for invalid data
            pass

    @given(data=json_values)
    @settings(max_examples=200)
    def test_team_estimated_metrics_handles_arbitrary_input(self, data):
        """TeamEstimatedMetricsResponse should handle arbitrary input."""
        try:
            response = TeamEstimatedMetricsResponse.model_validate(data)
            assert isinstance(response.teams, list)
        except ValidationError:
            # Validation errors are expected for invalid data
            pass

    @given(data=random_dicts)
    def test_player_metrics_passthrough_for_non_matching_dicts(self, data):
        """Player metrics validator passes through dicts without 'resultSet'."""
        if "resultSet" in data:
            return  # Skip matching data

        try:
            # Should either validate or raise ValidationError, not crash
            PlayerEstimatedMetricsResponse.model_validate(data)
        except ValidationError:
            pass  # Expected for non-matching data

    @given(data=random_dicts)
    def test_team_metrics_passthrough_for_non_matching_dicts(self, data):
        """Team metrics validator passes through dicts without 'resultSet'."""
        if "resultSet" in data:
            return  # Skip matching data

        try:
            # Should either validate or raise ValidationError, not crash
            TeamEstimatedMetricsResponse.model_validate(data)
        except ValidationError:
            pass  # Expected for non-matching data


# =============================================================================
# Edge case tests with specific malformed inputs
# =============================================================================


class TestMalformedInputEdgeCases:
    """Test specific edge cases that might cause issues."""

    @pytest.mark.parametrize(
        "data",
        [
            {"resultSets": None},
            {"resultSets": "not a list"},
            {"resultSets": 123},
            {"resultSets": []},
            {"resultSets": [None]},
            {"resultSets": [123]},
            {"resultSets": ["string"]},
            {"resultSets": [{"no_headers": True}]},
            {"resultSets": [{"headers": None, "rowSet": []}]},
            {"resultSets": [{"headers": [], "rowSet": None}]},
            {"resultSets": [{"headers": "not_list", "rowSet": []}]},
            {"resultSets": [{"headers": [], "rowSet": "not_list"}]},
            {"resultSet": None},
            {"resultSet": "not a dict"},
            {"resultSet": {"headers": None}},
            {"resultSet": {"rowSet": None}},
            {"resultSet": {"headers": "bad", "rowSet": []}},
        ],
    )
    def test_is_tabular_response_with_malformed_result_sets(self, data):
        """is_tabular_response handles various malformed resultSets structures."""
        # Should not crash
        result = is_tabular_response(data)
        # Only True if resultSets key exists (regardless of value)
        assert result == ("resultSets" in data)

    @pytest.mark.parametrize(
        "data",
        [
            {"resultSets": None},
            {"resultSets": []},
            {"resultSets": [None]},
            {"resultSets": [{"rowSet": []}]},  # Missing headers
            {"resultSets": {"ShotLocations": None}},
            {"resultSets": {"ShotLocations": "bad"}},
        ],
    )
    def test_shot_locations_parser_with_malformed_data(self, data):
        """Shot locations parser handles malformed data without crashing."""
        result = _parse_shot_locations(data)
        assert isinstance(result, list)

    @pytest.mark.parametrize(
        "data",
        [
            {"resultSet": None},
            {"resultSet": []},
            {"resultSet": "string"},
            {"resultSet": {"headers": None, "rowSet": []}},
            {"resultSet": {"headers": [], "rowSet": None}},
        ],
    )
    def test_estimated_metrics_with_malformed_result_set(self, data):
        """Estimated metrics validators handle malformed resultSet."""
        # Should not crash - may raise ValidationError
        try:
            PlayerEstimatedMetricsResponse.model_validate(data)
        except (ValidationError, TypeError):
            pass

        try:
            TeamEstimatedMetricsResponse.model_validate(data)
        except (ValidationError, TypeError):
            pass


# =============================================================================
# Regression tests for specific bugs
# =============================================================================


class TestValidatorRegressions:
    """Regression tests for previously discovered issues."""

    def test_empty_dict_does_not_crash_validators(self):
        """Empty dict should not crash any validator."""
        assert is_tabular_response({}) is False

        validator = tabular_validator("items")
        assert validator({}) == {}

        named_validator = named_result_sets_validator({"items": "Items"})
        assert named_validator({}) == {}

    def test_deeply_nested_structure_does_not_crash(self):
        """Deeply nested structures should not cause stack overflow."""
        # Create a moderately deep structure
        data: dict = {"level": 0}
        current = data
        for i in range(50):
            current["nested"] = {"level": i + 1}
            current = current["nested"]

        assert is_tabular_response(data) is False

    def test_large_list_in_result_sets_value(self):
        """Large list as resultSets value should not crash."""
        data = {"resultSets": list(range(1000))}
        assert is_tabular_response(data) is True

        # Parsing will fail but shouldn't crash
        result = _parse_shot_locations(data)
        assert isinstance(result, list)
