"""Tests that Synergy playtype helpers warn about restricted data."""

import warnings

import pytest
from pytest_mock import MockerFixture

from fastbreak.clients.nba import NBAClient


def _make_synergy_client(mocker: MockerFixture):
    """Return NBAClient whose .get() resolves to a mock with empty player/team stats."""
    response = mocker.MagicMock()
    response.player_stats = []
    response.team_stats = []
    client = NBAClient(session=mocker.MagicMock())
    client.get = mocker.AsyncMock(return_value=response)
    return client


class TestGetPlayerPlaytypesWarning:
    """get_player_playtypes warns about restricted Synergy data."""

    async def test_emits_user_warning(self, mocker: MockerFixture):
        """get_player_playtypes emits UserWarning about restricted data."""
        from fastbreak.players import get_player_playtypes

        client = _make_synergy_client(mocker)

        with pytest.warns(UserWarning, match="SynergyPlaytypes"):
            await get_player_playtypes(client, player_id=2544)

    async def test_warning_mentions_empty(self, mocker: MockerFixture):
        """Warning message mentions that data is restricted/empty."""
        from fastbreak.players import get_player_playtypes

        client = _make_synergy_client(mocker)

        with pytest.warns(UserWarning, match="restricted"):
            await get_player_playtypes(client, player_id=2544)

    async def test_still_returns_list(self, mocker: MockerFixture):
        """get_player_playtypes still returns a list despite the warning."""
        from fastbreak.players import get_player_playtypes

        client = _make_synergy_client(mocker)

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = await get_player_playtypes(client, player_id=2544)

        assert isinstance(result, list)


class TestGetTeamPlaytypesWarning:
    """get_team_playtypes warns about restricted Synergy data."""

    async def test_emits_user_warning(self, mocker: MockerFixture):
        """get_team_playtypes emits UserWarning about restricted data."""
        from fastbreak.teams import get_team_playtypes

        client = _make_synergy_client(mocker)

        with pytest.warns(UserWarning, match="SynergyPlaytypes"):
            await get_team_playtypes(client, team_id=1610612754)

    async def test_warning_mentions_restricted(self, mocker: MockerFixture):
        """Warning message mentions that data is restricted."""
        from fastbreak.teams import get_team_playtypes

        client = _make_synergy_client(mocker)

        with pytest.warns(UserWarning, match="restricted"):
            await get_team_playtypes(client, team_id=1610612754)

    async def test_still_returns_list(self, mocker: MockerFixture):
        """get_team_playtypes still returns a list despite the warning."""
        from fastbreak.teams import get_team_playtypes

        client = _make_synergy_client(mocker)

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = await get_team_playtypes(client, team_id=1610612754)

        assert isinstance(result, list)
