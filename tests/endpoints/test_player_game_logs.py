"""Tests for PlayerGameLogs endpoint."""

from pydantic import ValidationError

from fastbreak.endpoints import PlayerGameLogs
from fastbreak.models import PlayerGameLogsResponse


class TestPlayerGameLogs:
    """Tests for PlayerGameLogs endpoint."""

    def test_init_with_defaults(self):
        """PlayerGameLogs uses sensible defaults."""
        endpoint = PlayerGameLogs(player_id="2544")

        assert endpoint.player_id == "2544"
        assert endpoint.league_id == "00"
        assert endpoint.season == "2024-25"
        assert endpoint.season_type == "Regular Season"

    def test_init_with_player_id(self):
        """PlayerGameLogs accepts player_id."""
        endpoint = PlayerGameLogs(player_id="2544")

        assert endpoint.player_id == "2544"

    def test_params_returns_all_parameters(self):
        """params() returns all query parameters."""
        endpoint = PlayerGameLogs(player_id="2544", season="2023-24")

        params = endpoint.params()

        assert params["PlayerID"] == "2544"
        assert params["LeagueID"] == "00"
        assert params["Season"] == "2023-24"
        assert params["SeasonType"] == "Regular Season"

    def test_path_is_correct(self):
        """PlayerGameLogs has correct API path."""
        endpoint = PlayerGameLogs(player_id="2544")

        assert endpoint.path == "playergamelogs"

    def test_response_model_is_correct(self):
        """PlayerGameLogs uses correct response model."""
        endpoint = PlayerGameLogs(player_id="2544")

        assert endpoint.response_model is PlayerGameLogsResponse

    def test_endpoint_is_frozen(self):
        """PlayerGameLogs is immutable (frozen dataclass)."""
        endpoint = PlayerGameLogs(player_id="2544")

        try:
            endpoint.season = "2023-24"  # type: ignore[misc]
            frozen = False
        except (AttributeError, ValidationError):
            frozen = True

        assert frozen


class TestPlayerGameLogsResponse:
    """Tests for PlayerGameLogsResponse model."""

    @staticmethod
    def _make_headers() -> list[str]:
        """Return headers for player game logs (70 columns)."""
        return [
            "SEASON_YEAR",
            "PLAYER_ID",
            "PLAYER_NAME",
            "NICKNAME",
            "TEAM_ID",
            "TEAM_ABBREVIATION",
            "TEAM_NAME",
            "GAME_ID",
            "GAME_DATE",
            "MATCHUP",
            "WL",
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
            "DD2",
            "TD3",
            "WNBA_FANTASY_PTS",
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
            "NBA_FANTASY_PTS_RANK",
            "DD2_RANK",
            "TD3_RANK",
            "WNBA_FANTASY_PTS_RANK",
            "AVAILABLE_FLAG",
            "MIN_SEC",
            "TEAM_COUNT",
        ]

    @staticmethod
    def _make_row(
        player_id: int,
        player_name: str,
        game_id: str,
        matchup: str,
        wl: str,
        pts: int,
        reb: int,
        ast: int,
    ) -> list:
        """Create a test row for player game logs (70 values)."""
        return [
            "2024-25",  # SEASON_YEAR
            player_id,
            player_name,
            player_name.split()[0],  # NICKNAME
            1610612747,  # TEAM_ID
            "LAL",  # TEAM_ABBREVIATION
            "Los Angeles Lakers",  # TEAM_NAME
            game_id,
            "2025-04-11T00:00:00",  # GAME_DATE
            matchup,
            wl,
            35.5,  # MIN
            10,  # FGM
            20,  # FGA
            0.5,  # FG_PCT
            3,  # FG3M
            8,  # FG3A
            0.375,  # FG3_PCT
            5,  # FTM
            6,  # FTA
            0.833,  # FT_PCT
            2,  # OREB
            reb - 2,  # DREB
            reb,
            ast,
            3,  # TOV
            2,  # STL
            1,  # BLK
            0,  # BLKA
            2,  # PF
            4,  # PFD
            pts,
            10,  # PLUS_MINUS
            45.5,  # NBA_FANTASY_PTS
            1 if pts >= 10 and reb >= 10 else 0,  # DD2
            0,  # TD3
            40.0,  # WNBA_FANTASY_PTS
            # Rankings (30 values)
            1,  # GP_RANK
            1,  # W_RANK
            1,  # L_RANK
            1,  # W_PCT_RANK
            10,  # MIN_RANK
            20,  # FGM_RANK
            30,  # FGA_RANK
            40,  # FG_PCT_RANK
            50,  # FG3M_RANK
            60,  # FG3A_RANK
            70,  # FG3_PCT_RANK
            80,  # FTM_RANK
            90,  # FTA_RANK
            100,  # FT_PCT_RANK
            110,  # OREB_RANK
            120,  # DREB_RANK
            130,  # REB_RANK
            140,  # AST_RANK
            150,  # TOV_RANK
            160,  # STL_RANK
            170,  # BLK_RANK
            180,  # BLKA_RANK
            190,  # PF_RANK
            200,  # PFD_RANK
            210,  # PTS_RANK
            220,  # PLUS_MINUS_RANK
            230,  # NBA_FANTASY_PTS_RANK
            240,  # DD2_RANK
            250,  # TD3_RANK
            260,  # WNBA_FANTASY_PTS_RANK
            # Metadata
            1,  # AVAILABLE_FLAG
            "35:30",  # MIN_SEC
            1,  # TEAM_COUNT
        ]

    def test_parse_tabular_response(self):
        """Response parses NBA's tabular format correctly."""
        headers = self._make_headers()

        raw_response = {
            "resultSets": [
                {
                    "name": "PlayerGameLogs",
                    "headers": headers,
                    "rowSet": [
                        self._make_row(
                            2544,
                            "LeBron James",
                            "0022401185",
                            "LAL vs. HOU",
                            "W",
                            28,
                            12,
                            10,
                        ),
                        self._make_row(
                            2544,
                            "LeBron James",
                            "0022401170",
                            "LAL @ DEN",
                            "L",
                            22,
                            6,
                            8,
                        ),
                    ],
                }
            ]
        }

        response = PlayerGameLogsResponse.model_validate(raw_response)

        assert len(response.games) == 2

        # Check first game
        game1 = response.games[0]
        assert game1.player_id == 2544
        assert game1.player_name == "LeBron James"
        assert game1.nickname == "LeBron"
        assert game1.team_abbreviation == "LAL"
        assert game1.game_id == "0022401185"
        assert game1.matchup == "LAL vs. HOU"
        assert game1.wl == "W"
        assert game1.pts == 28
        assert game1.reb == 12
        assert game1.ast == 10
        assert game1.dd2 == 1  # Double-double
        assert game1.nba_fantasy_pts == 45.5
        assert game1.min_sec == "35:30"

        # Check second game
        game2 = response.games[1]
        assert game2.matchup == "LAL @ DEN"
        assert game2.wl == "L"
        assert game2.pts == 22
        assert game2.dd2 == 0  # No double-double

    def test_parse_empty_result_set(self):
        """Response handles empty result set."""
        headers = self._make_headers()

        raw_response = {
            "resultSets": [{"name": "PlayerGameLogs", "headers": headers, "rowSet": []}]
        }

        response = PlayerGameLogsResponse.model_validate(raw_response)

        assert response.games == []
