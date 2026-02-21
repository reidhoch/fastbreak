"""Tests for LeagueDashTeamShotLocations endpoint."""

import pytest
from pydantic import ValidationError

from fastbreak.endpoints import LeagueDashTeamShotLocations
from fastbreak.models import LeagueDashTeamShotLocationsResponse
from fastbreak.utils import get_season_from_date


class TestLeagueDashTeamShotLocations:
    """Tests for LeagueDashTeamShotLocations endpoint."""

    def test_init_with_defaults(self):
        """LeagueDashTeamShotLocations uses sensible defaults."""
        endpoint = LeagueDashTeamShotLocations(team_id=1610612747)

        assert endpoint.season == get_season_from_date()
        assert endpoint.season_type == "Regular Season"
        assert endpoint.per_mode == "PerGame"
        assert endpoint.measure_type == "Base"
        assert endpoint.distance_range == "5ft Range"
        assert endpoint.league_id == "00"

    def test_init_with_custom_params(self):
        """LeagueDashTeamShotLocations accepts custom parameters."""
        endpoint = LeagueDashTeamShotLocations(
            team_id=1610612747,
            season="2023-24",
            season_type="Playoffs",
            per_mode="Totals",
            distance_range="8ft Range",
        )

        assert endpoint.season == "2023-24"
        assert endpoint.season_type == "Playoffs"
        assert endpoint.per_mode == "Totals"
        assert endpoint.distance_range == "8ft Range"

    def test_params_with_defaults_only(self):
        """params() returns required parameters with defaults."""
        endpoint = LeagueDashTeamShotLocations(team_id=1610612747)

        params = endpoint.params()

        assert params["Season"] == get_season_from_date()
        assert params["SeasonType"] == "Regular Season"
        assert params["PerMode"] == "PerGame"
        assert params["MeasureType"] == "Base"
        assert params["DistanceRange"] == "5ft Range"
        assert params["TeamID"] == "1610612747"
        assert "Outcome" not in params
        assert "Location" not in params

    def test_params_with_all_optional_filters(self):
        """params() includes all optional filters when set."""
        endpoint = LeagueDashTeamShotLocations(
            team_id=1610612747,
            outcome="W",
            location="Home",
            date_from="01/01/2025",
            date_to="01/31/2025",
            vs_conference="East",
            vs_division="Atlantic",
            game_segment="First Half",
            conference="West",
            division="Pacific",
            season_segment="Pre All-Star",
        )

        params = endpoint.params()

        assert params["Outcome"] == "W"
        assert params["Location"] == "Home"
        assert params["DateFrom"] == "01/01/2025"
        assert params["DateTo"] == "01/31/2025"
        assert params["VsConference"] == "East"
        assert params["VsDivision"] == "Atlantic"
        assert params["GameSegment"] == "First Half"
        assert params["Conference"] == "West"
        assert params["Division"] == "Pacific"
        assert params["SeasonSegment"] == "Pre All-Star"

    def test_params_with_partial_optional_filters(self):
        """params() includes only set optional filters."""
        endpoint = LeagueDashTeamShotLocations(
            team_id=1610612747,
            outcome="L",
            location="Road",
        )

        params = endpoint.params()

        assert params["Outcome"] == "L"
        assert params["Location"] == "Road"
        assert "DateFrom" not in params
        assert "VsConference" not in params

    def test_path_is_correct(self):
        """LeagueDashTeamShotLocations has correct API path."""
        endpoint = LeagueDashTeamShotLocations(team_id=1610612747)

        assert endpoint.path == "leaguedashteamshotlocations"

    def test_response_model_is_correct(self):
        """LeagueDashTeamShotLocations uses LeagueDashTeamShotLocationsResponse model."""
        endpoint = LeagueDashTeamShotLocations(team_id=1610612747)

        assert endpoint.response_model is LeagueDashTeamShotLocationsResponse

    def test_endpoint_is_frozen(self):
        """LeagueDashTeamShotLocations is immutable (frozen dataclass)."""
        endpoint = LeagueDashTeamShotLocations(team_id=1610612747)

        with pytest.raises((AttributeError, ValidationError)):
            endpoint.team_id = 1610612738  # type: ignore[misc]
