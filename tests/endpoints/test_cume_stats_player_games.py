"""Tests for CumeStatsPlayerGames endpoint."""

from pydantic import ValidationError

from fastbreak.endpoints.cume_stats_player_games import CumeStatsPlayerGames
from fastbreak.models.cume_stats_player_games import CumeStatsPlayerGamesResponse


class TestCumeStatsPlayerGames:
    """Tests for CumeStatsPlayerGames endpoint."""

    def test_init_with_defaults(self):
        """CumeStatsPlayerGames uses sensible defaults."""
        endpoint = CumeStatsPlayerGames(player_id=2544)

        assert endpoint.league_id == "00"
        assert endpoint.season == "2025"
        assert endpoint.season_type == "Regular Season"
        assert endpoint.player_id == 2544

    def test_init_optional_params_default_to_none(self):
        """CumeStatsPlayerGames optional params default to None."""
        endpoint = CumeStatsPlayerGames(player_id=2544)

        assert endpoint.location is None
        assert endpoint.outcome is None
        assert endpoint.vs_team_id is None
        assert endpoint.vs_division is None
        assert endpoint.vs_conference is None

    def test_init_with_custom_required_params(self):
        """CumeStatsPlayerGames accepts custom required parameters."""
        endpoint = CumeStatsPlayerGames(
            league_id="10",
            season="2026",
            season_type="Playoffs",
            player_id=2544,
        )

        assert endpoint.league_id == "10"
        assert endpoint.season == "2026"
        assert endpoint.season_type == "Playoffs"
        assert endpoint.player_id == 2544

    def test_init_with_optional_filters(self):
        """CumeStatsPlayerGames accepts optional filter parameters."""
        endpoint = CumeStatsPlayerGames(
            player_id=2544,
            location="Home",
            outcome="W",
            vs_team_id=1610612744,
            vs_division="Pacific",
            vs_conference="West",
        )

        assert endpoint.location == "Home"
        assert endpoint.outcome == "W"
        assert endpoint.vs_team_id == 1610612744
        assert endpoint.vs_division == "Pacific"
        assert endpoint.vs_conference == "West"

    def test_params_returns_required_only_when_no_optionals(self):
        """params() returns only required params when no optionals set."""
        endpoint = CumeStatsPlayerGames(player_id=2544)

        params = endpoint.params()

        assert params == {
            "LeagueID": "00",
            "Season": "2025",
            "SeasonType": "Regular Season",
            "PlayerID": "2544",
        }
        assert "Location" not in params
        assert "Outcome" not in params
        assert "VsTeamID" not in params

    def test_params_includes_optional_when_set(self):
        """params() includes optional params when they are set."""
        endpoint = CumeStatsPlayerGames(
            player_id=2544,
            location="Road",
            outcome="L",
        )

        params = endpoint.params()

        assert params["Location"] == "Road"
        assert params["Outcome"] == "L"

    def test_params_includes_all_optional_params_when_set(self):
        """params() includes all optional params when set."""
        endpoint = CumeStatsPlayerGames(
            player_id=2544,
            location="Home",
            outcome="W",
            vs_team_id=1610612744,
            vs_division="Pacific",
            vs_conference="West",
        )

        params = endpoint.params()

        assert params["Location"] == "Home"
        assert params["Outcome"] == "W"
        assert params["VsTeamID"] == "1610612744"
        assert params["VsDivision"] == "Pacific"
        assert params["VsConference"] == "West"

    def test_params_converts_ids_to_strings(self):
        """params() converts integer IDs to strings."""
        endpoint = CumeStatsPlayerGames(
            player_id=2544,
            vs_team_id=1610612744,
        )

        params = endpoint.params()

        assert params["PlayerID"] == "2544"
        assert params["VsTeamID"] == "1610612744"
        assert isinstance(params["PlayerID"], str)
        assert isinstance(params["VsTeamID"], str)

    def test_path_is_correct(self):
        """CumeStatsPlayerGames has correct API path."""
        endpoint = CumeStatsPlayerGames(player_id=2544)

        assert endpoint.path == "cumestatsplayergames"

    def test_response_model_is_correct(self):
        """CumeStatsPlayerGames uses CumeStatsPlayerGamesResponse model."""
        endpoint = CumeStatsPlayerGames(player_id=2544)

        assert endpoint.response_model is CumeStatsPlayerGamesResponse

    def test_endpoint_is_frozen(self):
        """CumeStatsPlayerGames is immutable (frozen dataclass)."""
        endpoint = CumeStatsPlayerGames(player_id=2544)

        try:
            endpoint.season = "2023"  # type: ignore[misc]
            frozen = False
        except (AttributeError, ValidationError):
            frozen = True

        assert frozen, "Endpoint should be frozen (immutable)"
