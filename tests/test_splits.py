"""Tests for fastbreak.splits — player and team situational split helpers."""

from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING

import pytest
from hypothesis import given, strategies as st

from fastbreak.clients.nba import NBAClient
from fastbreak.endpoints import (
    PlayerDashboardByGameSplits,
    PlayerDashboardByGeneralSplits,
    PlayerDashboardByLastNGames,
    PlayerDashboardByShootingSplits,
    PlayerDashboardByTeamPerformance,
    TeamDashboardByGeneralSplits,
    TeamDashboardByShootingSplits,
)
from fastbreak.metrics import stat_delta
from fastbreak.splits import (
    PlayerSplitsProfile,
    TeamSplitsProfile,
    get_player_game_splits,
    get_player_general_splits,
    get_player_last_n_games,
    get_player_shooting_splits,
    get_player_splits_profile,
    get_player_team_performance_splits,
    get_team_general_splits,
    get_team_shooting_splits,
    get_team_splits_profile,
)

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


# ─── get_player_game_splits ───────────────────────────────────────────────────


class TestGetPlayerGameSplits:
    """Tests for the get_player_game_splits() async API wrapper."""

    async def test_calls_api_exactly_once(self, mocker: MockerFixture) -> None:
        """get_player_game_splits calls client.get exactly once and returns the response."""
        response = mocker.MagicMock()
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        result = await get_player_game_splits(client, player_id=2544)

        client.get.assert_called_once()
        assert result is response

    async def test_passes_player_id_to_endpoint(self, mocker: MockerFixture) -> None:
        """player_id is forwarded to PlayerDashboardByGameSplits."""
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=mocker.MagicMock())

        await get_player_game_splits(client, player_id=1641705)

        endpoint = client.get.call_args[0][0]
        assert isinstance(endpoint, PlayerDashboardByGameSplits)
        assert endpoint.player_id == 1641705  # noqa: PLR2004

    async def test_season_type_defaults_to_regular_season(
        self, mocker: MockerFixture
    ) -> None:
        """season_type defaults to 'Regular Season'."""
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=mocker.MagicMock())

        await get_player_game_splits(client, player_id=2544)

        endpoint = client.get.call_args[0][0]
        assert endpoint.season_type == "Regular Season"


# ─── get_player_general_splits ────────────────────────────────────────────────


class TestGetPlayerGeneralSplits:
    """Tests for the get_player_general_splits() async API wrapper."""

    async def test_calls_api_exactly_once(self, mocker: MockerFixture) -> None:
        response = mocker.MagicMock()
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        result = await get_player_general_splits(client, player_id=2544)

        client.get.assert_called_once()
        assert result is response

    async def test_passes_player_id_to_endpoint(self, mocker: MockerFixture) -> None:
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=mocker.MagicMock())

        await get_player_general_splits(client, player_id=2544)

        endpoint = client.get.call_args[0][0]
        assert isinstance(endpoint, PlayerDashboardByGeneralSplits)
        assert endpoint.player_id == 2544  # noqa: PLR2004


# ─── get_player_shooting_splits ───────────────────────────────────────────────


class TestGetPlayerShootingSplits:
    """Tests for the get_player_shooting_splits() async API wrapper."""

    async def test_calls_api_exactly_once(self, mocker: MockerFixture) -> None:
        response = mocker.MagicMock()
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        result = await get_player_shooting_splits(client, player_id=2544)

        client.get.assert_called_once()
        assert result is response

    async def test_passes_player_id_to_endpoint(self, mocker: MockerFixture) -> None:
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=mocker.MagicMock())

        await get_player_shooting_splits(client, player_id=2544)

        endpoint = client.get.call_args[0][0]
        assert isinstance(endpoint, PlayerDashboardByShootingSplits)
        assert endpoint.player_id == 2544  # noqa: PLR2004


# ─── get_player_last_n_games ──────────────────────────────────────────────────


class TestGetPlayerLastNGames:
    """Tests for the get_player_last_n_games() async API wrapper."""

    async def test_calls_api_exactly_once(self, mocker: MockerFixture) -> None:
        response = mocker.MagicMock()
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        result = await get_player_last_n_games(client, player_id=2544)

        client.get.assert_called_once()
        assert result is response

    async def test_passes_player_id_to_endpoint(self, mocker: MockerFixture) -> None:
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=mocker.MagicMock())

        await get_player_last_n_games(client, player_id=2544)

        endpoint = client.get.call_args[0][0]
        assert isinstance(endpoint, PlayerDashboardByLastNGames)
        assert endpoint.player_id == 2544  # noqa: PLR2004


# ─── get_player_team_performance_splits ──────────────────────────────────────


class TestGetPlayerTeamPerformanceSplits:
    """Tests for the get_player_team_performance_splits() async API wrapper."""

    async def test_calls_api_exactly_once(self, mocker: MockerFixture) -> None:
        response = mocker.MagicMock()
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        result = await get_player_team_performance_splits(client, player_id=2544)

        client.get.assert_called_once()
        assert result is response

    async def test_passes_player_id_to_endpoint(self, mocker: MockerFixture) -> None:
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=mocker.MagicMock())

        await get_player_team_performance_splits(client, player_id=2544)

        endpoint = client.get.call_args[0][0]
        assert isinstance(endpoint, PlayerDashboardByTeamPerformance)
        assert endpoint.player_id == 2544  # noqa: PLR2004


# ─── get_player_splits_profile ────────────────────────────────────────────────


class TestGetPlayerSplitsProfile:
    """Tests for get_player_splits_profile(), which fetches all 5 splits concurrently."""

    async def test_calls_get_many_once(self, mocker: MockerFixture) -> None:
        """get_player_splits_profile calls client.get_many exactly once."""
        client = NBAClient(session=mocker.MagicMock())
        client.get_many = mocker.AsyncMock(
            return_value=[mocker.MagicMock() for _ in range(5)]
        )

        await get_player_splits_profile(client, player_id=2544)

        client.get_many.assert_called_once()

    async def test_get_many_receives_5_endpoints_in_order(
        self, mocker: MockerFixture
    ) -> None:
        """get_many is called with [GameSplits, GeneralSplits, ShootingSplits, LastN, TeamPerf]."""
        client = NBAClient(session=mocker.MagicMock())
        client.get_many = mocker.AsyncMock(
            return_value=[mocker.MagicMock() for _ in range(5)]
        )

        await get_player_splits_profile(client, player_id=2544)

        endpoints = client.get_many.call_args[0][0]
        assert len(endpoints) == 5  # noqa: PLR2004
        assert isinstance(endpoints[0], PlayerDashboardByGameSplits)
        assert isinstance(endpoints[1], PlayerDashboardByGeneralSplits)
        assert isinstance(endpoints[2], PlayerDashboardByShootingSplits)
        assert isinstance(endpoints[3], PlayerDashboardByLastNGames)
        assert isinstance(endpoints[4], PlayerDashboardByTeamPerformance)

    async def test_profile_fields_populated(self, mocker: MockerFixture) -> None:
        """PlayerSplitsProfile maps get_many results to fields in order."""
        mock_results = [mocker.MagicMock() for _ in range(5)]
        client = NBAClient(session=mocker.MagicMock())
        client.get_many = mocker.AsyncMock(return_value=mock_results)

        profile = await get_player_splits_profile(client, player_id=2544)

        assert isinstance(profile, PlayerSplitsProfile)
        assert profile.player_id == 2544  # noqa: PLR2004
        assert profile.game_splits is mock_results[0]
        assert profile.general_splits is mock_results[1]
        assert profile.shooting_splits is mock_results[2]
        assert profile.last_n_games is mock_results[3]
        assert profile.team_performance is mock_results[4]


# ─── stat_delta ───────────────────────────────────────────────────────────────


class TestStatDelta:
    """Tests for the stat_delta() pure computation helper."""

    # ── Example-based tests ──

    def test_returns_difference(self) -> None:
        """stat_delta returns a - b for two floats."""
        assert stat_delta(0.48, 0.41) == pytest.approx(0.07)

    def test_returns_none_when_a_is_none(self) -> None:
        """stat_delta returns None when a is None."""
        assert stat_delta(None, 0.45) is None

    def test_returns_none_when_b_is_none(self) -> None:
        """stat_delta returns None when b is None."""
        assert stat_delta(0.45, None) is None

    def test_returns_none_when_both_none(self) -> None:
        """stat_delta returns None when both are None."""
        assert stat_delta(None, None) is None

    def test_negative_delta(self) -> None:
        """stat_delta can return negative values when b > a."""
        result = stat_delta(0.40, 0.50)
        assert result is not None
        assert result < 0

    # ── Property-based tests ──

    @given(
        a=st.floats(min_value=-200.0, max_value=200.0, allow_nan=False),
        b=st.floats(min_value=-200.0, max_value=200.0, allow_nan=False),
    )
    def test_antisymmetry(self, a: float, b: float) -> None:
        """stat_delta(a, b) == -stat_delta(b, a) for all finite floats."""
        assert stat_delta(a, b) == pytest.approx(-stat_delta(b, a))  # type: ignore[arg-type]

    @given(a=st.floats(min_value=-200.0, max_value=200.0, allow_nan=False))
    def test_identity(self, a: float) -> None:
        """stat_delta(a, a) == 0.0 for all finite floats."""
        assert stat_delta(a, a) == pytest.approx(0.0)

    @given(b=st.floats(min_value=-200.0, max_value=200.0, allow_nan=False))
    def test_none_propagates_from_a(self, b: float) -> None:
        """None in position a always yields None."""
        assert stat_delta(None, b) is None

    @given(a=st.floats(min_value=-200.0, max_value=200.0, allow_nan=False))
    def test_none_propagates_from_b(self, a: float) -> None:
        """None in position b always yields None."""
        assert stat_delta(a, None) is None


# ─── TeamSplitsProfile ───────────────────────────────────────────────────────


class TestTeamSplitsProfile:
    """Tests for the TeamSplitsProfile frozen dataclass."""

    def test_frozen(self, mocker: MockerFixture) -> None:
        """TeamSplitsProfile is frozen — assignment after creation raises."""
        profile = TeamSplitsProfile(
            team_id=1610612747,
            general=mocker.MagicMock(),
            shooting=mocker.MagicMock(),
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            profile.team_id = 0  # type: ignore[misc]

    def test_slots(self) -> None:
        """TeamSplitsProfile uses __slots__."""
        assert hasattr(TeamSplitsProfile, "__slots__")

    def test_fields(self, mocker: MockerFixture) -> None:
        """All three fields (team_id, general, shooting) are accessible."""
        gen_mock = mocker.MagicMock()
        shoot_mock = mocker.MagicMock()
        profile = TeamSplitsProfile(
            team_id=1610612747,
            general=gen_mock,
            shooting=shoot_mock,
        )
        assert profile.team_id == 1610612747  # noqa: PLR2004
        assert profile.general is gen_mock
        assert profile.shooting is shoot_mock


# ─── get_team_general_splits ─────────────────────────────────────────────────


class TestGetTeamGeneralSplits:
    """Tests for the get_team_general_splits() async API wrapper."""

    async def test_calls_api_once(self, mocker: MockerFixture) -> None:
        """get_team_general_splits calls client.get exactly once."""
        response = mocker.MagicMock()
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        result = await get_team_general_splits(client, team_id=1610612747)

        client.get.assert_called_once()
        assert result is response

    async def test_uses_team_general_splits_endpoint(
        self, mocker: MockerFixture
    ) -> None:
        """Endpoint passed to client.get is TeamDashboardByGeneralSplits."""
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=mocker.MagicMock())

        await get_team_general_splits(client, team_id=1610612747)

        endpoint = client.get.call_args[0][0]
        assert isinstance(endpoint, TeamDashboardByGeneralSplits)

    async def test_passes_team_id(self, mocker: MockerFixture) -> None:
        """team_id is forwarded to the endpoint."""
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=mocker.MagicMock())

        await get_team_general_splits(client, team_id=1610612747)

        endpoint = client.get.call_args[0][0]
        assert endpoint.team_id == 1610612747  # noqa: PLR2004

    async def test_defaults(self, mocker: MockerFixture) -> None:
        """Default season_type is 'Regular Season' and per_mode is 'PerGame'."""
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=mocker.MagicMock())

        await get_team_general_splits(client, team_id=1610612747)

        endpoint = client.get.call_args[0][0]
        assert endpoint.season_type == "Regular Season"
        assert endpoint.per_mode == "PerGame"


# ─── get_team_shooting_splits ────────────────────────────────────────────────


class TestGetTeamShootingSplits:
    """Tests for the get_team_shooting_splits() async API wrapper."""

    async def test_calls_api_once(self, mocker: MockerFixture) -> None:
        """get_team_shooting_splits calls client.get exactly once."""
        response = mocker.MagicMock()
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        result = await get_team_shooting_splits(client, team_id=1610612747)

        client.get.assert_called_once()
        assert result is response

    async def test_uses_team_shooting_splits_endpoint(
        self, mocker: MockerFixture
    ) -> None:
        """Endpoint passed to client.get is TeamDashboardByShootingSplits."""
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=mocker.MagicMock())

        await get_team_shooting_splits(client, team_id=1610612747)

        endpoint = client.get.call_args[0][0]
        assert isinstance(endpoint, TeamDashboardByShootingSplits)

    async def test_passes_team_id(self, mocker: MockerFixture) -> None:
        """team_id is forwarded to the endpoint."""
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=mocker.MagicMock())

        await get_team_shooting_splits(client, team_id=1610612747)

        endpoint = client.get.call_args[0][0]
        assert endpoint.team_id == 1610612747  # noqa: PLR2004

    async def test_defaults(self, mocker: MockerFixture) -> None:
        """Default season_type is 'Regular Season' and per_mode is 'PerGame'."""
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=mocker.MagicMock())

        await get_team_shooting_splits(client, team_id=1610612747)

        endpoint = client.get.call_args[0][0]
        assert endpoint.season_type == "Regular Season"
        assert endpoint.per_mode == "PerGame"


# ─── get_team_splits_profile ─────────────────────────────────────────────────


class TestGetTeamSplitsProfile:
    """Tests for get_team_splits_profile(), which fetches 2 splits concurrently."""

    async def test_calls_get_many_once(self, mocker: MockerFixture) -> None:
        """get_team_splits_profile calls client.get_many exactly once."""
        client = NBAClient(session=mocker.MagicMock())
        client.get_many = mocker.AsyncMock(
            return_value=[mocker.MagicMock() for _ in range(2)]
        )

        await get_team_splits_profile(client, team_id=1610612747)

        client.get_many.assert_called_once()

    async def test_get_many_receives_2_endpoints(self, mocker: MockerFixture) -> None:
        """get_many is called with [GeneralSplits, ShootingSplits]."""
        client = NBAClient(session=mocker.MagicMock())
        client.get_many = mocker.AsyncMock(
            return_value=[mocker.MagicMock() for _ in range(2)]
        )

        await get_team_splits_profile(client, team_id=1610612747)

        endpoints = client.get_many.call_args[0][0]
        assert len(endpoints) == 2  # noqa: PLR2004
        assert isinstance(endpoints[0], TeamDashboardByGeneralSplits)
        assert isinstance(endpoints[1], TeamDashboardByShootingSplits)

    async def test_profile_fields_populated(self, mocker: MockerFixture) -> None:
        """TeamSplitsProfile maps get_many results to fields in order."""
        mock_results = [mocker.MagicMock() for _ in range(2)]
        client = NBAClient(session=mocker.MagicMock())
        client.get_many = mocker.AsyncMock(return_value=mock_results)

        profile = await get_team_splits_profile(client, team_id=1610612747)

        assert isinstance(profile, TeamSplitsProfile)
        assert profile.general is mock_results[0]
        assert profile.shooting is mock_results[1]

    async def test_team_id_stored(self, mocker: MockerFixture) -> None:
        """TeamSplitsProfile stores the team_id passed to the function."""
        client = NBAClient(session=mocker.MagicMock())
        client.get_many = mocker.AsyncMock(
            return_value=[mocker.MagicMock() for _ in range(2)]
        )

        profile = await get_team_splits_profile(client, team_id=1610612747)

        assert profile.team_id == 1610612747  # noqa: PLR2004
