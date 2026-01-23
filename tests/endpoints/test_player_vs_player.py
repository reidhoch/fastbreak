"""Tests for the PlayerVsPlayer endpoint."""

from fastbreak.endpoints.player_vs_player import PlayerVsPlayer
from fastbreak.models.player_vs_player import PlayerVsPlayerResponse


class TestPlayerVsPlayer:
    """Tests for PlayerVsPlayer endpoint."""

    def test_init_with_defaults(self):
        """PlayerVsPlayer uses sensible defaults."""
        endpoint = PlayerVsPlayer()

        assert endpoint.league_id == "00"
        assert endpoint.player_id == ""
        assert endpoint.vs_player_id == ""
        assert endpoint.season == "2024-25"
        assert endpoint.season_type == "Regular Season"
        assert endpoint.per_mode == "PerGame"
        assert endpoint.measure_type == "Base"

    def test_init_with_player_ids(self):
        """PlayerVsPlayer accepts player IDs."""
        endpoint = PlayerVsPlayer(
            player_id="2544",
            vs_player_id="203999",
        )

        assert endpoint.player_id == "2544"
        assert endpoint.vs_player_id == "203999"

    def test_init_with_optional_filters(self):
        """PlayerVsPlayer accepts optional filters."""
        endpoint = PlayerVsPlayer(
            player_id="2544",
            vs_player_id="203999",
            season="2023-24",
            last_n_games="10",
            outcome="W",
        )

        assert endpoint.season == "2023-24"
        assert endpoint.last_n_games == "10"
        assert endpoint.outcome == "W"

    def test_params_with_required_only(self):
        """params() returns required parameters."""
        endpoint = PlayerVsPlayer()

        params = endpoint.params()

        assert params == {
            "LeagueID": "00",
            "PlayerID": "",
            "VsPlayerID": "",
            "Season": "2024-25",
            "SeasonType": "Regular Season",
            "PerMode": "PerGame",
            "MeasureType": "Base",
            "PaceAdjust": "N",
            "PlusMinus": "N",
            "Rank": "N",
            "LastNGames": "0",
            "Month": "0",
            "OpponentTeamID": "0",
            "Period": "0",
        }

    def test_params_with_filters(self):
        """params() includes optional filters when set."""
        endpoint = PlayerVsPlayer(
            player_id="2544",
            vs_player_id="203999",
            last_n_games="10",
            outcome="W",
            location="Home",
        )

        params = endpoint.params()

        assert params["PlayerID"] == "2544"
        assert params["VsPlayerID"] == "203999"
        assert params["LastNGames"] == "10"
        assert params["Outcome"] == "W"
        assert params["Location"] == "Home"

    def test_path_is_correct(self):
        """PlayerVsPlayer has correct API path."""
        endpoint = PlayerVsPlayer()

        assert endpoint.path == "playervsplayer"

    def test_response_model_is_correct(self):
        """PlayerVsPlayer uses PlayerVsPlayerResponse model."""
        endpoint = PlayerVsPlayer()

        assert endpoint.response_model is PlayerVsPlayerResponse

    def test_endpoint_is_frozen(self):
        """PlayerVsPlayer is immutable (frozen dataclass)."""
        endpoint = PlayerVsPlayer()

        try:
            endpoint.season = "2023-24"  # type: ignore[misc]
            frozen = False
        except AttributeError:
            frozen = True

        assert frozen, "Endpoint should be frozen (immutable)"


class TestPlayerVsPlayerResponse:
    """Tests for PlayerVsPlayerResponse model."""

    def test_response_from_api_data(self):
        """Response parses NBA API format correctly."""
        api_data = {
            "resultSets": [
                {
                    "name": "Overall",
                    "headers": [
                        "GROUP_SET",
                        "GROUP_VALUE",
                        "PLAYER_ID",
                        "PLAYER_NAME",
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
                        "NBA_FANTASY_PTS",
                    ],
                    "rowSet": [
                        [
                            "Overall",
                            "LeBron James",
                            2544,
                            "LeBron James",
                            70,
                            44,
                            26,
                            0.629,
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
                            47.1,
                        ],
                    ],
                },
                {
                    "name": "OnOffCourt",
                    "headers": [
                        "GROUP_SET",
                        "PLAYER_ID",
                        "PLAYER_NAME",
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
                        "NBA_FANTASY_PTS",
                    ],
                    "rowSet": [
                        [
                            "Vs. Player",
                            2544,
                            "LeBron James",
                            203999,
                            "Jokic, Nikola",
                            "On",
                            2,
                            1,
                            1,
                            0.5,
                            24.8,
                            5.0,
                            12.5,
                            0.4,
                            0.5,
                            3.5,
                            0.143,
                            1.0,
                            1.5,
                            0.667,
                            1.0,
                            4.5,
                            5.5,
                            4.0,
                            3.0,
                            0.5,
                            1.5,
                            0.0,
                            2.0,
                            2.0,
                            11.5,
                            -19.5,
                            27.1,
                        ],
                    ],
                },
                {"name": "ShotDistanceOverall", "headers": [], "rowSet": []},
                {"name": "ShotDistanceOnCourt", "headers": [], "rowSet": []},
                {"name": "ShotDistanceOffCourt", "headers": [], "rowSet": []},
                {"name": "ShotAreaOverall", "headers": [], "rowSet": []},
                {"name": "ShotAreaOnCourt", "headers": [], "rowSet": []},
                {"name": "ShotAreaOffCourt", "headers": [], "rowSet": []},
                {
                    "name": "PlayerInfo",
                    "headers": [
                        "PERSON_ID",
                        "FIRST_NAME",
                        "LAST_NAME",
                        "DISPLAY_FIRST_LAST",
                        "DISPLAY_LAST_COMMA_FIRST",
                        "DISPLAY_FI_LAST",
                        "BIRTHDATE",
                        "SCHOOL",
                        "COUNTRY",
                        "LAST_AFFILIATION",
                    ],
                    "rowSet": [
                        [
                            2544,
                            "LeBron",
                            "James",
                            "LeBron James",
                            "James, LeBron",
                            "L. James",
                            "1984-12-30T00:00:00",
                            "St. Vincent-St. Mary HS (OH)",
                            "USA",
                            "St. Vincent-St. Mary HS (OH)/USA",
                        ],
                    ],
                },
                {
                    "name": "VsPlayerInfo",
                    "headers": [
                        "PERSON_ID",
                        "FIRST_NAME",
                        "LAST_NAME",
                        "DISPLAY_FIRST_LAST",
                        "DISPLAY_LAST_COMMA_FIRST",
                        "DISPLAY_FI_LAST",
                        "BIRTHDATE",
                        "SCHOOL",
                        "COUNTRY",
                        "LAST_AFFILIATION",
                    ],
                    "rowSet": [
                        [
                            203999,
                            "Nikola",
                            "Jokic",
                            "Nikola Jokic",
                            "Jokic, Nikola",
                            "N. Jokic",
                            "1995-02-19T00:00:00",
                            "Mega Basket",
                            "Serbia",
                            "Mega Basket/Serbia",
                        ],
                    ],
                },
            ]
        }

        response = PlayerVsPlayerResponse.model_validate(api_data)

        assert len(response.overall) == 1
        assert response.overall[0].player_name == "LeBron James"
        assert response.overall[0].player_id == 2544
        assert response.overall[0].pts == 24.4

        assert len(response.on_off_court) == 1
        assert response.on_off_court[0].court_status == "On"
        assert response.on_off_court[0].vs_player_id == 203999

        assert len(response.player_info) == 1
        assert response.player_info[0].first_name == "LeBron"
        assert response.player_info[0].last_name == "James"

        assert len(response.vs_player_info) == 1
        assert response.vs_player_info[0].first_name == "Nikola"
        assert response.vs_player_info[0].country == "Serbia"

    def test_response_empty_result_sets(self):
        """Response handles empty result sets gracefully."""
        api_data = {
            "resultSets": [
                {"name": "Overall", "headers": [], "rowSet": []},
                {"name": "OnOffCourt", "headers": [], "rowSet": []},
                {"name": "ShotDistanceOverall", "headers": [], "rowSet": []},
                {"name": "ShotDistanceOnCourt", "headers": [], "rowSet": []},
                {"name": "ShotDistanceOffCourt", "headers": [], "rowSet": []},
                {"name": "ShotAreaOverall", "headers": [], "rowSet": []},
                {"name": "ShotAreaOnCourt", "headers": [], "rowSet": []},
                {"name": "ShotAreaOffCourt", "headers": [], "rowSet": []},
                {"name": "PlayerInfo", "headers": [], "rowSet": []},
                {"name": "VsPlayerInfo", "headers": [], "rowSet": []},
            ]
        }

        response = PlayerVsPlayerResponse.model_validate(api_data)

        assert len(response.overall) == 0
        assert len(response.on_off_court) == 0
        assert len(response.player_info) == 0
        assert len(response.vs_player_info) == 0
