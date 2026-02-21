"""Tests for the Endpoint base class and its subclasses.

Tests cover:
- __init_subclass__ validation for required ClassVars
- _is_base_endpoint flag for intermediate base classes
- Dashboard endpoint parameter building
"""

from typing import ClassVar

import pytest
from pydantic import BaseModel

from fastbreak.endpoints.base import (
    DashboardEndpoint,
    DraftCombineEndpoint,
    Endpoint,
    GameIdEndpoint,
    PlayerDashboardEndpoint,
    TeamDashboardEndpoint,
)
from fastbreak.utils import get_season_from_date

# =============================================================================
# Test Response Model
# =============================================================================


class DummyResponse(BaseModel):
    """Dummy response model for testing."""

    data: str = "test"


# =============================================================================
# Endpoint Subclass Validation Tests
# =============================================================================


class TestEndpointSubclassValidation:
    """Tests for __init_subclass__ validation."""

    def test_valid_endpoint_definition(self):
        """Valid endpoint with both path and response_model works."""

        class ValidEndpoint(Endpoint[DummyResponse]):
            path = "test/endpoint"
            response_model = DummyResponse

            def params(self):
                return {}

        assert ValidEndpoint.path == "test/endpoint"
        assert ValidEndpoint.response_model == DummyResponse

    def test_missing_path_raises_type_error(self):
        """Subclass without path ClassVar raises TypeError."""
        with pytest.raises(TypeError, match="must define 'path' ClassVar"):

            class MissingPathEndpoint(Endpoint[DummyResponse]):
                response_model = DummyResponse

                def params(self):
                    return {}

    def test_missing_response_model_raises_type_error(self):
        """Subclass without response_model ClassVar raises TypeError."""
        with pytest.raises(TypeError, match="must define 'response_model' ClassVar"):

            class MissingResponseModelEndpoint(Endpoint[DummyResponse]):
                path = "test"

                def params(self):
                    return {}

    def test_missing_both_raises_type_error_for_path(self):
        """Subclass missing both raises TypeError for path (checked first)."""
        with pytest.raises(TypeError, match="must define 'path' ClassVar"):

            class MissingBothEndpoint(Endpoint[DummyResponse]):
                def params(self):
                    return {}

    def test_base_endpoint_flag_skips_validation(self):
        """Classes with _is_base_endpoint=True skip validation."""

        class IntermediateEndpoint(Endpoint[DummyResponse]):
            _is_base_endpoint: ClassVar[bool] = True

        # Should not raise - class defined successfully
        assert IntermediateEndpoint._is_base_endpoint is True

    def test_inheriting_from_intermediate_requires_classvars(self):
        """Concrete subclass of intermediate base still needs ClassVars."""

        class IntermediateEndpoint(Endpoint[DummyResponse]):
            _is_base_endpoint: ClassVar[bool] = True

        with pytest.raises(TypeError, match="must define 'path' ClassVar"):

            class ConcreteEndpoint(IntermediateEndpoint):
                def params(self):
                    return {}

    def test_inheriting_path_from_intermediate(self):
        """Intermediate can define path, concrete only needs response_model."""

        class IntermediateWithPath(Endpoint[DummyResponse]):
            _is_base_endpoint: ClassVar[bool] = True
            path: ClassVar[str] = "shared/path"

        class ConcreteEndpoint(IntermediateWithPath):
            response_model = DummyResponse

            def params(self):
                return {}

        assert ConcreteEndpoint.path == "shared/path"

    def test_inheriting_response_model_from_intermediate(self):
        """Intermediate can define response_model, concrete only needs path."""

        class IntermediateWithModel(Endpoint[DummyResponse]):
            _is_base_endpoint: ClassVar[bool] = True
            response_model: ClassVar[type[DummyResponse]] = DummyResponse

        class ConcreteEndpoint(IntermediateWithModel):
            path: ClassVar[str] = "concrete/path"

            def params(self):
                return {}

        assert ConcreteEndpoint.response_model == DummyResponse


# =============================================================================
# Base Endpoint Classes Tests
# =============================================================================


class TestGameIdEndpointBase:
    """Tests for GameIdEndpoint base class."""

    def test_is_base_endpoint_flag_set(self):
        """GameIdEndpoint has _is_base_endpoint=True."""
        assert GameIdEndpoint._is_base_endpoint is True

    def test_subclass_only_needs_path_and_response_model(self):
        """GameIdEndpoint subclass only needs path and response_model."""

        class BoxScoreEndpoint(GameIdEndpoint[DummyResponse]):
            path = "boxscoretraditionalv3"
            response_model = DummyResponse

        endpoint = BoxScoreEndpoint(game_id="0022400123")
        assert endpoint.params() == {"GameID": "0022400123"}

    def test_params_returns_game_id(self):
        """GameIdEndpoint.params() returns GameID parameter."""

        class TestEndpoint(GameIdEndpoint[DummyResponse]):
            path = "test"
            response_model = DummyResponse

        endpoint = TestEndpoint(game_id="0022400001")
        assert endpoint.params() == {"GameID": "0022400001"}


class TestDraftCombineEndpointBase:
    """Tests for DraftCombineEndpoint base class."""

    def test_is_base_endpoint_flag_set(self):
        """DraftCombineEndpoint has _is_base_endpoint=True."""
        assert DraftCombineEndpoint._is_base_endpoint is True

    def test_default_parameters(self):
        """DraftCombineEndpoint has correct default parameters."""

        class TestEndpoint(DraftCombineEndpoint[DummyResponse]):
            path = "draftcombinestats"
            response_model = DummyResponse

        endpoint = TestEndpoint()
        assert endpoint.league_id == "00"
        assert endpoint.season_year == get_season_from_date()

    def test_params_returns_correct_dict(self):
        """DraftCombineEndpoint.params() returns correct parameters."""

        class TestEndpoint(DraftCombineEndpoint[DummyResponse]):
            path = "draftcombinestats"
            response_model = DummyResponse

        endpoint = TestEndpoint(league_id="00", season_year="2023-24")
        params = endpoint.params()
        assert params == {"LeagueID": "00", "SeasonYear": "2023-24"}


# =============================================================================
# Dashboard Endpoint Classes Tests
# =============================================================================


class TestDashboardEndpointBase:
    """Tests for DashboardEndpoint base class."""

    def test_is_base_endpoint_flag_set(self):
        """DashboardEndpoint has _is_base_endpoint=True."""
        assert DashboardEndpoint._is_base_endpoint is True

    def test_default_parameters(self):
        """DashboardEndpoint has correct default parameters."""
        # Check defaults on the actual base class rather than creating a subclass
        assert DashboardEndpoint.model_fields["league_id"].default == "00"
        assert (
            DashboardEndpoint.model_fields["season"].default_factory()
            == get_season_from_date()
        )
        assert DashboardEndpoint.model_fields["season_type"].default == "Regular Season"
        assert DashboardEndpoint.model_fields["per_mode"].default == "PerGame"


class TestPlayerDashboardEndpointBase:
    """Tests for PlayerDashboardEndpoint base class."""

    def test_is_base_endpoint_flag_set(self):
        """PlayerDashboardEndpoint has _is_base_endpoint=True."""
        assert PlayerDashboardEndpoint._is_base_endpoint is True

    def test_requires_player_id(self):
        """PlayerDashboardEndpoint requires player_id."""

        class TestEndpoint(PlayerDashboardEndpoint[DummyResponse]):
            path = "playerdashboardbygeneralsplits"
            response_model = DummyResponse

        endpoint = TestEndpoint(player_id=2544)
        assert endpoint.player_id == 2544

    def test_params_includes_player_id(self):
        """PlayerDashboardEndpoint.params() includes PlayerID."""

        class TestEndpoint(PlayerDashboardEndpoint[DummyResponse]):
            path = "test"
            response_model = DummyResponse

        endpoint = TestEndpoint(player_id=2544)
        params = endpoint.params()
        assert params["PlayerID"] == "2544"

    def test_params_includes_base_params(self):
        """PlayerDashboardEndpoint.params() includes all base params."""

        class TestEndpoint(PlayerDashboardEndpoint[DummyResponse]):
            path = "test"
            response_model = DummyResponse

        endpoint = TestEndpoint(player_id=2544)
        params = endpoint.params()

        # Check some base params are included
        assert "LeagueID" in params
        assert "Season" in params
        assert "SeasonType" in params
        assert "PerMode" in params
        assert "PlayerID" in params

    def test_ist_round_parameter_optional(self):
        """ist_round parameter is optional."""

        class TestEndpoint(PlayerDashboardEndpoint[DummyResponse]):
            path = "test"
            response_model = DummyResponse

        endpoint = TestEndpoint(player_id=2544)
        assert endpoint.ist_round is None
        assert "ISTRound" not in endpoint.params()

    def test_ist_round_included_when_set(self):
        """ist_round is included in params when set."""

        class TestEndpoint(PlayerDashboardEndpoint[DummyResponse]):
            path = "test"
            response_model = DummyResponse

        endpoint = TestEndpoint(player_id=2544, ist_round="Round 1")
        params = endpoint.params()
        assert params["ISTRound"] == "Round 1"

    def test_optional_params_not_included_when_none(self):
        """Optional params are not included when None."""

        class TestEndpoint(PlayerDashboardEndpoint[DummyResponse]):
            path = "test"
            response_model = DummyResponse

        endpoint = TestEndpoint(player_id=2544)
        params = endpoint.params()

        # These should not be in params when None
        assert "Outcome" not in params
        assert "Location" not in params
        assert "DateFrom" not in params
        assert "DateTo" not in params

    def test_optional_params_included_when_set(self):
        """Optional params are included when set."""

        class TestEndpoint(PlayerDashboardEndpoint[DummyResponse]):
            path = "test"
            response_model = DummyResponse

        endpoint = TestEndpoint(
            player_id=2544,
            outcome="W",
            location="Home",
            date_from="01/01/2025",
            date_to="01/31/2025",
        )
        params = endpoint.params()

        assert params["Outcome"] == "W"
        assert params["Location"] == "Home"
        assert params["DateFrom"] == "01/01/2025"
        assert params["DateTo"] == "01/31/2025"


class TestTeamDashboardEndpointBase:
    """Tests for TeamDashboardEndpoint base class."""

    def test_is_base_endpoint_flag_set(self):
        """TeamDashboardEndpoint has _is_base_endpoint=True."""
        assert TeamDashboardEndpoint._is_base_endpoint is True

    def test_requires_team_id(self):
        """TeamDashboardEndpoint requires team_id."""

        class TestEndpoint(TeamDashboardEndpoint[DummyResponse]):
            path = "teamdashboardbygeneralsplits"
            response_model = DummyResponse

        endpoint = TestEndpoint(team_id=1610612744)
        assert endpoint.team_id == 1610612744

    def test_params_includes_team_id(self):
        """TeamDashboardEndpoint.params() includes TeamID."""

        class TestEndpoint(TeamDashboardEndpoint[DummyResponse]):
            path = "test"
            response_model = DummyResponse

        endpoint = TestEndpoint(team_id=1610612744)
        params = endpoint.params()
        assert params["TeamID"] == "1610612744"

    def test_params_includes_base_params(self):
        """TeamDashboardEndpoint.params() includes all base params."""

        class TestEndpoint(TeamDashboardEndpoint[DummyResponse]):
            path = "test"
            response_model = DummyResponse

        endpoint = TestEndpoint(team_id=1610612744)
        params = endpoint.params()

        # Check some base params are included
        assert "LeagueID" in params
        assert "Season" in params
        assert "SeasonType" in params
        assert "PerMode" in params
        assert "TeamID" in params


# =============================================================================
# Endpoint Immutability Tests
# =============================================================================


class TestEndpointFrozen:
    """Tests for endpoint immutability (frozen=True)."""

    def test_endpoint_is_frozen(self):
        """Endpoint instances are frozen (immutable)."""

        class TestEndpoint(Endpoint[DummyResponse]):
            path = "test"
            response_model = DummyResponse
            value: str = "initial"

            def params(self):
                return {"value": self.value}

        endpoint = TestEndpoint(value="test")

        with pytest.raises(Exception):  # ValidationError for frozen model
            endpoint.value = "changed"

    def test_game_id_endpoint_is_frozen(self):
        """GameIdEndpoint instances are frozen."""

        class TestEndpoint(GameIdEndpoint[DummyResponse]):
            path = "test"
            response_model = DummyResponse

        endpoint = TestEndpoint(game_id="0022400001")

        with pytest.raises(Exception):
            endpoint.game_id = "0022400002"

    def test_player_dashboard_endpoint_is_frozen(self):
        """PlayerDashboardEndpoint instances are frozen."""

        class TestEndpoint(PlayerDashboardEndpoint[DummyResponse]):
            path = "test"
            response_model = DummyResponse

        endpoint = TestEndpoint(player_id=2544)

        with pytest.raises(Exception):
            endpoint.player_id = 201939


# =============================================================================
# Parse Response Tests
# =============================================================================


class TestEndpointParseResponse:
    """Tests for Endpoint.parse_response method."""

    def test_parse_response_uses_response_model(self):
        """parse_response uses the response_model to validate data."""

        class TestEndpoint(Endpoint[DummyResponse]):
            path = "test"
            response_model = DummyResponse

            def params(self):
                return {}

        endpoint = TestEndpoint()
        result = endpoint.parse_response({"data": "test value"})

        assert isinstance(result, DummyResponse)
        assert result.data == "test value"

    def test_parse_response_with_default_values(self):
        """parse_response handles missing fields with defaults."""

        class TestEndpoint(Endpoint[DummyResponse]):
            path = "test"
            response_model = DummyResponse

            def params(self):
                return {}

        endpoint = TestEndpoint()
        result = endpoint.parse_response({})

        assert isinstance(result, DummyResponse)
        assert result.data == "test"  # Default value
