import pytest
from pytest_mock import MockerFixture

from fastbreak.clients.nba import NBAClient
from fastbreak.players import get_player, get_player_id, search_players


def _make_player(mocker: MockerFixture, person_id: int, first: str, last: str):
    return mocker.MagicMock(
        person_id=person_id,
        player_first_name=first,
        player_last_name=last,
    )


def _make_client(mocker: MockerFixture, *players):
    """Return a NBAClient whose .get() resolves to a mock player index."""
    response = mocker.MagicMock()
    response.players = list(players)
    client = NBAClient(session=mocker.MagicMock())
    client.get = mocker.AsyncMock(return_value=response)
    return client


class TestSearchPlayers:
    """Tests for the search_players standalone function."""

    async def test_finds_players_by_partial_last_name(self, mocker: MockerFixture):
        """search_players returns players matching a partial last name."""
        client = _make_client(
            mocker,
            _make_player(mocker, 201939, "Stephen", "Curry"),
            _make_player(mocker, 1628384, "Seth", "Curry"),
        )

        results = await search_players(client, "Curry")

        assert len(results) == 2

    async def test_empty_query_returns_empty_list(self, mocker: MockerFixture):
        """search_players returns [] for an empty query without hitting the API."""
        client = _make_client(mocker)

        results = await search_players(client, "")

        assert results == []
        client.get.assert_not_called()

    async def test_respects_limit_parameter(self, mocker: MockerFixture):
        """search_players returns at most `limit` results."""
        players = [_make_player(mocker, i, "Test", f"Player{i}") for i in range(10)]
        client = _make_client(mocker, *players)

        results = await search_players(client, "Test", limit=3)

        assert len(results) == 3

    async def test_returns_empty_for_no_match(self, mocker: MockerFixture):
        """search_players returns [] when no player matches the query."""
        client = _make_client(mocker, _make_player(mocker, 1, "LeBron", "James"))

        results = await search_players(client, "zzznomatch")

        assert results == []


class TestGetPlayer:
    """Tests for the get_player standalone function."""

    async def test_finds_player_by_integer_id(self, mocker: MockerFixture):
        """get_player returns the matching player when given a numeric ID."""
        player = _make_player(mocker, 201939, "Stephen", "Curry")
        client = _make_client(mocker, player)

        result = await get_player(client, 201939)

        assert result is not None
        assert result.person_id == 201939

    async def test_finds_player_by_exact_full_name(self, mocker: MockerFixture):
        """get_player returns the matching player when given an exact full name."""
        player = _make_player(mocker, 201939, "Stephen", "Curry")
        client = _make_client(mocker, player)

        result = await get_player(client, "Stephen Curry")

        assert result is not None
        assert result.person_id == 201939

    async def test_name_match_is_case_insensitive(self, mocker: MockerFixture):
        """get_player matches names regardless of case."""
        player = _make_player(mocker, 201939, "Stephen", "Curry")
        client = _make_client(mocker, player)

        result = await get_player(client, "stephen curry")

        assert result is not None

    async def test_returns_none_when_id_not_found(self, mocker: MockerFixture):
        """get_player returns None when no player has the given ID."""
        client = _make_client(mocker)

        result = await get_player(client, 99999999)

        assert result is None

    async def test_returns_none_when_name_not_found(self, mocker: MockerFixture):
        """get_player returns None when no player matches the given name."""
        client = _make_client(mocker, _make_player(mocker, 1, "LeBron", "James"))

        result = await get_player(client, "Nonexistent Player")

        assert result is None


class TestGetPlayerId:
    """Tests for the get_player_id standalone function."""

    async def test_returns_player_id_for_known_name(self, mocker: MockerFixture):
        """get_player_id returns the numeric ID for a matching player."""
        player = _make_player(mocker, 201939, "Stephen", "Curry")
        client = _make_client(mocker, player)

        result = await get_player_id(client, "Stephen Curry")

        assert result == 201939

    async def test_returns_none_when_not_found(self, mocker: MockerFixture):
        """get_player_id returns None when the player doesn't exist."""
        client = _make_client(mocker)

        result = await get_player_id(client, "Nonexistent Player")

        assert result is None
