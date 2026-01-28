"""Tests for the ShotChartDetail endpoint."""

import pytest

from fastbreak.endpoints import ShotChartDetail
from fastbreak.models import LeagueAverage, Shot, ShotChartDetailResponse


class TestShotChartDetailEndpoint:
    """Tests for ShotChartDetail endpoint configuration."""

    def test_path(self):
        """Endpoint has correct path."""
        endpoint = ShotChartDetail(player_id=2544)
        assert endpoint.path == "shotchartdetail"

    def test_default_params(self):
        """Default parameters are set correctly."""
        endpoint = ShotChartDetail(player_id=2544)
        params = endpoint.params()

        assert params["PlayerID"] == "2544"
        assert params["TeamID"] == "0"
        assert params["LeagueID"] == "00"
        assert params["SeasonType"] == "Regular Season"
        assert params["ContextMeasure"] == "FGA"
        # Season is optional - not included when None
        assert "Season" not in params
        # These are always sent with defaults
        assert params["OpponentTeamID"] == "0"
        assert params["Period"] == "0"
        assert params["LastNGames"] == "0"
        assert params["Month"] == "0"

    def test_custom_params(self):
        """Custom parameters are included in params dict."""
        endpoint = ShotChartDetail(
            player_id=2544,
            team_id=1610612747,
            season="2023-24",
            context_measure="FG3A",
            last_n_games=10,
            period=4,
        )
        params = endpoint.params()

        assert params["PlayerID"] == "2544"
        assert params["TeamID"] == "1610612747"
        assert params["Season"] == "2023-24"
        assert params["ContextMeasure"] == "FG3A"
        assert params["LastNGames"] == "10"
        assert params["Period"] == "4"

    def test_optional_params_excluded_when_none(self):
        """Optional string params are excluded when None."""
        endpoint = ShotChartDetail(player_id=2544)
        params = endpoint.params()

        # String params excluded when None
        assert "GameID" not in params
        assert "Location" not in params
        assert "Outcome" not in params
        assert "ISTRound" not in params
        assert "ClutchTime" not in params


class TestShotChartDetailResponse:
    """Tests for ShotChartDetailResponse model parsing."""

    @pytest.fixture
    def sample_response(self):
        """Sample API response with shot chart data."""
        return {
            "resultSets": [
                {
                    "name": "Shot_Chart_Detail",
                    "headers": [
                        "GRID_TYPE",
                        "GAME_ID",
                        "GAME_EVENT_ID",
                        "PLAYER_ID",
                        "PLAYER_NAME",
                        "TEAM_ID",
                        "TEAM_NAME",
                        "PERIOD",
                        "MINUTES_REMAINING",
                        "SECONDS_REMAINING",
                        "EVENT_TYPE",
                        "ACTION_TYPE",
                        "SHOT_TYPE",
                        "SHOT_ZONE_BASIC",
                        "SHOT_ZONE_AREA",
                        "SHOT_ZONE_RANGE",
                        "SHOT_DISTANCE",
                        "LOC_X",
                        "LOC_Y",
                        "SHOT_ATTEMPTED_FLAG",
                        "SHOT_MADE_FLAG",
                        "GAME_DATE",
                        "HTM",
                        "VTM",
                    ],
                    "rowSet": [
                        [
                            "Shot Chart Detail",
                            "0022300001",
                            10,
                            2544,
                            "LeBron James",
                            1610612747,
                            "Los Angeles Lakers",
                            1,
                            10,
                            30,
                            "Made Shot",
                            "Driving Layup",
                            "2PT Field Goal",
                            "Restricted Area",
                            "Center(C)",
                            "Less Than 8 ft.",
                            2,
                            -15,
                            25,
                            1,
                            1,
                            "20231024",
                            "LAL",
                            "DEN",
                        ],
                        [
                            "Shot Chart Detail",
                            "0022300001",
                            25,
                            2544,
                            "LeBron James",
                            1610612747,
                            "Los Angeles Lakers",
                            1,
                            8,
                            45,
                            "Missed Shot",
                            "Jump Shot",
                            "3PT Field Goal",
                            "Above the Break 3",
                            "Right Side Center(RC)",
                            "24+ ft.",
                            26,
                            150,
                            85,
                            1,
                            0,
                            "20231024",
                            "LAL",
                            "DEN",
                        ],
                    ],
                },
                {
                    "name": "LeagueAverages",
                    "headers": [
                        "GRID_TYPE",
                        "SHOT_ZONE_BASIC",
                        "SHOT_ZONE_AREA",
                        "SHOT_ZONE_RANGE",
                        "FGA",
                        "FGM",
                        "FG_PCT",
                    ],
                    "rowSet": [
                        [
                            "League Averages",
                            "Restricted Area",
                            "Center(C)",
                            "Less Than 8 ft.",
                            50000,
                            32500,
                            0.650,
                        ],
                        [
                            "League Averages",
                            "Above the Break 3",
                            "Right Side Center(RC)",
                            "24+ ft.",
                            40000,
                            14800,
                            0.370,
                        ],
                    ],
                },
            ]
        }

    def test_parses_shots(self, sample_response):
        """Response correctly parses shot data."""
        response = ShotChartDetailResponse.model_validate(sample_response)

        assert len(response.shots) == 2
        shot = response.shots[0]
        assert shot.player_id == 2544
        assert shot.player_name == "LeBron James"
        assert shot.loc_x == -15
        assert shot.loc_y == 25
        assert shot.shot_made_flag == 1
        assert shot.shot_zone_basic == "Restricted Area"

    def test_parses_league_averages(self, sample_response):
        """Response correctly parses league averages."""
        response = ShotChartDetailResponse.model_validate(sample_response)

        assert len(response.league_averages) == 2
        avg = response.league_averages[0]
        assert avg.shot_zone_basic == "Restricted Area"
        assert avg.fga == 50000
        assert avg.fgm == 32500
        assert avg.fg_pct == 0.650

    def test_empty_response(self):
        """Handles empty result sets gracefully."""
        empty_response = {
            "resultSets": [
                {"name": "Shot_Chart_Detail", "headers": [], "rowSet": []},
                {"name": "LeagueAverages", "headers": [], "rowSet": []},
            ]
        }
        response = ShotChartDetailResponse.model_validate(empty_response)

        assert response.shots == []
        assert response.league_averages == []


class TestShotModel:
    """Tests for individual Shot model."""

    def test_shot_coordinates(self):
        """Shot has correct x/y coordinate fields."""
        shot = Shot(
            grid_type="Shot Chart Detail",
            game_id="0022300001",
            game_event_id=10,
            player_id=2544,
            player_name="LeBron James",
            team_id=1610612747,
            team_name="Los Angeles Lakers",
            period=1,
            minutes_remaining=10,
            seconds_remaining=30,
            event_type="Made Shot",
            action_type="Driving Layup",
            shot_type="2PT Field Goal",
            shot_zone_basic="Restricted Area",
            shot_zone_area="Center(C)",
            shot_zone_range="Less Than 8 ft.",
            shot_distance=2,
            loc_x=-15,
            loc_y=25,
            shot_attempted_flag=1,
            shot_made_flag=1,
            game_date="20231024",
            htm="LAL",
            vtm="DEN",
        )

        assert shot.loc_x == -15
        assert shot.loc_y == 25
        assert shot.shot_distance == 2
