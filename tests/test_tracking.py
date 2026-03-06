"""Tests for fastbreak.tracking — player/team tracking helpers."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastbreak.clients.nba import NBAClient
from fastbreak.endpoints import (
    PlayerDashPtPass,
    PlayerDashPtReb,
    PlayerDashPtShotDefend,
    PlayerDashPtShots,
    TeamDashPtPass,
    TeamDashPtReb,
    TeamDashPtShots,
)
from fastbreak.tracking import (
    PlayerTrackingProfile,
    TeamTrackingProfile,
    get_player_passes,
    get_player_rebounds,
    get_player_shot_defense,
    get_player_shots,
    get_player_tracking_profile,
    get_team_passes,
    get_team_rebounds,
    get_team_shots,
    get_team_tracking_profile,
)

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


# ─── get_player_shots ─────────────────────────────────────────────────────────


class TestGetPlayerShots:
    """Tests for the get_player_shots() async API wrapper."""

    async def test_calls_api_exactly_once(self, mocker: MockerFixture) -> None:
        """get_player_shots calls client.get exactly once and returns the response."""
        response = mocker.MagicMock()
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        result = await get_player_shots(client, player_id=2544)

        client.get.assert_called_once()
        assert result is response

    async def test_passes_player_id_to_endpoint(self, mocker: MockerFixture) -> None:
        """player_id is forwarded to PlayerDashPtShots as a string."""
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=mocker.MagicMock())

        await get_player_shots(client, player_id=201939)

        endpoint = client.get.call_args[0][0]
        assert isinstance(endpoint, PlayerDashPtShots)
        assert endpoint.player_id == "201939"

    async def test_season_type_defaults_to_regular_season(
        self, mocker: MockerFixture
    ) -> None:
        """season_type defaults to 'Regular Season'."""
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=mocker.MagicMock())

        await get_player_shots(client, player_id=2544)

        endpoint = client.get.call_args[0][0]
        assert isinstance(endpoint, PlayerDashPtShots)
        assert endpoint.season_type == "Regular Season"

    async def test_last_n_games_forwarded(self, mocker: MockerFixture) -> None:
        """last_n_games is forwarded as a string."""
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=mocker.MagicMock())

        await get_player_shots(client, player_id=2544, last_n_games=10)

        endpoint = client.get.call_args[0][0]
        assert isinstance(endpoint, PlayerDashPtShots)
        assert endpoint.last_n_games == "10"


# ─── get_player_passes ────────────────────────────────────────────────────────


class TestGetPlayerPasses:
    async def test_calls_api_exactly_once(self, mocker: MockerFixture) -> None:
        response = mocker.MagicMock()
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        result = await get_player_passes(client, player_id=2544)

        client.get.assert_called_once()
        assert result is response

    async def test_passes_player_id_to_endpoint(self, mocker: MockerFixture) -> None:
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=mocker.MagicMock())

        await get_player_passes(client, player_id=2544)

        endpoint = client.get.call_args[0][0]
        assert isinstance(endpoint, PlayerDashPtPass)
        assert endpoint.player_id == 2544


# ─── get_player_rebounds ──────────────────────────────────────────────────────


class TestGetPlayerRebounds:
    async def test_calls_api_exactly_once(self, mocker: MockerFixture) -> None:
        response = mocker.MagicMock()
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        result = await get_player_rebounds(client, player_id=2544)

        client.get.assert_called_once()
        assert result is response

    async def test_passes_player_id_to_endpoint(self, mocker: MockerFixture) -> None:
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=mocker.MagicMock())

        await get_player_rebounds(client, player_id=2544)

        endpoint = client.get.call_args[0][0]
        assert isinstance(endpoint, PlayerDashPtReb)
        assert endpoint.player_id == 2544


# ─── get_player_shot_defense ──────────────────────────────────────────────────


class TestGetPlayerShotDefense:
    async def test_calls_api_exactly_once(self, mocker: MockerFixture) -> None:
        response = mocker.MagicMock()
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        result = await get_player_shot_defense(client, player_id=2544)

        client.get.assert_called_once()
        assert result is response

    async def test_passes_player_id_to_endpoint(self, mocker: MockerFixture) -> None:
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=mocker.MagicMock())

        await get_player_shot_defense(client, player_id=2544)

        endpoint = client.get.call_args[0][0]
        assert isinstance(endpoint, PlayerDashPtShotDefend)
        assert endpoint.player_id == 2544


# ─── get_team_shots ───────────────────────────────────────────────────────────


class TestGetTeamShots:
    async def test_calls_api_exactly_once(self, mocker: MockerFixture) -> None:
        response = mocker.MagicMock()
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        result = await get_team_shots(client, team_id=1610612747)

        client.get.assert_called_once()
        assert result is response

    async def test_passes_team_id_to_endpoint(self, mocker: MockerFixture) -> None:
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=mocker.MagicMock())

        await get_team_shots(client, team_id=1610612747)

        endpoint = client.get.call_args[0][0]
        assert isinstance(endpoint, TeamDashPtShots)
        assert endpoint.team_id == 1610612747


# ─── get_team_passes ──────────────────────────────────────────────────────────


class TestGetTeamPasses:
    async def test_calls_api_exactly_once(self, mocker: MockerFixture) -> None:
        response = mocker.MagicMock()
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        result = await get_team_passes(client, team_id=1610612747)

        client.get.assert_called_once()
        assert result is response

    async def test_passes_team_id_to_endpoint(self, mocker: MockerFixture) -> None:
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=mocker.MagicMock())

        await get_team_passes(client, team_id=1610612747)

        endpoint = client.get.call_args[0][0]
        assert isinstance(endpoint, TeamDashPtPass)
        assert endpoint.team_id == 1610612747


# ─── get_team_rebounds ────────────────────────────────────────────────────────


class TestGetTeamRebounds:
    async def test_calls_api_exactly_once(self, mocker: MockerFixture) -> None:
        response = mocker.MagicMock()
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        result = await get_team_rebounds(client, team_id=1610612747)

        client.get.assert_called_once()
        assert result is response

    async def test_passes_team_id_to_endpoint(self, mocker: MockerFixture) -> None:
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=mocker.MagicMock())

        await get_team_rebounds(client, team_id=1610612747)

        endpoint = client.get.call_args[0][0]
        assert isinstance(endpoint, TeamDashPtReb)
        assert endpoint.team_id == 1610612747


# ─── get_player_tracking_profile ─────────────────────────────────────────────


class TestGetPlayerTrackingProfile:
    async def test_calls_get_many_once(self, mocker: MockerFixture) -> None:
        """get_player_tracking_profile calls client.get_many exactly once."""
        client = NBAClient(session=mocker.MagicMock())
        client.get_many = mocker.AsyncMock(
            return_value=[mocker.MagicMock() for _ in range(4)]
        )

        await get_player_tracking_profile(client, player_id=2544)

        client.get_many.assert_called_once()

    async def test_get_many_receives_4_endpoints_in_order(
        self, mocker: MockerFixture
    ) -> None:
        """get_many is called with [Shots, Pass, Reb, ShotDefend] in that order."""
        client = NBAClient(session=mocker.MagicMock())
        client.get_many = mocker.AsyncMock(
            return_value=[mocker.MagicMock() for _ in range(4)]
        )

        await get_player_tracking_profile(client, player_id=2544)

        endpoints = client.get_many.call_args[0][0]
        assert len(endpoints) == 4  # noqa: PLR2004
        assert isinstance(endpoints[0], PlayerDashPtShots)
        assert isinstance(endpoints[1], PlayerDashPtPass)
        assert isinstance(endpoints[2], PlayerDashPtReb)
        assert isinstance(endpoints[3], PlayerDashPtShotDefend)

    async def test_profile_fields_populated(self, mocker: MockerFixture) -> None:
        """PlayerTrackingProfile maps get_many results to fields in order."""
        mock_results = [mocker.MagicMock() for _ in range(4)]
        client = NBAClient(session=mocker.MagicMock())
        client.get_many = mocker.AsyncMock(return_value=mock_results)

        profile = await get_player_tracking_profile(client, player_id=2544)

        assert isinstance(profile, PlayerTrackingProfile)
        assert profile.player_id == 2544  # noqa: PLR2004
        assert profile.shots is mock_results[0]
        assert profile.passes is mock_results[1]
        assert profile.rebounds is mock_results[2]
        assert profile.shot_defense is mock_results[3]


# ─── get_team_tracking_profile ───────────────────────────────────────────────


class TestGetTeamTrackingProfile:
    async def test_calls_get_many_once(self, mocker: MockerFixture) -> None:
        """get_team_tracking_profile calls client.get_many exactly once."""
        client = NBAClient(session=mocker.MagicMock())
        client.get_many = mocker.AsyncMock(
            return_value=[mocker.MagicMock() for _ in range(3)]
        )

        await get_team_tracking_profile(client, team_id=1610612747)

        client.get_many.assert_called_once()

    async def test_get_many_receives_3_endpoints_in_order(
        self, mocker: MockerFixture
    ) -> None:
        """get_many is called with [Shots, Pass, Reb] in that order."""
        client = NBAClient(session=mocker.MagicMock())
        client.get_many = mocker.AsyncMock(
            return_value=[mocker.MagicMock() for _ in range(3)]
        )

        await get_team_tracking_profile(client, team_id=1610612747)

        endpoints = client.get_many.call_args[0][0]
        assert len(endpoints) == 3  # noqa: PLR2004
        assert isinstance(endpoints[0], TeamDashPtShots)
        assert isinstance(endpoints[1], TeamDashPtPass)
        assert isinstance(endpoints[2], TeamDashPtReb)

    async def test_profile_fields_populated(self, mocker: MockerFixture) -> None:
        """TeamTrackingProfile maps get_many results to fields in order."""
        mock_results = [mocker.MagicMock() for _ in range(3)]
        client = NBAClient(session=mocker.MagicMock())
        client.get_many = mocker.AsyncMock(return_value=mock_results)

        profile = await get_team_tracking_profile(client, team_id=1610612747)

        assert isinstance(profile, TeamTrackingProfile)
        assert profile.team_id == 1610612747  # noqa: PLR2004
        assert profile.shots is mock_results[0]
        assert profile.passes is mock_results[1]
        assert profile.rebounds is mock_results[2]
