"""Tests for PlayerCompare endpoint."""

import pytest
from pydantic import ValidationError

from fastbreak.endpoints import PlayerCompare
from fastbreak.models import PlayerCompareResponse
from fastbreak.seasons import get_season_from_date


class TestPlayerCompare:
    """Tests for PlayerCompare endpoint."""

    def test_init_with_defaults(self):
        """PlayerCompare uses sensible defaults."""
        endpoint = PlayerCompare()

        assert endpoint.league_id == "00"
        assert endpoint.player_id_list == ""
        assert endpoint.vs_player_id_list == ""
        assert endpoint.season == get_season_from_date()
        assert endpoint.season_type == "Regular Season"
        assert endpoint.per_mode == "PerGame"
        assert endpoint.measure_type == "Base"

    def test_init_with_player_ids(self):
        """PlayerCompare accepts player ID lists."""
        endpoint = PlayerCompare(
            player_id_list="2544",
            vs_player_id_list="203999",
        )

        assert endpoint.player_id_list == "2544"
        assert endpoint.vs_player_id_list == "203999"

    def test_init_with_multiple_players(self):
        """PlayerCompare accepts comma-separated player IDs."""
        endpoint = PlayerCompare(
            player_id_list="2544,201566",
            vs_player_id_list="203999,201935",
        )

        assert endpoint.player_id_list == "2544,201566"
        assert endpoint.vs_player_id_list == "203999,201935"

    def test_init_with_optional_filters(self):
        """PlayerCompare accepts optional filters."""
        endpoint = PlayerCompare(
            player_id_list="2544",
            vs_player_id_list="203999",
            season="2023-24",
            last_n_games=10,
            outcome="W",
        )

        assert endpoint.season == "2023-24"
        assert endpoint.last_n_games == 10
        assert endpoint.outcome == "W"

    def test_params_with_required_only(self):
        """params() returns required and always-sent parameters."""
        endpoint = PlayerCompare()

        params = endpoint.params()

        assert params == {
            "LeagueID": "00",
            "PlayerIDList": "",
            "VsPlayerIDList": "",
            "Season": get_season_from_date(),
            "SeasonType": "Regular Season",
            "PerMode": "PerGame",
            "MeasureType": "Base",
            "PaceAdjust": "N",
            "PlusMinus": "N",
            "Rank": "N",
            "Month": "0",
            "OpponentTeamID": "0",
            "Period": "0",
            "LastNGames": "0",
        }

    def test_params_with_filters(self):
        """params() includes optional filters when set."""
        endpoint = PlayerCompare(
            player_id_list="2544",
            vs_player_id_list="203999",
            last_n_games=10,
            outcome="W",
            location="Home",
        )

        params = endpoint.params()

        assert params["PlayerIDList"] == "2544"
        assert params["VsPlayerIDList"] == "203999"
        assert params["LastNGames"] == "10"
        assert params["Outcome"] == "W"
        assert params["Location"] == "Home"

    def test_path_is_correct(self):
        """PlayerCompare has correct API path."""
        endpoint = PlayerCompare()

        assert endpoint.path == "playercompare"

    def test_response_model_is_correct(self):
        """PlayerCompare uses PlayerCompareResponse model."""
        endpoint = PlayerCompare()

        assert endpoint.response_model is PlayerCompareResponse

    def test_endpoint_is_frozen(self):
        """PlayerCompare is immutable (frozen dataclass)."""
        endpoint = PlayerCompare()

        with pytest.raises((AttributeError, ValidationError)):
            endpoint.season = "2023-24"  # type: ignore[misc]


class TestPlayerCompareResponse:
    """Tests for PlayerCompareResponse model."""

    def test_parse_tabular_response(self):
        """Response parses NBA's tabular format correctly."""
        raw_response = {
            "resultSets": [
                {
                    "name": "OverallCompare",
                    "headers": [
                        "GROUP_SET",
                        "DESCRIPTION",
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
                        "TOV",
                        "STL",
                        "BLK",
                        "BLKA",
                        "PF",
                        "PFD",
                        "PTS",
                        "PLUS_MINUS",
                    ],
                    "rowSet": [
                        [
                            "OVERALL",
                            "L. James's combined stats",
                            34.9,
                            9.3,
                            18.1,
                            0.513,
                            2.1,
                            5.7,
                            0.376,
                            3.7,
                            4.7,
                            0.782,
                            1.0,
                            6.8,
                            7.8,
                            8.2,
                            3.7,
                            1.0,
                            0.6,
                            0.7,
                            1.4,
                            3.8,
                            24.4,
                            -0.8,
                        ],
                        [
                            "OVERALL",
                            "N. Jokić's combined stats",
                            36.7,
                            11.2,
                            19.5,
                            0.576,
                            2.0,
                            4.7,
                            0.417,
                            5.2,
                            6.4,
                            0.8,
                            2.9,
                            9.9,
                            12.7,
                            10.2,
                            3.3,
                            1.8,
                            0.6,
                            0.9,
                            2.3,
                            5.9,
                            29.6,
                            8.5,
                        ],
                    ],
                },
                {
                    "name": "Individual",
                    "headers": [
                        "GROUP_SET",
                        "DESCRIPTION",
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
                        "TOV",
                        "STL",
                        "BLK",
                        "BLKA",
                        "PF",
                        "PFD",
                        "PTS",
                        "PLUS_MINUS",
                    ],
                    "rowSet": [
                        [
                            "INDIVIDUAL",
                            "L. James",
                            34.9,
                            9.3,
                            18.1,
                            0.513,
                            2.1,
                            5.7,
                            0.376,
                            3.7,
                            4.7,
                            0.782,
                            1.0,
                            6.8,
                            7.8,
                            8.2,
                            3.7,
                            1.0,
                            0.6,
                            0.7,
                            1.4,
                            3.8,
                            24.4,
                            -0.8,
                        ],
                        [
                            "VS INDIVIDUAL",
                            "N. Jokić",
                            36.7,
                            11.2,
                            19.5,
                            0.576,
                            2.0,
                            4.7,
                            0.417,
                            5.2,
                            6.4,
                            0.8,
                            2.9,
                            9.9,
                            12.7,
                            10.2,
                            3.3,
                            1.8,
                            0.6,
                            0.9,
                            2.3,
                            5.9,
                            29.6,
                            8.5,
                        ],
                    ],
                },
            ]
        }

        response = PlayerCompareResponse.model_validate(raw_response)

        # Check overall compare
        assert len(response.overall_compare) == 2
        lebron_overall = response.overall_compare[0]
        assert lebron_overall.group_set == "OVERALL"
        assert lebron_overall.description == "L. James's combined stats"
        assert lebron_overall.pts == 24.4
        assert lebron_overall.reb == 7.8
        assert lebron_overall.ast == 8.2

        jokic_overall = response.overall_compare[1]
        assert jokic_overall.pts == 29.6
        assert jokic_overall.reb == 12.7
        assert jokic_overall.ast == 10.2

        # Check individual
        assert len(response.individual) == 2
        lebron_ind = response.individual[0]
        assert lebron_ind.group_set == "INDIVIDUAL"
        assert lebron_ind.description == "L. James"

        jokic_ind = response.individual[1]
        assert jokic_ind.group_set == "VS INDIVIDUAL"
        assert jokic_ind.description == "N. Jokić"

    def test_parse_empty_response(self):
        """Response handles empty result sets."""
        raw_response = {
            "resultSets": [
                {
                    "name": "OverallCompare",
                    "headers": ["GROUP_SET", "DESCRIPTION"],
                    "rowSet": [],
                },
                {
                    "name": "Individual",
                    "headers": ["GROUP_SET", "DESCRIPTION"],
                    "rowSet": [],
                },
            ]
        }

        response = PlayerCompareResponse.model_validate(raw_response)

        assert response.overall_compare == []
        assert response.individual == []
