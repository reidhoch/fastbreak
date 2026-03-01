"""Tests for homepage-related endpoints."""

import pytest
from pydantic import ValidationError

from fastbreak.endpoints import HomepageLeaders, HomepageV2, LeadersTiles
from fastbreak.models import (
    HomepageLeadersResponse,
    HomepageV2Response,
    LeadersTilesResponse,
)


class TestHomepageV2:
    """Tests for HomepageV2 endpoint."""

    def test_init_with_defaults(self):
        """HomepageV2 works with default parameters."""
        endpoint = HomepageV2()

        assert endpoint.stat_type == "Traditional"
        assert endpoint.league_id == "00"
        assert endpoint.player_or_team == "Player"

    def test_init_with_season(self):
        """HomepageV2 accepts season parameter."""
        endpoint = HomepageV2(season="2024-25")

        assert endpoint.season == "2024-25"

    def test_params_returns_correct_dict(self):
        """params() returns correctly formatted parameters."""
        endpoint = HomepageV2(season="2024-25")

        params = endpoint.params()

        assert params["StatType"] == "Traditional"
        assert params["Season"] == "2024-25"
        assert params["PlayerOrTeam"] == "Player"

    def test_path_is_correct(self):
        """HomepageV2 has correct API path."""
        assert HomepageV2().path == "homepagev2"

    def test_response_model_is_correct(self):
        """HomepageV2 uses HomepageV2Response model."""
        assert HomepageV2().response_model is HomepageV2Response

    def test_endpoint_is_frozen(self):
        """HomepageV2 is immutable."""
        endpoint = HomepageV2()

        with pytest.raises((AttributeError, ValidationError)):
            endpoint.stat_type = "Advanced"  # type: ignore[misc]

    def test_params_without_season_omits_season_key(self):
        """params() omits Season key when season is not set."""
        assert "Season" not in HomepageV2().params()


class TestHomepageV2Response:
    """Tests for HomepageV2Response model."""

    def test_parse_result_sets(self):
        """Response parses multiple stat result sets."""
        raw_response = {
            "resultSets": [
                {
                    "name": "HomePageStat1",
                    "headers": [
                        "RANK",
                        "PLAYER_ID",
                        "PLAYER",
                        "TEAM_ID",
                        "TEAM_ABBREVIATION",
                        "TEAM_NAME",
                        "JERSEY_NUM",
                        "PLAYER_POSITION",
                        "PTS",
                    ],
                    "rowSet": [
                        [
                            1,
                            1628983,
                            "Shai Gilgeous-Alexander",
                            1610612760,
                            "OKC",
                            "Oklahoma City Thunder",
                            "2",
                            "G",
                            32.7,
                        ],
                    ],
                },
                {
                    "name": "HomePageStat2",
                    "headers": [
                        "RANK",
                        "PLAYER_ID",
                        "PLAYER",
                        "TEAM_ID",
                        "TEAM_ABBREVIATION",
                        "TEAM_NAME",
                        "JERSEY_NUM",
                        "PLAYER_POSITION",
                        "REB",
                    ],
                    "rowSet": [
                        [
                            1,
                            203999,
                            "Nikola Jokić",
                            1610612743,
                            "DEN",
                            "Denver Nuggets",
                            "15",
                            "C",
                            13.1,
                        ],
                    ],
                },
            ]
        }

        response = HomepageV2Response.model_validate(raw_response)

        assert len(response.pts_leaders) == 1
        assert response.pts_leaders[0].player == "Shai Gilgeous-Alexander"
        assert response.pts_leaders[0].pts == 32.7

        assert len(response.reb_leaders) == 1
        assert response.reb_leaders[0].player == "Nikola Jokić"


class TestHomepageLeaders:
    """Tests for HomepageLeaders endpoint."""

    def test_init_with_stat_category(self):
        """HomepageLeaders accepts stat category."""
        endpoint = HomepageLeaders(stat_category="Rebounds")

        assert endpoint.stat_category == "Rebounds"

    def test_params_returns_correct_dict(self):
        """params() returns correctly formatted parameters."""
        endpoint = HomepageLeaders(stat_category="Points", season="2024-25")

        params = endpoint.params()

        assert params["StatCategory"] == "Points"
        assert params["Season"] == "2024-25"

    def test_path_is_correct(self):
        """HomepageLeaders has correct API path."""
        assert HomepageLeaders().path == "homepageleaders"

    def test_params_without_season_omits_season_key(self):
        """params() omits Season key when season is not set."""
        assert "Season" not in HomepageLeaders().params()


class TestHomepageLeadersResponse:
    """Tests for HomepageLeadersResponse model."""

    def test_parse_leaders_result_set(self):
        """Response parses leaders with efficiency stats."""
        raw_response = {
            "resultSets": [
                {
                    "name": "HomePageLeaders",
                    "headers": [
                        "RANK",
                        "PLAYERID",
                        "PLAYER",
                        "TEAM_ID",
                        "TEAM_ABBREVIATION",
                        "TEAM_NAME",
                        "PTS",
                        "FG_PCT",
                        "FG3_PCT",
                        "FT_PCT",
                        "EFG_PCT",
                        "TS_PCT",
                        "PTS_PER48",
                    ],
                    "rowSet": [
                        [
                            1,
                            1628983,
                            "Shai Gilgeous-Alexander",
                            1610612760,
                            "OKC",
                            "Oklahoma City Thunder",
                            32.7,
                            0.519,
                            0.375,
                            0.898,
                            0.569,
                            0.637,
                            45.9,
                        ],
                    ],
                }
            ]
        }

        response = HomepageLeadersResponse.model_validate(raw_response)

        assert len(response.leaders) == 1
        leader = response.leaders[0]
        assert leader.player == "Shai Gilgeous-Alexander"
        assert leader.ts_pct == 0.637
        assert leader.pts_per_48 == 45.9


class TestLeadersTiles:
    """Tests for LeadersTiles endpoint."""

    def test_init_with_stat(self):
        """LeadersTiles accepts stat parameter."""
        endpoint = LeadersTiles(stat="REB")

        assert endpoint.stat == "REB"

    def test_params_returns_correct_dict(self):
        """params() returns correctly formatted parameters."""
        endpoint = LeadersTiles(stat="PTS", season="2024-25")

        params = endpoint.params()

        assert params["Stat"] == "PTS"
        assert params["Season"] == "2024-25"

    def test_path_is_correct(self):
        """LeadersTiles has correct API path."""
        assert LeadersTiles().path == "leaderstiles"

    def test_params_without_season_omits_season_key(self):
        """params() omits Season key when season is not set."""
        assert "Season" not in LeadersTiles().params()


class TestLeadersTilesResponse:
    """Tests for LeadersTilesResponse model."""

    def test_parse_with_historical_data(self):
        """Response parses leaders with historical comparisons."""
        raw_response = {
            "resultSet": [
                {
                    "name": "LeadersTiles",
                    "headers": [
                        "RANK",
                        "PLAYER_ID",
                        "PLAYER",
                        "TEAM_ID",
                        "TEAM_ABBREVIATION",
                        "TEAM_NAME",
                        "PTS",
                    ],
                    "rowSet": [
                        [
                            1,
                            1628983,
                            "Shai Gilgeous-Alexander",
                            1610612760,
                            "OKC",
                            "Oklahoma City Thunder",
                            32.7,
                        ],
                    ],
                },
                {
                    "name": "AllTimeSeasonHigh",
                    "headers": [
                        "PLAYER_ID",
                        "PLAYER_NAME",
                        "PTS",
                        "SEASON_YEAR",
                        "TEAM_ID",
                        "TEAM_ABBREVIATION",
                        "TEAM_NAME",
                    ],
                    "rowSet": [
                        [
                            76375,
                            "Wilt Chamberlain",
                            50.4,
                            "1961-62",
                            1610612744,
                            "PHW",
                            "Warriors",
                        ],
                    ],
                },
                {
                    "name": "LastSeasonHigh",
                    "headers": [
                        "RANK",
                        "PLAYER_ID",
                        "PLAYER_NAME",
                        "PTS",
                        "SEASON_YEAR",
                        "TEAM_ID",
                        "TEAM_ABBREVIATION",
                        "TEAM_NAME",
                    ],
                    "rowSet": [
                        [
                            1,
                            1628983,
                            "Shai Gilgeous-Alexander",
                            31.4,
                            "2023-24",
                            1610612760,
                            "OKC",
                            "Oklahoma City Thunder",
                        ],
                    ],
                },
            ]
        }

        response = LeadersTilesResponse.model_validate(raw_response)

        assert len(response.leaders) == 1
        assert response.leaders[0].player == "Shai Gilgeous-Alexander"

        assert len(response.all_time_season_high) == 1
        assert response.all_time_season_high[0].player_name == "Wilt Chamberlain"
        assert response.all_time_season_high[0].pts == 50.4

        assert len(response.last_season_high) == 1
        assert response.last_season_high[0].pts == 31.4

    def test_validate_normalized_data_passthrough(self):
        """model_validate accepts already-normalized data without a resultSet key."""
        data = {"leaders": [], "all_time_season_high": [], "last_season_high": []}
        response = LeadersTilesResponse.model_validate(data)
        assert response.leaders == []
        assert response.all_time_season_high == []
        assert response.last_season_high == []
