from fastbreak.models import CommonPlayoffSeriesResponse, PlayoffSeriesGame


class TestPlayoffSeriesGame:
    """Tests for PlayoffSeriesGame model."""

    def test_parse_valid_entry(self):
        """PlayoffSeriesGame parses valid data."""
        data = {
            "GAME_ID": "0042400101",
            "HOME_TEAM_ID": 1610612739,
            "VISITOR_TEAM_ID": 1610612748,
            "SERIES_ID": "004240010",
            "GAME_NUM": 1,
        }

        game = PlayoffSeriesGame.model_validate(data)

        assert game.game_id == "0042400101"
        assert game.home_team_id == 1610612739
        assert game.visitor_team_id == 1610612748
        assert game.series_id == "004240010"
        assert game.game_num == 1

    def test_parse_game_7(self):
        """PlayoffSeriesGame handles game 7."""
        data = {
            "GAME_ID": "0042400407",
            "HOME_TEAM_ID": 1610612760,
            "VISITOR_TEAM_ID": 1610612754,
            "SERIES_ID": "004240040",
            "GAME_NUM": 7,
        }

        game = PlayoffSeriesGame.model_validate(data)

        assert game.game_num == 7
        assert game.series_id == "004240040"


class TestCommonPlayoffSeriesResponse:
    """Tests for CommonPlayoffSeriesResponse model."""

    def test_parse_result_sets_format(self):
        """CommonPlayoffSeriesResponse parses tabular data correctly."""
        data = {
            "resource": "commonplayoffseries",
            "parameters": {
                "LeagueID": "00",
                "Season": "2024-25",
                "SeriesID": None,
            },
            "resultSets": [
                {
                    "name": "PlayoffSeries",
                    "headers": [
                        "GAME_ID",
                        "HOME_TEAM_ID",
                        "VISITOR_TEAM_ID",
                        "SERIES_ID",
                        "GAME_NUM",
                    ],
                    "rowSet": [
                        ["0042400101", 1610612739, 1610612748, "004240010", 1],
                        ["0042400102", 1610612739, 1610612748, "004240010", 2],
                        ["0042400103", 1610612748, 1610612739, "004240010", 3],
                        ["0042400104", 1610612748, 1610612739, "004240010", 4],
                    ],
                }
            ],
        }

        response = CommonPlayoffSeriesResponse.model_validate(data)

        assert len(response.games) == 4
        assert response.games[0].game_id == "0042400101"
        assert response.games[0].home_team_id == 1610612739
        assert response.games[0].game_num == 1
        assert response.games[3].game_num == 4
        # Games 3 and 4 have swapped home/away
        assert response.games[2].home_team_id == 1610612748
        assert response.games[2].visitor_team_id == 1610612739

    def test_handles_empty_result_set(self):
        """CommonPlayoffSeriesResponse handles empty rowSet gracefully."""
        data = {
            "resultSets": [
                {
                    "name": "PlayoffSeries",
                    "headers": [
                        "GAME_ID",
                        "HOME_TEAM_ID",
                        "VISITOR_TEAM_ID",
                        "SERIES_ID",
                        "GAME_NUM",
                    ],
                    "rowSet": [],
                }
            ],
        }

        response = CommonPlayoffSeriesResponse.model_validate(data)

        assert len(response.games) == 0

    def test_preserves_order_from_api(self):
        """CommonPlayoffSeriesResponse maintains order from API response."""
        data = {
            "resultSets": [
                {
                    "name": "PlayoffSeries",
                    "headers": [
                        "GAME_ID",
                        "HOME_TEAM_ID",
                        "VISITOR_TEAM_ID",
                        "SERIES_ID",
                        "GAME_NUM",
                    ],
                    "rowSet": [
                        ["0042400101", 1, 2, "004240010", 1],
                        ["0042400111", 3, 4, "004240011", 1],
                        ["0042400102", 1, 2, "004240010", 2],
                    ],
                }
            ],
        }

        response = CommonPlayoffSeriesResponse.model_validate(data)

        assert response.games[0].game_id == "0042400101"
        assert response.games[1].game_id == "0042400111"
        assert response.games[2].game_id == "0042400102"

    def test_multiple_series(self):
        """CommonPlayoffSeriesResponse handles multiple series."""
        data = {
            "resultSets": [
                {
                    "name": "PlayoffSeries",
                    "headers": [
                        "GAME_ID",
                        "HOME_TEAM_ID",
                        "VISITOR_TEAM_ID",
                        "SERIES_ID",
                        "GAME_NUM",
                    ],
                    "rowSet": [
                        ["0042400101", 1610612739, 1610612748, "004240010", 1],
                        ["0042400111", 1610612738, 1610612753, "004240011", 1],
                        ["0042400121", 1610612752, 1610612765, "004240012", 1],
                    ],
                }
            ],
        }

        response = CommonPlayoffSeriesResponse.model_validate(data)

        series_ids = {g.series_id for g in response.games}
        assert series_ids == {"004240010", "004240011", "004240012"}

    def test_finals_series(self):
        """CommonPlayoffSeriesResponse handles Finals series (round 4)."""
        data = {
            "resultSets": [
                {
                    "name": "PlayoffSeries",
                    "headers": [
                        "GAME_ID",
                        "HOME_TEAM_ID",
                        "VISITOR_TEAM_ID",
                        "SERIES_ID",
                        "GAME_NUM",
                    ],
                    "rowSet": [
                        ["0042400401", 1610612760, 1610612754, "004240040", 1],
                        ["0042400402", 1610612760, 1610612754, "004240040", 2],
                        ["0042400403", 1610612754, 1610612760, "004240040", 3],
                        ["0042400404", 1610612754, 1610612760, "004240040", 4],
                        ["0042400405", 1610612760, 1610612754, "004240040", 5],
                        ["0042400406", 1610612754, 1610612760, "004240040", 6],
                        ["0042400407", 1610612760, 1610612754, "004240040", 7],
                    ],
                }
            ],
        }

        response = CommonPlayoffSeriesResponse.model_validate(data)

        assert len(response.games) == 7
        assert all(g.series_id == "004240040" for g in response.games)
        assert response.games[6].game_num == 7
