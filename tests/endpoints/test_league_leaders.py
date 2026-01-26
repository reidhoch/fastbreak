"""Tests for LeagueLeaders endpoint."""

from fastbreak.endpoints import LeagueLeaders
from fastbreak.models import LeagueLeadersResponse
from fastbreak.models.league_leaders import (
    _is_singular_result_set,
    _parse_singular_result_set,
)


class TestLeagueLeaders:
    """Tests for LeagueLeaders endpoint."""

    def test_init_with_defaults(self):
        """LeagueLeaders uses sensible defaults."""
        endpoint = LeagueLeaders()

        assert endpoint.season == "2024-25"
        assert endpoint.season_type == "Regular Season"
        assert endpoint.per_mode == "PerGame"
        assert endpoint.stat_category == "PTS"
        assert endpoint.scope == "S"
        assert endpoint.league_id == "00"
        assert endpoint.active_flag is None

    def test_init_with_custom_season(self):
        """LeagueLeaders accepts custom season."""
        endpoint = LeagueLeaders(season="2023-24")

        assert endpoint.season == "2023-24"

    def test_init_with_totals_mode(self):
        """LeagueLeaders accepts Totals mode."""
        endpoint = LeagueLeaders(per_mode="Totals")

        assert endpoint.per_mode == "Totals"

    def test_init_with_playoffs(self):
        """LeagueLeaders accepts Playoffs season type."""
        endpoint = LeagueLeaders(season_type="Playoffs")

        assert endpoint.season_type == "Playoffs"

    def test_init_with_different_stat_category(self):
        """LeagueLeaders accepts different stat categories."""
        endpoint = LeagueLeaders(stat_category="AST")

        assert endpoint.stat_category == "AST"

    def test_init_with_rookie_scope(self):
        """LeagueLeaders accepts rookie scope."""
        endpoint = LeagueLeaders(scope="RS")

        assert endpoint.scope == "RS"

    def test_params_returns_correct_dict(self):
        """params() returns correctly formatted parameters."""
        endpoint = LeagueLeaders(
            season="2024-25",
            season_type="Regular Season",
            per_mode="PerGame",
            stat_category="PTS",
            scope="S",
            league_id="00",
        )

        params = endpoint.params()

        assert params == {
            "Season": "2024-25",
            "SeasonType": "Regular Season",
            "PerMode": "PerGame",
            "StatCategory": "PTS",
            "Scope": "S",
            "LeagueID": "00",
        }

    def test_params_includes_active_flag(self):
        """params() includes active_flag when set."""
        endpoint = LeagueLeaders(active_flag="Y")

        params = endpoint.params()

        assert params["ActiveFlag"] == "Y"

    def test_path_is_correct(self):
        """LeagueLeaders has correct API path."""
        endpoint = LeagueLeaders()

        assert endpoint.path == "leagueleaders"

    def test_response_model_is_correct(self):
        """LeagueLeaders uses LeagueLeadersResponse model."""
        endpoint = LeagueLeaders()

        assert endpoint.response_model is LeagueLeadersResponse

    def test_endpoint_is_frozen(self):
        """LeagueLeaders is immutable (frozen dataclass)."""
        endpoint = LeagueLeaders()

        try:
            endpoint.season = "2023-24"  # type: ignore[misc]
            frozen = False
        except AttributeError:
            frozen = True

        assert frozen, "Endpoint should be frozen (immutable)"


class TestLeagueLeadersResponse:
    """Tests for LeagueLeadersResponse model."""

    def test_parse_tabular_response(self):
        """Response parses NBA's tabular format correctly."""
        raw_response = {
            "resultSet": {
                "name": "LeagueLeaders",
                "headers": [
                    "PLAYER_ID",
                    "RANK",
                    "PLAYER",
                    "TEAM_ID",
                    "TEAM",
                    "GP",
                    "MIN",
                    "FGM",
                    "FGA",
                    "FG_PCT",
                    "FG3M",
                    "FG3A",
                    "FG3_PCT",
                    "FTM",
                    "FTA",
                    "FT_PCT",
                    "OREB",
                    "DREB",
                    "REB",
                    "AST",
                    "STL",
                    "BLK",
                    "TOV",
                    "PTS",
                    "EFF",
                ],
                "rowSet": [
                    [
                        1628983,
                        1,
                        "Shai Gilgeous-Alexander",
                        1610612760,
                        "OKC",
                        76,
                        34.2,
                        11.3,
                        21.8,
                        0.519,
                        2.1,
                        5.7,
                        0.375,
                        7.9,
                        8.8,
                        0.898,
                        0.9,
                        4.1,
                        5.0,
                        6.4,
                        1.7,
                        1.0,
                        2.4,
                        32.7,
                        33.0,
                    ],
                ],
            }
        }

        response = LeagueLeadersResponse.model_validate(raw_response)

        assert len(response.leaders) == 1

        leader = response.leaders[0]
        assert leader.player == "Shai Gilgeous-Alexander"
        assert leader.team == "OKC"
        assert leader.rank == 1
        assert leader.pts == 32.7
        assert leader.gp == 76

    def test_parse_empty_response(self):
        """Response handles empty result sets."""
        raw_response = {
            "resultSet": {
                "name": "LeagueLeaders",
                "headers": ["PLAYER_ID"],
                "rowSet": [],
            }
        }

        response = LeagueLeadersResponse.model_validate(raw_response)

        assert response.leaders == []


class TestIsSingularResultSet:
    """Tests for _is_singular_result_set TypeGuard."""

    def test_returns_true_for_singular_format(self):
        """Returns True when data has 'resultSet' key (singular)."""
        data = {"resultSet": {"headers": [], "rowSet": []}}
        assert _is_singular_result_set(data) is True

    def test_returns_false_for_plural_format(self):
        """Returns False for 'resultSets' (plural) format."""
        data = {"resultSets": [{"headers": [], "rowSet": []}]}
        assert _is_singular_result_set(data) is False

    def test_returns_false_for_non_dict(self):
        """Returns False for non-dict types."""
        assert _is_singular_result_set([1, 2, 3]) is False
        assert _is_singular_result_set("string") is False
        assert _is_singular_result_set(None) is False
        assert _is_singular_result_set(123) is False

    def test_returns_false_for_empty_dict(self):
        """Returns False for empty dict."""
        assert _is_singular_result_set({}) is False

    def test_returns_false_for_other_keys(self):
        """Returns False when dict has other keys but not resultSet."""
        data = {"other_key": "value", "another": 123}
        assert _is_singular_result_set(data) is False


class TestParseSingularResultSet:
    """Tests for _parse_singular_result_set function."""

    def test_parses_headers_and_rows(self):
        """Parses headers and rows into list of dicts."""
        data = {
            "resultSet": {
                "headers": ["ID", "NAME", "VALUE"],
                "rowSet": [
                    [1, "Alice", 100],
                    [2, "Bob", 200],
                ],
            }
        }

        result = _parse_singular_result_set(data)

        assert len(result) == 2
        assert result[0] == {"ID": 1, "NAME": "Alice", "VALUE": 100}
        assert result[1] == {"ID": 2, "NAME": "Bob", "VALUE": 200}

    def test_returns_empty_list_for_empty_rowset(self):
        """Returns empty list when rowSet is empty."""
        data = {
            "resultSet": {
                "headers": ["ID", "NAME"],
                "rowSet": [],
            }
        }

        result = _parse_singular_result_set(data)

        assert result == []

    def test_handles_single_row(self):
        """Correctly parses single row."""
        data = {
            "resultSet": {
                "headers": ["ID"],
                "rowSet": [[42]],
            }
        }

        result = _parse_singular_result_set(data)

        assert result == [{"ID": 42}]

    def test_handles_null_values(self):
        """Preserves null values in rows."""
        data = {
            "resultSet": {
                "headers": ["ID", "NULLABLE"],
                "rowSet": [[1, None]],
            }
        }

        result = _parse_singular_result_set(data)

        assert result[0]["NULLABLE"] is None

    def test_uses_correct_header_for_each_column(self):
        """Each column value is mapped to correct header."""
        data = {
            "resultSet": {
                "headers": ["A", "B", "C"],
                "rowSet": [[10, 20, 30]],
            }
        }

        result = _parse_singular_result_set(data)

        assert result[0]["A"] == 10
        assert result[0]["B"] == 20
        assert result[0]["C"] == 30
