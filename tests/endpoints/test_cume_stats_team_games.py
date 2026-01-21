"""Tests for CumeStatsTeamGames endpoint."""

from fastbreak.endpoints.cume_stats_team_games import CumeStatsTeamGames
from fastbreak.models.cume_stats_team_games import CumeStatsTeamGamesResponse


class TestCumeStatsTeamGames:
    """Tests for CumeStatsTeamGames endpoint."""

    def test_init_with_defaults(self):
        """CumeStatsTeamGames uses sensible defaults."""
        endpoint = CumeStatsTeamGames()

        assert endpoint.league_id == "00"
        assert endpoint.season_id == "2024-25"
        assert endpoint.season_type == "Regular Season"
        assert endpoint.team_id == 0

    def test_init_optional_params_default_to_none(self):
        """CumeStatsTeamGames optional params default to None."""
        endpoint = CumeStatsTeamGames()

        assert endpoint.location is None
        assert endpoint.outcome is None
        assert endpoint.vs_team_id is None
        assert endpoint.vs_division is None
        assert endpoint.vs_conference is None

    def test_init_with_custom_required_params(self):
        """CumeStatsTeamGames accepts custom required parameters."""
        endpoint = CumeStatsTeamGames(
            league_id="10",
            season_id="2025-26",
            season_type="Playoffs",
            team_id=1610612745,
        )

        assert endpoint.league_id == "10"
        assert endpoint.season_id == "2025-26"
        assert endpoint.season_type == "Playoffs"
        assert endpoint.team_id == 1610612745

    def test_init_with_optional_filters(self):
        """CumeStatsTeamGames accepts optional filter parameters."""
        endpoint = CumeStatsTeamGames(
            team_id=1610612745,
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
        endpoint = CumeStatsTeamGames(team_id=1610612745)

        params = endpoint.params()

        assert params == {
            "LeagueID": "00",
            "SeasonID": "2024-25",
            "SeasonType": "Regular Season",
            "TeamID": "1610612745",
        }
        assert "Location" not in params
        assert "Outcome" not in params
        assert "VsTeamID" not in params

    def test_params_uses_season_id_not_season(self):
        """params() uses SeasonID parameter (not Season)."""
        endpoint = CumeStatsTeamGames(season_id="2025-26")

        params = endpoint.params()

        assert "SeasonID" in params
        assert "Season" not in params
        assert params["SeasonID"] == "2025-26"

    def test_params_includes_optional_when_set(self):
        """params() includes optional params when they are set."""
        endpoint = CumeStatsTeamGames(
            team_id=1610612745,
            location="Road",
            outcome="L",
        )

        params = endpoint.params()

        assert params["Location"] == "Road"
        assert params["Outcome"] == "L"

    def test_params_includes_all_optional_params_when_set(self):
        """params() includes all optional params when set."""
        endpoint = CumeStatsTeamGames(
            team_id=1610612745,
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
        endpoint = CumeStatsTeamGames(
            team_id=1610612745,
            vs_team_id=1610612744,
        )

        params = endpoint.params()

        assert params["TeamID"] == "1610612745"
        assert params["VsTeamID"] == "1610612744"
        assert isinstance(params["TeamID"], str)
        assert isinstance(params["VsTeamID"], str)

    def test_path_is_correct(self):
        """CumeStatsTeamGames has correct API path."""
        endpoint = CumeStatsTeamGames()

        assert endpoint.path == "cumestatsteamgames"

    def test_response_model_is_correct(self):
        """CumeStatsTeamGames uses CumeStatsTeamGamesResponse model."""
        endpoint = CumeStatsTeamGames()

        assert endpoint.response_model is CumeStatsTeamGamesResponse

    def test_endpoint_is_frozen(self):
        """CumeStatsTeamGames is immutable (frozen dataclass)."""
        endpoint = CumeStatsTeamGames()

        try:
            endpoint.season_id = "2023-24"  # type: ignore[misc]
            frozen = False
        except AttributeError:
            frozen = True

        assert frozen, "Endpoint should be frozen (immutable)"
