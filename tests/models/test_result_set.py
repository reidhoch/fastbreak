import pytest

from fastbreak.models import (
    is_tabular_response,
    parse_result_set,
    parse_result_set_by_name,
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
