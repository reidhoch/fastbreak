"""Tests for the PlayoffPicture endpoint."""

import pytest
from pydantic import ValidationError

from fastbreak.endpoints.playoff_picture import PlayoffPicture
from fastbreak.models.playoff_picture import PlayoffPictureResponse


class TestPlayoffPicture:
    """Tests for PlayoffPicture endpoint."""

    def test_init_with_defaults(self):
        """PlayoffPicture uses sensible defaults."""
        endpoint = PlayoffPicture()

        assert endpoint.league_id == "00"
        assert endpoint.season_id == "22024"

    def test_init_with_custom_season(self):
        """PlayoffPicture accepts custom season ID."""
        endpoint = PlayoffPicture(season_id="22023")

        assert endpoint.season_id == "22023"

    def test_params_returns_correct_dict(self):
        """params() returns correct parameters."""
        endpoint = PlayoffPicture(season_id="22023")

        params = endpoint.params()

        assert params == {
            "LeagueID": "00",
            "SeasonID": "22023",
        }

    def test_path_is_correct(self):
        """PlayoffPicture has correct API path."""
        endpoint = PlayoffPicture()

        assert endpoint.path == "playoffpicture"

    def test_response_model_is_correct(self):
        """PlayoffPicture uses PlayoffPictureResponse model."""
        endpoint = PlayoffPicture()

        assert endpoint.response_model is PlayoffPictureResponse

    def test_endpoint_is_frozen(self):
        """PlayoffPicture is immutable (frozen dataclass)."""
        endpoint = PlayoffPicture()

        with pytest.raises((AttributeError, ValidationError)):
            endpoint.season_id = "22023"  # type: ignore[misc]


class TestPlayoffPictureResponse:
    """Tests for PlayoffPictureResponse model."""

    def test_response_from_api_data(self):
        """Response parses NBA API format correctly."""
        api_data = {
            "resultSets": [
                {
                    "name": "EastConfPlayoffPicture",
                    "headers": [
                        "CONFERENCE",
                        "HIGH_SEED_RANK",
                        "HIGH_SEED_TEAM",
                        "HIGH_SEED_TEAM_ID",
                        "LOW_SEED_RANK",
                        "LOW_SEED_TEAM",
                        "LOW_SEED_TEAM_ID",
                        "HIGH_SEED_SERIES_W",
                        "HIGH_SEED_SERIES_L",
                        "HIGH_SEED_SERIES_REMAINING_G",
                        "HIGH_SEED_SERIES_REMAINING_HOME_G",
                        "HIGH_SEED_SERIES_REMAINING_AWAY_G",
                    ],
                    "rowSet": [
                        [
                            "East",
                            1,
                            "Boston",
                            1610612738,
                            8,
                            "Miami",
                            1610612748,
                            4,
                            1,
                            0,
                            0,
                            0,
                        ],
                    ],
                },
                {
                    "name": "WestConfPlayoffPicture",
                    "headers": [
                        "CONFERENCE",
                        "HIGH_SEED_RANK",
                        "HIGH_SEED_TEAM",
                        "HIGH_SEED_TEAM_ID",
                        "LOW_SEED_RANK",
                        "LOW_SEED_TEAM",
                        "LOW_SEED_TEAM_ID",
                        "HIGH_SEED_SERIES_W",
                        "HIGH_SEED_SERIES_L",
                        "HIGH_SEED_SERIES_REMAINING_G",
                        "HIGH_SEED_SERIES_REMAINING_HOME_G",
                        "HIGH_SEED_SERIES_REMAINING_AWAY_G",
                    ],
                    "rowSet": [
                        [
                            "West",
                            1,
                            "Oklahoma City",
                            1610612760,
                            8,
                            "L.A. Lakers",
                            1610612747,
                            4,
                            0,
                            0,
                            0,
                            0,
                        ],
                    ],
                },
                {
                    "name": "EastConfStandings",
                    "headers": [
                        "CONFERENCE",
                        "RANK",
                        "TEAM",
                        "TEAM_SLUG",
                        "TEAM_ID",
                        "WINS",
                        "LOSSES",
                        "PCT",
                        "DIV",
                        "CONF",
                        "HOME",
                        "AWAY",
                        "GB",
                        "GR_OVER_500",
                        "GR_OVER_500_HOME",
                        "GR_OVER_500_AWAY",
                        "GR_UNDER_500",
                        "GR_UNDER_500_HOME",
                        "GR_UNDER_500_AWAY",
                        "RANKING_CRITERIA",
                        "CLINCHED_PLAYOFFS",
                        "CLINCHED_CONFERENCE",
                        "CLINCHED_DIVISION",
                        "ELIMINATED_PLAYOFFS",
                        "SOSA_REMAINING",
                    ],
                    "rowSet": [
                        [
                            "East",
                            1,
                            "Boston",
                            "celtics",
                            1610612738,
                            64,
                            18,
                            0.78,
                            "15-2",
                            "41-11",
                            "37-4",
                            "27-14",
                            0.0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            1,
                            1,
                            1,
                            0,
                            None,
                        ],
                    ],
                },
                {
                    "name": "WestConfStandings",
                    "headers": [
                        "CONFERENCE",
                        "RANK",
                        "TEAM",
                        "TEAM_SLUG",
                        "TEAM_ID",
                        "WINS",
                        "LOSSES",
                        "PCT",
                        "DIV",
                        "CONF",
                        "HOME",
                        "AWAY",
                        "GB",
                        "GR_OVER_500",
                        "GR_OVER_500_HOME",
                        "GR_OVER_500_AWAY",
                        "GR_UNDER_500",
                        "GR_UNDER_500_HOME",
                        "GR_UNDER_500_AWAY",
                        "RANKING_CRITERIA",
                        "CLINCHED_PLAYOFFS",
                        "CLINCHED_CONFERENCE",
                        "CLINCHED_DIVISION",
                        "ELIMINATED_PLAYOFFS",
                        "SOSA_REMAINING",
                    ],
                    "rowSet": [
                        [
                            "West",
                            1,
                            "Oklahoma City",
                            "thunder",
                            1610612760,
                            57,
                            25,
                            0.695,
                            "12-4",
                            "36-16",
                            "33-8",
                            "24-17",
                            0.0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            1,
                            1,
                            1,
                            1,
                            0,
                            None,
                        ],
                    ],
                },
                {
                    "name": "EastConfRemainingGames",
                    "headers": [
                        "TEAM",
                        "TEAM_ID",
                        "REMAINING_G",
                        "REMAINING_HOME_G",
                        "REMAINING_AWAY_G",
                    ],
                    "rowSet": [
                        ["Boston", 1610612738, 5, 3, 2],
                    ],
                },
                {
                    "name": "WestConfRemainingGames",
                    "headers": [
                        "TEAM",
                        "TEAM_ID",
                        "REMAINING_G",
                        "REMAINING_HOME_G",
                        "REMAINING_AWAY_G",
                    ],
                    "rowSet": [
                        ["Oklahoma City", 1610612760, 4, 2, 2],
                    ],
                },
            ]
        }

        response = PlayoffPictureResponse.model_validate(api_data)

        # Check East playoff picture
        assert len(response.east_conf_playoff_picture) == 1
        assert response.east_conf_playoff_picture[0].high_seed_team == "Boston"
        assert response.east_conf_playoff_picture[0].low_seed_team == "Miami"
        assert response.east_conf_playoff_picture[0].high_seed_series_w == 4

        # Check West playoff picture
        assert len(response.west_conf_playoff_picture) == 1
        assert response.west_conf_playoff_picture[0].high_seed_team == "Oklahoma City"
        assert response.west_conf_playoff_picture[0].low_seed_team == "L.A. Lakers"

        # Check East standings
        assert len(response.east_conf_standings) == 1
        assert response.east_conf_standings[0].team == "Boston"
        assert response.east_conf_standings[0].wins == 64
        assert response.east_conf_standings[0].clinched_playoffs == 1
        assert response.east_conf_standings[0].clinched_conference == 1

        # Check West standings
        assert len(response.west_conf_standings) == 1
        assert response.west_conf_standings[0].team == "Oklahoma City"
        assert response.west_conf_standings[0].team_slug == "thunder"

        # Check remaining games
        assert len(response.east_conf_remaining_games) == 1
        assert response.east_conf_remaining_games[0].remaining_g == 5
        assert len(response.west_conf_remaining_games) == 1
        assert response.west_conf_remaining_games[0].remaining_g == 4

    def test_response_empty_result_sets(self):
        """Response handles empty result sets gracefully."""
        api_data = {
            "resultSets": [
                {"name": "EastConfPlayoffPicture", "headers": [], "rowSet": []},
                {"name": "WestConfPlayoffPicture", "headers": [], "rowSet": []},
                {"name": "EastConfStandings", "headers": [], "rowSet": []},
                {"name": "WestConfStandings", "headers": [], "rowSet": []},
                {"name": "EastConfRemainingGames", "headers": [], "rowSet": []},
                {"name": "WestConfRemainingGames", "headers": [], "rowSet": []},
            ]
        }

        response = PlayoffPictureResponse.model_validate(api_data)

        assert len(response.east_conf_playoff_picture) == 0
        assert len(response.west_conf_playoff_picture) == 0
        assert len(response.east_conf_standings) == 0
        assert len(response.west_conf_standings) == 0
        assert len(response.east_conf_remaining_games) == 0
        assert len(response.west_conf_remaining_games) == 0
