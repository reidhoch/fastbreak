"""Tests for franchise players models."""

import pytest

from fastbreak.models import FranchisePlayer, FranchisePlayersResponse


class TestFranchisePlayer:
    """Tests for FranchisePlayer model."""

    @pytest.fixture
    def sample_player_data(self) -> dict:
        """Sample franchise player data from the API."""
        return {
            "LEAGUE_ID": "00",
            "TEAM_ID": 1610612747,
            "TEAM": "Los Angeles Lakers",
            "PERSON_ID": 2544,
            "PLAYER": "LeBron James",
            "SEASON_TYPE": "Regular Season",
            "ACTIVE_WITH_TEAM": 1,
            "GP": 500,
            "FGM": 4500.0,
            "FGA": 9000.0,
            "FG_PCT": 0.500,
            "FG3M": 800.0,
            "FG3A": 2400.0,
            "FG3_PCT": 0.333,
            "FTM": 3000.0,
            "FTA": 4000.0,
            "FT_PCT": 0.750,
            "OREB": 500.0,
            "DREB": 3500.0,
            "REB": 4000.0,
            "AST": 5000.0,
            "PF": 800.0,
            "STL": 600.0,
            "TOV": 1500.0,
            "BLK": 300.0,
            "PTS": 13000.0,
        }

    def test_parse_player(self, sample_player_data: dict):
        """FranchisePlayer parses API data correctly."""
        player = FranchisePlayer.model_validate(sample_player_data)

        assert player.league_id == "00"
        assert player.team_id == 1610612747
        assert player.team == "Los Angeles Lakers"
        assert player.person_id == 2544
        assert player.player == "LeBron James"
        assert player.gp == 500
        assert player.pts == pytest.approx(13000.0)
        assert player.reb == pytest.approx(4000.0)
        assert player.ast == pytest.approx(5000.0)

    def test_parse_player_with_null_historical_stats(self):
        """FranchisePlayer handles null values for historical stats.

        Some stats weren't tracked in early NBA seasons:
        - OREB/DREB: not tracked before 1973
        - STL/BLK: not tracked before 1973
        - TOV: not tracked before 1977
        - REB: missing for some very early seasons
        """
        data = {
            "LEAGUE_ID": "00",
            "TEAM_ID": 1610612747,
            "TEAM": "Minneapolis Lakers",
            "PERSON_ID": 600015,
            "PLAYER": "George Mikan",
            "SEASON_TYPE": "Regular Season",
            "ACTIVE_WITH_TEAM": 0,
            "GP": 439,
            "FGM": 4097.0,
            "FGA": 11505.0,
            "FG_PCT": 0.356,
            "FG3M": None,
            "FG3A": None,
            "FG3_PCT": None,
            "FTM": 2849.0,
            "FTA": 3906.0,
            "FT_PCT": 0.729,
            "OREB": None,
            "DREB": None,
            "REB": None,  # Historical player with no rebound data
            "AST": 442.0,
            "PF": 1746.0,
            "STL": None,
            "TOV": None,
            "BLK": None,
            "PTS": 11043.0,
        }

        player = FranchisePlayer.model_validate(data)

        assert player.player == "George Mikan"
        assert player.oreb is None
        assert player.dreb is None
        assert player.reb is None
        assert player.stl is None
        assert player.tov is None
        assert player.blk is None
        assert player.fg3m is None
        assert player.fg3a is None
        assert player.fg3_pct is None


class TestFranchisePlayersResponse:
    """Tests for FranchisePlayersResponse model."""

    def test_parse_tabular_response(self):
        """FranchisePlayersResponse parses tabular resultSets format."""
        data = {
            "resultSets": [
                {
                    "name": "FranchisePlayers",
                    "headers": [
                        "LEAGUE_ID",
                        "TEAM_ID",
                        "TEAM",
                        "PERSON_ID",
                        "PLAYER",
                        "SEASON_TYPE",
                        "ACTIVE_WITH_TEAM",
                        "GP",
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
                    ],
                    "rowSet": [
                        [
                            "00",
                            1610612747,
                            "Los Angeles Lakers",
                            2544,
                            "LeBron James",
                            "Regular Season",
                            1,
                            500,
                            4500.0,
                            9000.0,
                            0.500,
                            800.0,
                            2400.0,
                            0.333,
                            3000.0,
                            4000.0,
                            0.750,
                            500.0,
                            3500.0,
                            4000.0,
                            5000.0,
                            800.0,
                            600.0,
                            1500.0,
                            300.0,
                            13000.0,
                        ],
                    ],
                }
            ]
        }

        response = FranchisePlayersResponse.model_validate(data)

        assert len(response.players) == 1
        assert response.players[0].player == "LeBron James"

    def test_parse_empty_response(self):
        """FranchisePlayersResponse handles empty player list."""
        data = {
            "resultSets": [
                {
                    "name": "FranchisePlayers",
                    "headers": [
                        "LEAGUE_ID",
                        "TEAM_ID",
                        "TEAM",
                        "PERSON_ID",
                        "PLAYER",
                        "SEASON_TYPE",
                        "ACTIVE_WITH_TEAM",
                        "GP",
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
                    ],
                    "rowSet": [],
                }
            ]
        }

        response = FranchisePlayersResponse.model_validate(data)

        assert response.players == []
