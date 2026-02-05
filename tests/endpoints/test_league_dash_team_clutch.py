import pytest
from pydantic import ValidationError

from fastbreak.endpoints import LeagueDashTeamClutch
from fastbreak.models import LeagueDashTeamClutchResponse


class TestLeagueDashTeamClutch:
    """Tests for LeagueDashTeamClutch endpoint."""

    def test_init_with_defaults(self):
        """LeagueDashTeamClutch uses sensible defaults."""
        endpoint = LeagueDashTeamClutch()

        assert endpoint.league_id == "00"
        assert endpoint.season == "2024-25"
        assert endpoint.season_type == "Regular Season"
        assert endpoint.clutch_time == "Last 5 Minutes"
        assert endpoint.ahead_behind == "Ahead or Behind"
        assert endpoint.point_diff == 5
        assert endpoint.measure_type == "Base"
        assert endpoint.per_mode == "Per100Possessions"

    def test_init_with_custom_season(self):
        """LeagueDashTeamClutch accepts custom season."""
        endpoint = LeagueDashTeamClutch(season="2023-24")

        assert endpoint.season == "2023-24"

    def test_init_with_custom_clutch_time(self):
        """LeagueDashTeamClutch accepts custom clutch_time."""
        endpoint = LeagueDashTeamClutch(clutch_time="Last 2 Minutes")

        assert endpoint.clutch_time == "Last 2 Minutes"

    def test_init_with_custom_ahead_behind(self):
        """LeagueDashTeamClutch accepts custom ahead_behind."""
        endpoint = LeagueDashTeamClutch(ahead_behind="Ahead or Tied")

        assert endpoint.ahead_behind == "Ahead or Tied"

    def test_init_with_custom_point_diff(self):
        """LeagueDashTeamClutch accepts custom point_diff."""
        endpoint = LeagueDashTeamClutch(point_diff=3)

        assert endpoint.point_diff == 3

    def test_init_with_custom_measure_type(self):
        """LeagueDashTeamClutch accepts custom measure_type."""
        endpoint = LeagueDashTeamClutch(measure_type="Advanced")

        assert endpoint.measure_type == "Advanced"

    def test_init_with_optional_filters(self):
        """LeagueDashTeamClutch accepts optional filters."""
        endpoint = LeagueDashTeamClutch(
            conference="East",
            division="Atlantic",
            location="Home",
            outcome="W",
        )

        assert endpoint.conference == "East"
        assert endpoint.division == "Atlantic"
        assert endpoint.location == "Home"
        assert endpoint.outcome == "W"

    def test_params_returns_correct_dict(self):
        """params() returns correctly formatted parameters."""
        endpoint = LeagueDashTeamClutch()

        params = endpoint.params()

        assert params["LeagueID"] == "00"
        assert params["Season"] == "2024-25"
        assert params["SeasonType"] == "Regular Season"
        assert params["ClutchTime"] == "Last 5 Minutes"
        assert params["AheadBehind"] == "Ahead or Behind"
        assert params["PointDiff"] == "5"
        assert params["MeasureType"] == "Base"
        assert params["PerMode"] == "Per100Possessions"

    def test_params_with_optional_filters(self):
        """params() correctly includes optional filters."""
        endpoint = LeagueDashTeamClutch(
            conference="West",
            division="Pacific",
        )

        params = endpoint.params()

        assert params["Conference"] == "West"
        assert params["Division"] == "Pacific"

    def test_params_empty_string_for_unset_filters(self):
        """params() uses empty string for unset optional filters."""
        endpoint = LeagueDashTeamClutch()

        params = endpoint.params()

        assert params["Conference"] == ""
        assert params["Division"] == ""
        assert params["DateFrom"] == ""
        assert params["DateTo"] == ""

    def test_path_is_correct(self):
        """LeagueDashTeamClutch has correct API path."""
        endpoint = LeagueDashTeamClutch()

        assert endpoint.path == "leaguedashteamclutch"

    def test_response_model_is_correct(self):
        """LeagueDashTeamClutch uses LeagueDashTeamClutchResponse model."""
        endpoint = LeagueDashTeamClutch()

        assert endpoint.response_model is LeagueDashTeamClutchResponse

    def test_endpoint_is_frozen(self):
        """LeagueDashTeamClutch is immutable (frozen dataclass)."""
        endpoint = LeagueDashTeamClutch()

        with pytest.raises((AttributeError, ValidationError)):
            endpoint.season = "2023-24"  # type: ignore[misc]
