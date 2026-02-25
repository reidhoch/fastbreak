import pytest
from pytest_mock import MockerFixture

from fastbreak.clients.nba import NBAClient
from fastbreak.games import get_game_ids


def _make_client(mocker: MockerFixture, game_entries: list[dict]):
    """Return a NBAClient whose .get() resolves to a mock LeagueGameLogResponse."""
    entry_mocks = [mocker.MagicMock(**e) for e in game_entries]
    response = mocker.MagicMock()
    response.games = entry_mocks
    client = NBAClient(session=mocker.MagicMock())
    client.get = mocker.AsyncMock(return_value=response)
    return client


class TestGetGameIds:
    """Tests for the get_game_ids standalone function."""

    async def test_deduplicates_game_ids(self, mocker: MockerFixture):
        """get_game_ids returns each game ID once even though each game has two team rows."""
        # LeagueGameLog returns one row per team — two rows per game
        client = _make_client(
            mocker,
            [
                {"game_id": "0022400001"},
                {"game_id": "0022400001"},  # same game, other team
                {"game_id": "0022400002"},
                {"game_id": "0022400002"},
            ],
        )

        result = await get_game_ids(client)

        assert result == ["0022400001", "0022400002"]

    async def test_returns_sorted_game_ids(self, mocker: MockerFixture):
        """get_game_ids returns game IDs in ascending (chronological) order."""
        client = _make_client(
            mocker,
            [
                {"game_id": "0022400003"},
                {"game_id": "0022400003"},
                {"game_id": "0022400001"},
                {"game_id": "0022400001"},
                {"game_id": "0022400002"},
                {"game_id": "0022400002"},
            ],
        )

        result = await get_game_ids(client)

        assert result == ["0022400001", "0022400002", "0022400003"]

    async def test_returns_empty_list_when_no_games(self, mocker: MockerFixture):
        """get_game_ids returns [] when the log has no entries."""
        client = _make_client(mocker, [])

        result = await get_game_ids(client)

        assert result == []

    async def test_passes_season_to_endpoint(self, mocker: MockerFixture):
        """get_game_ids passes the given season to LeagueGameLog."""
        client = _make_client(mocker, [])

        await get_game_ids(client, season="2023-24")

        call_args = client.get.call_args
        endpoint = call_args[0][0]
        assert endpoint.season == "2023-24"

    async def test_passes_season_type_to_endpoint(self, mocker: MockerFixture):
        """get_game_ids passes season_type to LeagueGameLog."""
        client = _make_client(mocker, [])

        await get_game_ids(client, season_type="Playoffs")

        endpoint = client.get.call_args[0][0]
        assert endpoint.season_type == "Playoffs"

    async def test_passes_date_range_to_endpoint(self, mocker: MockerFixture):
        """get_game_ids passes date_from and date_to to LeagueGameLog."""
        client = _make_client(mocker, [])

        await get_game_ids(client, date_from="01/01/2025", date_to="01/31/2025")

        endpoint = client.get.call_args[0][0]
        assert endpoint.date_from == "01/01/2025"
        assert endpoint.date_to == "01/31/2025"

    async def test_passes_team_id_to_endpoint(self, mocker: MockerFixture):
        """get_game_ids passes team_id to LeagueGameLog for team-specific filtering."""
        client = _make_client(mocker, [])

        await get_game_ids(client, team_id=1610612744)

        endpoint = client.get.call_args[0][0]
        assert endpoint.team_id == 1610612744

    async def test_team_id_omitted_by_default(self, mocker: MockerFixture):
        """get_game_ids passes no team filter when team_id is not provided."""
        client = _make_client(mocker, [])

        await get_game_ids(client)

        endpoint = client.get.call_args[0][0]
        assert endpoint.team_id is None

    async def test_filters_game_ids_by_team_id_client_side(self, mocker: MockerFixture):
        """get_game_ids filters entries by team_id client-side (API ignores TeamID param)."""
        # API returns all teams' rows — game 3 doesn't involve team 1
        client = _make_client(
            mocker,
            [
                {"game_id": "0022400001", "team_id": 1},
                {"game_id": "0022400001", "team_id": 2},  # other team, same game
                {"game_id": "0022400002", "team_id": 1},
                {"game_id": "0022400002", "team_id": 3},  # other team, same game
                {"game_id": "0022400003", "team_id": 2},  # team 1 not in this game
                {"game_id": "0022400003", "team_id": 3},  # team 1 not in this game
            ],
        )

        result = await get_game_ids(client, team_id=1)

        assert result == ["0022400001", "0022400002"]
