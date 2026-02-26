"""Tests for LeaguePlayerOnDetails endpoint."""

import pytest
from pydantic import ValidationError

from fastbreak.endpoints import LeaguePlayerOnDetails
from fastbreak.models import LeaguePlayerOnDetailsResponse
from fastbreak.seasons import get_season_from_date


class TestLeaguePlayerOnDetails:
    """Tests for LeaguePlayerOnDetails endpoint."""

    def test_init_with_required_team_id(self):
        """LeaguePlayerOnDetails requires team_id."""
        endpoint = LeaguePlayerOnDetails(team_id=1610612747)

        assert endpoint.team_id == 1610612747
        assert endpoint.season == get_season_from_date()
        assert endpoint.season_type == "Regular Season"
        assert endpoint.per_mode == "Totals"
        assert endpoint.measure_type == "Base"

    def test_init_with_custom_season(self):
        """LeaguePlayerOnDetails accepts custom season."""
        endpoint = LeaguePlayerOnDetails(team_id=1610612747, season="2023-24")

        assert endpoint.season == "2023-24"

    def test_init_with_per_game_mode(self):
        """LeaguePlayerOnDetails accepts PerGame mode."""
        endpoint = LeaguePlayerOnDetails(team_id=1610612747, per_mode="PerGame")

        assert endpoint.per_mode == "PerGame"

    def test_init_with_playoffs(self):
        """LeaguePlayerOnDetails accepts Playoffs season type."""
        endpoint = LeaguePlayerOnDetails(team_id=1610612747, season_type="Playoffs")

        assert endpoint.season_type == "Playoffs"

    def test_init_with_advanced_measure(self):
        """LeaguePlayerOnDetails accepts Advanced measure type."""
        endpoint = LeaguePlayerOnDetails(team_id=1610612747, measure_type="Advanced")

        assert endpoint.measure_type == "Advanced"

    def test_params_returns_correct_dict(self):
        """params() returns correctly formatted parameters."""
        endpoint = LeaguePlayerOnDetails(
            team_id=1610612747,
            season="2024-25",
            season_type="Regular Season",
            per_mode="Totals",
            measure_type="Base",
        )

        params = endpoint.params()

        assert params["TeamID"] == "1610612747"
        assert params["Season"] == "2024-25"
        assert params["SeasonType"] == "Regular Season"
        assert params["PerMode"] == "Totals"
        assert params["MeasureType"] == "Base"

    def test_params_includes_all_filters(self):
        """params() includes all filter parameters."""
        endpoint = LeaguePlayerOnDetails(team_id=1610612747)

        params = endpoint.params()

        # All required filter params should be present
        assert "DateFrom" in params
        assert "DateTo" in params
        assert "GameSegment" in params
        assert "LastNGames" in params
        assert "VsConference" in params
        assert "VsDivision" in params

    def test_path_is_correct(self):
        """LeaguePlayerOnDetails has correct API path."""
        endpoint = LeaguePlayerOnDetails(team_id=1610612747)

        assert endpoint.path == "leagueplayerondetails"

    def test_response_model_is_correct(self):
        """LeaguePlayerOnDetails uses LeaguePlayerOnDetailsResponse model."""
        endpoint = LeaguePlayerOnDetails(team_id=1610612747)

        assert endpoint.response_model is LeaguePlayerOnDetailsResponse

    def test_endpoint_is_frozen(self):
        """LeaguePlayerOnDetails is immutable (frozen dataclass)."""
        endpoint = LeaguePlayerOnDetails(team_id=1610612747)

        with pytest.raises((AttributeError, ValidationError)):
            endpoint.season = "2023-24"  # type: ignore[misc]


class TestLeaguePlayerOnDetailsResponse:
    """Tests for LeaguePlayerOnDetailsResponse model."""

    def test_parse_tabular_response(self):
        """Response parses NBA's tabular format correctly."""
        raw_response = {
            "resultSets": [
                {
                    "name": "PlayersOnCourtLeaguePlayerDetails",
                    "headers": [
                        "GROUP_SET",
                        "TEAM_ID",
                        "TEAM_ABBREVIATION",
                        "TEAM_NAME",
                        "VS_PLAYER_ID",
                        "VS_PLAYER_NAME",
                        "COURT_STATUS",
                        "GP",
                        "W",
                        "L",
                        "W_PCT",
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
                        "GP_RANK",
                        "W_RANK",
                        "L_RANK",
                        "W_PCT_RANK",
                        "MIN_RANK",
                        "FGM_RANK",
                        "FGA_RANK",
                        "FG_PCT_RANK",
                        "FG3M_RANK",
                        "FG3A_RANK",
                        "FG3_PCT_RANK",
                        "FTM_RANK",
                        "FTA_RANK",
                        "FT_PCT_RANK",
                        "OREB_RANK",
                        "DREB_RANK",
                        "REB_RANK",
                        "AST_RANK",
                        "TOV_RANK",
                        "STL_RANK",
                        "BLK_RANK",
                        "BLKA_RANK",
                        "PF_RANK",
                        "PFD_RANK",
                        "PTS_RANK",
                        "PLUS_MINUS_RANK",
                    ],
                    "rowSet": [
                        [
                            "On/Off Court",
                            1610612747,
                            "LAL",
                            "Los Angeles Lakers",
                            2544,
                            "James, LeBron",
                            "On",
                            70,
                            44,
                            26,
                            0.629,
                            2444.446667,
                            2108,
                            4346,
                            0.485,
                            660,
                            1852,
                            0.356,
                            905,
                            1151,
                            0.786,
                            465,
                            1662,
                            2127,
                            1355,
                            717.0,
                            376,
                            228,
                            209,
                            845,
                            966,
                            5781,
                            -54.0,
                            4,
                            4,
                            21,
                            11,
                            2,
                            2,
                            2,
                            6,
                            2,
                            2,
                            15,
                            2,
                            2,
                            8,
                            2,
                            2,
                            2,
                            2,
                            24,
                            2,
                            1,
                            23,
                            23,
                            2,
                            2,
                            20,
                        ],
                    ],
                },
            ]
        }

        response = LeaguePlayerOnDetailsResponse.model_validate(raw_response)

        assert len(response.details) == 1

        detail = response.details[0]
        assert detail.team_abbreviation == "LAL"
        assert detail.vs_player_name == "James, LeBron"
        assert detail.court_status == "On"
        assert detail.gp == 70
        assert detail.w == 44
        assert detail.pts == 5781

    def test_parse_empty_response(self):
        """Response handles empty result sets."""
        raw_response = {
            "resultSets": [
                {
                    "name": "PlayersOnCourtLeaguePlayerDetails",
                    "headers": ["GROUP_SET"],
                    "rowSet": [],
                },
            ]
        }

        response = LeaguePlayerOnDetailsResponse.model_validate(raw_response)

        assert response.details == []
