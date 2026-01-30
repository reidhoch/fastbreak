"""Tests for LeagueGameLog endpoint."""

from pydantic import ValidationError

from fastbreak.endpoints import LeagueGameLog
from fastbreak.models import LeagueGameLogResponse


class TestLeagueGameLog:
    """Tests for LeagueGameLog endpoint."""

    def test_init_with_defaults(self):
        """LeagueGameLog uses sensible defaults."""
        endpoint = LeagueGameLog()

        assert endpoint.league_id == "00"
        assert endpoint.season == "2024-25"
        assert endpoint.season_type == "Regular Season"
        assert endpoint.player_or_team == "T"
        assert endpoint.counter == 1000
        assert endpoint.sorter == "PTS"
        assert endpoint.direction == "DESC"

    def test_init_with_custom_season(self):
        """LeagueGameLog accepts custom season."""
        endpoint = LeagueGameLog(season="2023-24")

        assert endpoint.season == "2023-24"

    def test_init_with_player_mode(self):
        """LeagueGameLog accepts player mode."""
        endpoint = LeagueGameLog(player_or_team="P")

        assert endpoint.player_or_team == "P"

    def test_init_with_sorting(self):
        """LeagueGameLog accepts sorting parameters."""
        endpoint = LeagueGameLog(sorter="AST", direction="ASC", counter=50)

        assert endpoint.sorter == "AST"
        assert endpoint.direction == "ASC"
        assert endpoint.counter == 50

    def test_init_with_date_filters(self):
        """LeagueGameLog accepts date filters."""
        endpoint = LeagueGameLog(date_from="01/01/2025", date_to="01/31/2025")

        assert endpoint.date_from == "01/01/2025"
        assert endpoint.date_to == "01/31/2025"

    def test_params_returns_correct_dict(self):
        """params() returns correctly formatted parameters."""
        endpoint = LeagueGameLog(
            league_id="00",
            season="2024-25",
            season_type="Playoffs",
            player_or_team="T",
            counter=10,
            sorter="REB",
            direction="ASC",
        )

        params = endpoint.params()

        assert params == {
            "LeagueID": "00",
            "Season": "2024-25",
            "SeasonType": "Playoffs",
            "PlayerOrTeam": "T",
            "Counter": "10",
            "Sorter": "REB",
            "Direction": "ASC",
        }

    def test_params_includes_date_filters(self):
        """params() includes date filters when set."""
        endpoint = LeagueGameLog(date_from="01/01/2025", date_to="01/31/2025")

        params = endpoint.params()

        assert params["DateFrom"] == "01/01/2025"
        assert params["DateTo"] == "01/31/2025"

    def test_params_excludes_none_date_filters(self):
        """params() excludes date filters when not set."""
        endpoint = LeagueGameLog()

        params = endpoint.params()

        assert "DateFrom" not in params
        assert "DateTo" not in params

    def test_path_is_correct(self):
        """LeagueGameLog has correct API path."""
        endpoint = LeagueGameLog()

        assert endpoint.path == "leaguegamelog"

    def test_response_model_is_correct(self):
        """LeagueGameLog uses LeagueGameLogResponse model."""
        endpoint = LeagueGameLog()

        assert endpoint.response_model is LeagueGameLogResponse

    def test_endpoint_is_frozen(self):
        """LeagueGameLog is immutable (frozen dataclass)."""
        endpoint = LeagueGameLog()

        try:
            endpoint.season = "2023-24"  # type: ignore[misc]
            frozen = False
        except (AttributeError, ValidationError):
            frozen = True

        assert frozen, "Endpoint should be frozen (immutable)"


class TestLeagueGameLogResponse:
    """Tests for LeagueGameLogResponse model."""

    def test_parse_tabular_response(self):
        """Response parses NBA's tabular format correctly."""
        raw_response = {
            "resultSets": [
                {
                    "name": "LeagueGameLog",
                    "headers": [
                        "SEASON_ID",
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
                        "STL",
                        "BLK",
                        "TOV",
                        "PF",
                        "PTS",
                        "PLUS_MINUS",
                        "VIDEO_AVAILABLE",
                    ],
                    "rowSet": [
                        [
                            "22024",
                            1610612751,
                            "BKN",
                            "Brooklyn Nets",
                            "0022400571",
                            "2025-01-15",
                            "BKN @ LAC",
                            "L",
                            240,
                            25,
                            83,
                            0.301,
                            5,
                            28,
                            0.179,
                            12,
                            22,
                            0.545,
                            15,
                            24,
                            39,
                            15,
                            9,
                            2,
                            22,
                            16,
                            67,
                            -59,
                            1,
                        ],
                    ],
                },
            ]
        }

        response = LeagueGameLogResponse.model_validate(raw_response)

        assert len(response.games) == 1

        game = response.games[0]
        assert game.team_abbreviation == "BKN"
        assert game.team_name == "Brooklyn Nets"
        assert game.matchup == "BKN @ LAC"
        assert game.wl == "L"
        assert game.pts == 67
        assert game.plus_minus == -59
        assert game.video_available == 1

    def test_parse_empty_response(self):
        """Response handles empty result sets."""
        raw_response = {
            "resultSets": [
                {
                    "name": "LeagueGameLog",
                    "headers": ["SEASON_ID"],
                    "rowSet": [],
                },
            ]
        }

        response = LeagueGameLogResponse.model_validate(raw_response)

        assert response.games == []
