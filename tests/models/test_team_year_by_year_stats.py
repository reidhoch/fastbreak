"""Tests for team year by year stats models."""

import pytest

from fastbreak.models import TeamYearStats, TeamYearByYearStatsResponse


class TestTeamYearStats:
    """Tests for TeamYearStats model."""

    @pytest.fixture
    def sample_season_data(self) -> dict:
        """Sample team season data from the API."""
        return {
            "TEAM_ID": 1610612747,
            "TEAM_CITY": "Los Angeles",
            "TEAM_NAME": "Lakers",
            "YEAR": "2023-24",
            "GP": 82,
            "WINS": 47,
            "LOSSES": 35,
            "WIN_PCT": 0.573,
            "CONF_RANK": 7,
            "DIV_RANK": 3,
            "PO_WINS": 5,
            "PO_LOSSES": 4,
            "CONF_COUNT": 1,
            "DIV_COUNT": 0,
            "NBA_FINALS_APPEARANCE": "N/A",
            "FGM": 42.5,
            "FGA": 89.2,
            "FG_PCT": 0.476,
            "FG3M": 12.3,
            "FG3A": 33.5,
            "FG3_PCT": 0.367,
            "FTM": 18.2,
            "FTA": 23.5,
            "FT_PCT": 0.775,
            "OREB": 10.5,
            "DREB": 34.2,
            "REB": 44.7,
            "AST": 26.3,
            "PF": 19.8,
            "STL": 7.5,
            "TOV": 13.2,
            "BLK": 5.3,
            "PTS": 115.5,
            "PTS_RANK": 8,
        }

    def test_parse_season(self, sample_season_data: dict):
        """TeamYearStats parses API data correctly."""
        season = TeamYearStats.model_validate(sample_season_data)

        assert season.team_id == 1610612747
        assert season.team_city == "Los Angeles"
        assert season.team_name == "Lakers"
        assert season.year == "2023-24"
        assert season.gp == 82
        assert season.wins == 47
        assert season.losses == 35
        assert season.win_pct == pytest.approx(0.573)
        assert season.conf_rank == 7
        assert season.div_rank == 3
        assert season.conf_count == 1
        assert season.div_count == 0

    def test_parse_season_with_null_conf_div_counts(self):
        """TeamYearStats handles null conference/division counts.

        Historical seasons before the modern conference/division structure
        return null for CONF_COUNT and DIV_COUNT.
        """
        data = {
            "TEAM_ID": 1610612747,
            "TEAM_CITY": "Minneapolis",
            "TEAM_NAME": "Lakers",
            "YEAR": "1949-50",
            "GP": 68,
            "WINS": 51,
            "LOSSES": 17,
            "WIN_PCT": 0.750,
            "CONF_RANK": 1,
            "DIV_RANK": 1,
            "PO_WINS": 10,
            "PO_LOSSES": 4,
            "CONF_COUNT": None,  # Not tracked for historical seasons
            "DIV_COUNT": None,  # Not tracked for historical seasons
            "NBA_FINALS_APPEARANCE": "League Champion",
            "FGM": 28.5,
            "FGA": 75.0,
            "FG_PCT": 0.380,
            "FG3M": 0.0,
            "FG3A": 0.0,
            "FG3_PCT": 0.0,
            "FTM": 22.0,
            "FTA": 30.0,
            "FT_PCT": 0.733,
            "OREB": 15.0,
            "DREB": 30.0,
            "REB": 45.0,
            "AST": 18.0,
            "PF": 23.0,
            "STL": 8.0,
            "TOV": 15.0,
            "BLK": 3.0,
            "PTS": 79.0,
            "PTS_RANK": 1,
        }

        season = TeamYearStats.model_validate(data)

        assert season.year == "1949-50"
        assert season.team_city == "Minneapolis"
        assert season.conf_count is None
        assert season.div_count is None
        assert season.nba_finals_appearance == "League Champion"


class TestTeamYearByYearStatsResponse:
    """Tests for TeamYearByYearStatsResponse model."""

    def test_parse_tabular_response(self):
        """TeamYearByYearStatsResponse parses tabular resultSets format."""
        data = {
            "resultSets": [
                {
                    "name": "TeamStats",
                    "headers": [
                        "TEAM_ID",
                        "TEAM_CITY",
                        "TEAM_NAME",
                        "YEAR",
                        "GP",
                        "WINS",
                        "LOSSES",
                        "WIN_PCT",
                        "CONF_RANK",
                        "DIV_RANK",
                        "PO_WINS",
                        "PO_LOSSES",
                        "CONF_COUNT",
                        "DIV_COUNT",
                        "NBA_FINALS_APPEARANCE",
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
                        "PF",
                        "STL",
                        "TOV",
                        "BLK",
                        "PTS",
                        "PTS_RANK",
                    ],
                    "rowSet": [
                        [
                            1610612747,
                            "Los Angeles",
                            "Lakers",
                            "2023-24",
                            82,
                            47,
                            35,
                            0.573,
                            7,
                            3,
                            5,
                            4,
                            1,
                            0,
                            "N/A",
                            42.5,
                            89.2,
                            0.476,
                            12.3,
                            33.5,
                            0.367,
                            18.2,
                            23.5,
                            0.775,
                            10.5,
                            34.2,
                            44.7,
                            26.3,
                            19.8,
                            7.5,
                            13.2,
                            5.3,
                            115.5,
                            8,
                        ],
                    ],
                }
            ]
        }

        response = TeamYearByYearStatsResponse.model_validate(data)

        assert len(response.seasons) == 1
        assert response.seasons[0].year == "2023-24"
        assert response.seasons[0].team_name == "Lakers"

    def test_parse_empty_response(self):
        """TeamYearByYearStatsResponse handles empty seasons list."""
        data = {
            "resultSets": [
                {
                    "name": "TeamStats",
                    "headers": [
                        "TEAM_ID",
                        "TEAM_CITY",
                        "TEAM_NAME",
                        "YEAR",
                        "GP",
                        "WINS",
                        "LOSSES",
                        "WIN_PCT",
                        "CONF_RANK",
                        "DIV_RANK",
                        "PO_WINS",
                        "PO_LOSSES",
                        "CONF_COUNT",
                        "DIV_COUNT",
                        "NBA_FINALS_APPEARANCE",
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
                        "PF",
                        "STL",
                        "TOV",
                        "BLK",
                        "PTS",
                        "PTS_RANK",
                    ],
                    "rowSet": [],
                }
            ]
        }

        response = TeamYearByYearStatsResponse.model_validate(data)

        assert response.seasons == []
