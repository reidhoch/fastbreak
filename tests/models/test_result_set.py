import pytest

from fastbreak.models.common.result_set import (
    is_tabular_response,
    named_result_sets_validator,
    parse_result_set,
    parse_result_set_by_name,
    parse_single_result_set,
    tabular_validator,
)


class TestIsTabularResponse:
    """Tests for is_tabular_response helper."""

    def test_returns_true_for_tabular_format(self):
        """Returns True when data has resultSets key."""
        data = {"resultSets": [{"headers": [], "rowSet": []}]}
        assert is_tabular_response(data) is True

    def test_returns_false_for_structured_format(self):
        """Returns False for structured JSON without resultSets."""
        data = {"game": {"gameId": "123"}, "meta": {}}
        assert is_tabular_response(data) is False

    def test_returns_false_for_non_dict(self):
        """Returns False for non-dict values."""
        assert is_tabular_response([1, 2, 3]) is False
        assert is_tabular_response("string") is False
        assert is_tabular_response(None) is False
        assert is_tabular_response(123) is False


class TestParseResultSet:
    """Tests for parse_result_set helper."""

    def test_parses_simple_result_set(self):
        """Parses headers and rows into list of dicts."""
        data = {
            "resultSets": [
                {
                    "headers": ["id", "name", "score"],
                    "rowSet": [
                        [1, "Alice", 100],
                        [2, "Bob", 95],
                    ],
                }
            ]
        }

        result = parse_result_set(data)

        assert len(result) == 2
        assert result[0] == {"id": 1, "name": "Alice", "score": 100}
        assert result[1] == {"id": 2, "name": "Bob", "score": 95}

    def test_parses_specific_index(self):
        """Parses resultSet at specified index."""
        data = {
            "resultSets": [
                {"headers": ["a"], "rowSet": [[1]]},
                {"headers": ["b"], "rowSet": [[2]]},
                {"headers": ["c"], "rowSet": [[3]]},
            ]
        }

        result = parse_result_set(data, index=1)

        assert result == [{"b": 2}]

    def test_handles_empty_row_set(self):
        """Returns empty list for empty rowSet."""
        data = {"resultSets": [{"headers": ["id"], "rowSet": []}]}

        result = parse_result_set(data)

        assert result == []

    def test_handles_null_values(self):
        """Preserves null values in rows."""
        data = {
            "resultSets": [
                {
                    "headers": ["id", "name", "value"],
                    "rowSet": [[1, None, 100]],
                }
            ]
        }

        result = parse_result_set(data)

        assert result[0]["name"] is None


class TestParseResultSetByName:
    """Tests for parse_result_set_by_name helper."""

    def test_finds_result_set_by_name(self):
        """Finds and parses resultSet by its name field."""
        data = {
            "resultSets": [
                {"name": "Players", "headers": ["id"], "rowSet": [[1]]},
                {"name": "Teams", "headers": ["id"], "rowSet": [[100]]},
            ]
        }

        result = parse_result_set_by_name(data, "Teams")

        assert result == [{"id": 100}]

    def test_raises_for_missing_name(self):
        """Raises ValueError when name not found."""
        data = {
            "resultSets": [
                {"name": "Players", "headers": ["id"], "rowSet": [[1]]},
            ]
        }

        with pytest.raises(ValueError, match="No resultSet named 'Missing'"):
            parse_result_set_by_name(data, "Missing")

    def test_error_message_lists_available_names(self):
        """Error message includes available resultSet names."""
        data = {
            "resultSets": [
                {"name": "Alpha", "headers": [], "rowSet": []},
                {"name": "Beta", "headers": [], "rowSet": []},
            ]
        }

        with pytest.raises(ValueError, match=r"Available: \['Alpha', 'Beta'\]"):
            parse_result_set_by_name(data, "Gamma")


class TestParseSingleResultSet:
    """Tests for parse_single_result_set helper."""

    def test_returns_first_row_from_named_result_set(self):
        """Returns first row as dict when result set has data."""
        data = {
            "resultSets": [
                {
                    "name": "Stats",
                    "headers": ["id", "value"],
                    "rowSet": [[1, 100], [2, 200]],
                },
            ]
        }

        result = parse_single_result_set(data, "Stats")

        assert result == {"id": 1, "value": 100}

    def test_returns_none_for_empty_result_set(self):
        """Returns None when result set has no rows."""
        data = {
            "resultSets": [
                {"name": "Empty", "headers": ["id"], "rowSet": []},
            ]
        }

        result = parse_single_result_set(data, "Empty")

        assert result is None

    def test_raises_for_missing_name(self):
        """Raises ValueError when name not found."""
        data = {"resultSets": [{"name": "Other", "headers": [], "rowSet": []}]}

        with pytest.raises(ValueError, match="No resultSet named 'Missing'"):
            parse_single_result_set(data, "Missing")


class TestTabularValidator:
    """Tests for tabular_validator factory function."""

    def test_creates_validator_that_parses_tabular_data(self):
        """Created validator parses tabular data into specified field."""
        validator = tabular_validator("items")
        data = {
            "resultSets": [
                {"headers": ["id", "name"], "rowSet": [[1, "Alice"], [2, "Bob"]]}
            ]
        }

        result = validator(data)

        assert result == {
            "items": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
        }

    def test_validator_passes_through_non_tabular_data(self):
        """Validator returns non-tabular data unchanged."""
        validator = tabular_validator("items")
        data = {"items": [{"id": 1}]}  # Already structured

        result = validator(data)

        assert result == {"items": [{"id": 1}]}

    def test_validator_uses_specified_index(self):
        """Validator parses result set at specified index."""
        validator = tabular_validator("second", index=1)
        data = {
            "resultSets": [
                {"headers": ["a"], "rowSet": [[1]]},
                {"headers": ["b"], "rowSet": [[2]]},
            ]
        }

        result = validator(data)

        assert result == {"second": [{"b": 2}]}

    def test_validator_uses_correct_field_name(self):
        """Validator populates the specified field name."""
        validator = tabular_validator("players")
        data = {"resultSets": [{"headers": ["id"], "rowSet": [[1]]}]}

        result = validator(data)

        assert "players" in result
        assert result["players"] == [{"id": 1}]

    def test_validator_default_index_is_zero(self):
        """Validator defaults to first result set (index 0)."""
        validator = tabular_validator("first")
        data = {
            "resultSets": [
                {"headers": ["first"], "rowSet": [[1]]},
                {"headers": ["second"], "rowSet": [[2]]},
            ]
        }

        result = validator(data)

        assert result == {"first": [{"first": 1}]}


class TestNamedResultSetsValidator:
    """Tests for named_result_sets_validator factory function."""

    def test_parses_multiple_named_result_sets(self):
        """Validator parses multiple named result sets into fields."""
        validator = named_result_sets_validator(
            {
                "players": "Players",
                "teams": "Teams",
            }
        )
        data = {
            "resultSets": [
                {"name": "Players", "headers": ["id"], "rowSet": [[1], [2]]},
                {"name": "Teams", "headers": ["id"], "rowSet": [[100]]},
            ]
        }

        result = validator(data)

        assert result["players"] == [{"id": 1}, {"id": 2}]
        assert result["teams"] == [{"id": 100}]

    def test_passes_through_non_tabular_data(self):
        """Validator returns non-tabular data unchanged."""
        validator = named_result_sets_validator({"players": "Players"})
        data = {"players": [{"id": 1}]}  # Already structured

        result = validator(data)

        assert result == {"players": [{"id": 1}]}

    def test_handles_single_row_mapping(self):
        """Validator extracts first row when is_single=True."""
        validator = named_result_sets_validator(
            {
                "total": ("TotalStats", True),
            }
        )
        data = {
            "resultSets": [
                {"name": "TotalStats", "headers": ["sum"], "rowSet": [[100]]},
            ]
        }

        result = validator(data)

        assert result["total"] == {"sum": 100}

    def test_single_row_returns_none_for_empty(self):
        """Single row mapping returns None when result set is empty."""
        validator = named_result_sets_validator(
            {
                "total": ("TotalStats", True),
            }
        )
        data = {
            "resultSets": [
                {"name": "TotalStats", "headers": ["sum"], "rowSet": []},
            ]
        }

        result = validator(data)

        assert result["total"] is None

    def test_mixed_list_and_single_mappings(self):
        """Validator handles both list and single-row mappings together."""
        validator = named_result_sets_validator(
            {
                "items": "Items",  # String means list
                "summary": ("Summary", True),  # Tuple with True means single
            }
        )
        data = {
            "resultSets": [
                {"name": "Items", "headers": ["id"], "rowSet": [[1], [2], [3]]},
                {"name": "Summary", "headers": ["count"], "rowSet": [[3]]},
            ]
        }

        result = validator(data)

        assert result["items"] == [{"id": 1}, {"id": 2}, {"id": 3}]
        assert result["summary"] == {"count": 3}

    def test_distinguishes_string_vs_tuple_mapping(self):
        """Validator correctly distinguishes string (list) from tuple (maybe single)."""
        # String mapping always returns a list
        validator_list = named_result_sets_validator({"data": "Results"})
        # Tuple with False also returns a list
        validator_tuple_false = named_result_sets_validator(
            {"data": ("Results", False)}
        )

        data = {
            "resultSets": [
                {"name": "Results", "headers": ["id"], "rowSet": [[1]]},
            ]
        }

        result_list = validator_list(data)
        result_tuple = validator_tuple_false(data)

        # Both should return a list
        assert result_list["data"] == [{"id": 1}]
        assert result_tuple["data"] == [{"id": 1}]

    def test_multiple_single_row_mappings(self):
        """Validator handles multiple single-row mappings."""
        validator = named_result_sets_validator(
            {
                "stats1": ("Stats1", True),
                "stats2": ("Stats2", True),
            }
        )
        data = {
            "resultSets": [
                {"name": "Stats1", "headers": ["val"], "rowSet": [[10]]},
                {"name": "Stats2", "headers": ["val"], "rowSet": [[20]]},
            ]
        }

        result = validator(data)

        assert result["stats1"] == {"val": 10}
        assert result["stats2"] == {"val": 20}

    def test_raises_for_missing_result_set_name(self):
        """Validator raises ValueError when named result set is missing."""
        validator = named_result_sets_validator({"data": "Missing"})
        data = {
            "resultSets": [
                {"name": "Other", "headers": [], "rowSet": []},
            ]
        }

        with pytest.raises(ValueError, match="No resultSet named 'Missing'"):
            validator(data)
