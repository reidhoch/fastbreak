"""Tests for LeagueLeaders endpoint."""

from fastbreak.endpoints import LeagueLeaders
from fastbreak.models import LeagueLeadersResponse


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
