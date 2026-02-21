"""Tests for PlayerDashPtPass endpoint."""

import pytest
from pydantic import ValidationError

from fastbreak.endpoints import PlayerDashPtPass
from fastbreak.models import PlayerDashPtPassResponse
from fastbreak.utils import get_season_from_date


class TestPlayerDashPtPass:
    """Tests for PlayerDashPtPass endpoint."""

    def test_init_with_defaults(self):
        """PlayerDashPtPass uses sensible defaults."""
        endpoint = PlayerDashPtPass(player_id=2544)

        assert endpoint.player_id == 2544
        assert endpoint.league_id == "00"
        assert endpoint.season == get_season_from_date()
        assert endpoint.per_mode == "PerGame"
        # Always-sent params have default 0
        assert endpoint.team_id == 0
        assert endpoint.month == 0
        assert endpoint.opponent_team_id == 0
        assert endpoint.last_n_games == 0

    def test_init_with_player_id(self):
        """PlayerDashPtPass accepts player_id."""
        endpoint = PlayerDashPtPass(player_id=203999)

        assert endpoint.player_id == 203999

    def test_init_with_optional_filters(self):
        """PlayerDashPtPass accepts optional filters."""
        endpoint = PlayerDashPtPass(
            player_id=203999,
            season="2023-24",
            outcome="W",
            ist_round="Finals",
        )

        assert endpoint.season == "2023-24"
        assert endpoint.outcome == "W"
        assert endpoint.ist_round == "Finals"

    def test_params_with_required_only(self):
        """params() returns required and always-sent parameters."""
        endpoint = PlayerDashPtPass(player_id=203999)

        params = endpoint.params()

        assert params == {
            "PlayerID": "203999",
            "LeagueID": "00",
            "Season": get_season_from_date(),
            "SeasonType": "Regular Season",
            "PerMode": "PerGame",
            "TeamID": "0",
            "Month": "0",
            "OpponentTeamID": "0",
            "LastNGames": "0",
        }

    def test_params_with_filters(self):
        """params() includes optional filters when set."""
        endpoint = PlayerDashPtPass(
            player_id=203999,
            outcome="W",
            location="Home",
            ist_round="Finals",
        )

        params = endpoint.params()

        assert params["PlayerID"] == "203999"
        assert params["Outcome"] == "W"
        assert params["Location"] == "Home"
        assert params["ISTRound"] == "Finals"

    def test_path_is_correct(self):
        """PlayerDashPtPass has correct API path."""
        endpoint = PlayerDashPtPass(player_id=2544)

        assert endpoint.path == "playerdashptpass"

    def test_response_model_is_correct(self):
        """PlayerDashPtPass uses correct response model."""
        endpoint = PlayerDashPtPass(player_id=2544)

        assert endpoint.response_model is PlayerDashPtPassResponse

    def test_endpoint_is_frozen(self):
        """PlayerDashPtPass is immutable (frozen dataclass)."""
        endpoint = PlayerDashPtPass(player_id=2544)

        with pytest.raises((AttributeError, ValidationError)):
            endpoint.season = "2023-24"  # type: ignore[misc]


class TestPlayerDashPtPassResponse:
    """Tests for PlayerDashPtPassResponse model."""

    @staticmethod
    def _make_passes_made_headers() -> list[str]:
        """Return headers for passes made result set (21 columns)."""
        return [
            "PLAYER_ID",
            "PLAYER_NAME_LAST_FIRST",
            "TEAM_NAME",
            "TEAM_ID",
            "TEAM_ABBREVIATION",
            "PASS_TYPE",
            "G",
            "PASS_TO",
            "PASS_TEAMMATE_PLAYER_ID",
            "FREQUENCY",
            "PASS",
            "AST",
            "FGM",
            "FGA",
            "FG_PCT",
            "FG2M",
            "FG2A",
            "FG2_PCT",
            "FG3M",
            "FG3A",
            "FG3_PCT",
        ]

    @staticmethod
    def _make_passes_received_headers() -> list[str]:
        """Return headers for passes received result set (21 columns)."""
        return [
            "PLAYER_ID",
            "PLAYER_NAME_LAST_FIRST",
            "TEAM_NAME",
            "TEAM_ID",
            "TEAM_ABBREVIATION",
            "PASS_TYPE",
            "G",
            "PASS_FROM",
            "PASS_TEAMMATE_PLAYER_ID",
            "FREQUENCY",
            "PASS",
            "AST",
            "FGM",
            "FGA",
            "FG_PCT",
            "FG2M",
            "FG2A",
            "FG2_PCT",
            "FG3M",
            "FG3A",
            "FG3_PCT",
        ]

    @staticmethod
    def _make_pass_made_row(
        player_id: int,
        player_name: str,
        pass_to: str,
        teammate_id: int,
        passes: float,
        ast: float,
    ) -> list:
        """Create a test row for passes made (21 values)."""
        return [
            player_id,
            player_name,
            "Denver Nuggets",
            1610612743,
            "DEN",
            "made",
            8,
            pass_to,
            teammate_id,
            0.1,  # frequency
            passes,
            ast,
            ast,  # fgm
            passes,  # fga
            ast / passes if passes > 0 else 0.0,  # fg_pct
            ast * 0.6,  # fg2m
            passes * 0.6,  # fg2a
            0.5,  # fg2_pct
            ast * 0.4,  # fg3m
            passes * 0.4,  # fg3a
            0.4,  # fg3_pct
        ]

    @staticmethod
    def _make_pass_received_row(
        player_id: int,
        player_name: str,
        pass_from: str,
        teammate_id: int,
        passes: float,
        ast: float,
    ) -> list:
        """Create a test row for passes received (21 values)."""
        return [
            player_id,
            player_name,
            "Denver Nuggets",
            1610612743,
            "DEN",
            "received",
            8,
            pass_from,
            teammate_id,
            0.1,  # frequency
            passes,
            ast,
            ast,  # fgm
            passes,  # fga
            ast / passes if passes > 0 else 0.0,  # fg_pct
            ast * 0.6,  # fg2m
            passes * 0.6,  # fg2a
            0.5,  # fg2_pct
            ast * 0.4,  # fg3m
            passes * 0.4,  # fg3a
            0.4,  # fg3_pct
        ]

    def test_parse_tabular_response(self):
        """Response parses NBA's tabular format correctly."""
        made_headers = self._make_passes_made_headers()
        received_headers = self._make_passes_received_headers()

        raw_response = {
            "resultSets": [
                {
                    "name": "PassesMade",
                    "headers": made_headers,
                    "rowSet": [
                        self._make_pass_made_row(
                            203999,
                            "Jokić, Nikola",
                            "Watson, Peyton",
                            1631212,
                            7.0,
                            0.75,
                        ),
                        self._make_pass_made_row(
                            203999, "Jokić, Nikola", "Gordon, Aaron", 203932, 6.0, 1.0
                        ),
                    ],
                },
                {
                    "name": "PassesReceived",
                    "headers": received_headers,
                    "rowSet": [
                        self._make_pass_received_row(
                            203999, "Jokić, Nikola", "Murray, Jamal", 1627750, 5.0, 0.5
                        ),
                    ],
                },
            ]
        }

        response = PlayerDashPtPassResponse.model_validate(raw_response)

        # Check passes made
        assert len(response.passes_made) == 2
        assert response.passes_made[0].player_id == 203999
        assert response.passes_made[0].pass_to == "Watson, Peyton"
        assert response.passes_made[0].pass_teammate_player_id == 1631212
        assert response.passes_made[0].passes == 7.0
        assert response.passes_made[1].pass_to == "Gordon, Aaron"

        # Check passes received
        assert len(response.passes_received) == 1
        assert response.passes_received[0].pass_from == "Murray, Jamal"
        assert response.passes_received[0].pass_teammate_player_id == 1627750
        assert response.passes_received[0].passes == 5.0

    def test_parse_empty_result_sets(self):
        """Response handles empty result sets."""
        made_headers = self._make_passes_made_headers()
        received_headers = self._make_passes_received_headers()

        raw_response = {
            "resultSets": [
                {"name": "PassesMade", "headers": made_headers, "rowSet": []},
                {"name": "PassesReceived", "headers": received_headers, "rowSet": []},
            ]
        }

        response = PlayerDashPtPassResponse.model_validate(raw_response)

        assert response.passes_made == []
        assert response.passes_received == []
