"""Tests for PlayerNextNGames endpoint."""

from pydantic import ValidationError

from fastbreak.endpoints import PlayerNextNGames
from fastbreak.models import PlayerNextNGamesResponse


class TestPlayerNextNGames:
    """Tests for PlayerNextNGames endpoint."""

    def test_init_with_defaults(self):
        """PlayerNextNGames uses sensible defaults."""
        endpoint = PlayerNextNGames(player_id="2544")

        assert endpoint.player_id == "2544"
        assert endpoint.league_id == "00"
        assert endpoint.season == "2024-25"
        assert endpoint.season_type == "Regular Season"
        assert endpoint.number_of_games == "10"

    def test_init_with_player_id(self):
        """PlayerNextNGames accepts player_id."""
        endpoint = PlayerNextNGames(player_id="2544")

        assert endpoint.player_id == "2544"

    def test_params_returns_all_parameters(self):
        """params() returns all query parameters."""
        endpoint = PlayerNextNGames(player_id="2544", number_of_games="5")

        params = endpoint.params()

        assert params["PlayerID"] == "2544"
        assert params["LeagueID"] == "00"
        assert params["Season"] == "2024-25"
        assert params["SeasonType"] == "Regular Season"
        assert params["NumberOfGames"] == "5"

    def test_path_is_correct(self):
        """PlayerNextNGames has correct API path."""
        endpoint = PlayerNextNGames(player_id="2544")

        assert endpoint.path == "playernextngames"

    def test_response_model_is_correct(self):
        """PlayerNextNGames uses correct response model."""
        endpoint = PlayerNextNGames(player_id="2544")

        assert endpoint.response_model is PlayerNextNGamesResponse

    def test_endpoint_is_frozen(self):
        """PlayerNextNGames is immutable (frozen dataclass)."""
        endpoint = PlayerNextNGames(player_id="2544")

        try:
            endpoint.season = "2023-24"  # type: ignore[misc]
            frozen = False
        except (AttributeError, ValidationError):
            frozen = True

        assert frozen


class TestPlayerNextNGamesResponse:
    """Tests for PlayerNextNGamesResponse model."""

    @staticmethod
    def _make_headers() -> list[str]:
        """Return headers for next N games (13 columns)."""
        return [
            "GAME_ID",
            "GAME_DATE",
            "HOME_TEAM_ID",
            "VISITOR_TEAM_ID",
            "HOME_TEAM_NAME",
            "VISITOR_TEAM_NAME",
            "HOME_TEAM_ABBREVIATION",
            "VISITOR_TEAM_ABBREVIATION",
            "HOME_TEAM_NICKNAME",
            "VISITOR_TEAM_NICKNAME",
            "GAME_TIME",
            "HOME_WL",
            "VISITOR_WL",
        ]

    @staticmethod
    def _make_row(
        game_id: str,
        game_date: str,
        home_team_id: int,
        visitor_team_id: int,
        home_abbrev: str,
        visitor_abbrev: str,
    ) -> list:
        """Create a test row for next N games (13 values)."""
        return [
            game_id,
            game_date,
            home_team_id,
            visitor_team_id,
            f"{home_abbrev} Full Name",  # HOME_TEAM_NAME
            f"{visitor_abbrev} Full Name",  # VISITOR_TEAM_NAME
            home_abbrev,
            visitor_abbrev,
            home_abbrev,  # HOME_TEAM_NICKNAME
            visitor_abbrev,  # VISITOR_TEAM_NICKNAME
            "7:30 PM ET",  # GAME_TIME
            None,  # HOME_WL
            None,  # VISITOR_WL
        ]

    def test_parse_tabular_response(self):
        """Response parses NBA's tabular format correctly."""
        headers = self._make_headers()

        raw_response = {
            "resultSets": [
                {
                    "name": "NextNGames",
                    "headers": headers,
                    "rowSet": [
                        self._make_row(
                            "0022401200",
                            "2025-04-15T00:00:00",
                            1610612747,
                            1610612744,
                            "LAL",
                            "GSW",
                        ),
                        self._make_row(
                            "0022401210",
                            "2025-04-17T00:00:00",
                            1610612746,
                            1610612747,
                            "LAC",
                            "LAL",
                        ),
                    ],
                }
            ]
        }

        response = PlayerNextNGamesResponse.model_validate(raw_response)

        assert len(response.games) == 2

        # Check first game
        game1 = response.games[0]
        assert game1.game_id == "0022401200"
        assert game1.game_date == "2025-04-15T00:00:00"
        assert game1.home_team_id == 1610612747
        assert game1.visitor_team_id == 1610612744
        assert game1.home_team_abbreviation == "LAL"
        assert game1.visitor_team_abbreviation == "GSW"
        assert game1.game_time == "7:30 PM ET"
        assert game1.home_wl is None

        # Check second game
        game2 = response.games[1]
        assert game2.home_team_abbreviation == "LAC"
        assert game2.visitor_team_abbreviation == "LAL"

    def test_parse_empty_result_set(self):
        """Response handles empty result set."""
        headers = self._make_headers()

        raw_response = {
            "resultSets": [{"name": "NextNGames", "headers": headers, "rowSet": []}]
        }

        response = PlayerNextNGamesResponse.model_validate(raw_response)

        assert response.games == []
