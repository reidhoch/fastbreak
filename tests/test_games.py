import pytest
from pytest_mock import MockerFixture

from fastbreak.clients.nba import NBAClient
from fastbreak.games import (
    get_box_scores,
    get_game_ids,
    get_game_summary,
    get_games_on_date,
    get_play_by_play,
    get_todays_games,
)


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


def _make_scoreboard_client(mocker: MockerFixture, games: list):
    """Return a NBAClient whose .get() resolves to a mock ScoreboardV3Response."""
    scoreboard = mocker.MagicMock()
    scoreboard.games = games
    response = mocker.MagicMock()
    response.scoreboard = scoreboard
    client = NBAClient(session=mocker.MagicMock())
    client.get = mocker.AsyncMock(return_value=response)
    return client


class TestGetGamesOnDate:
    """Tests for get_games_on_date standalone function."""

    async def test_returns_games_for_date(self, mocker: MockerFixture):
        """get_games_on_date returns the list of games from the scoreboard."""
        game = mocker.MagicMock()
        client = _make_scoreboard_client(mocker, [game])

        result = await get_games_on_date(client, "2025-01-15")

        assert result == [game]

    async def test_returns_empty_list_when_no_games(self, mocker: MockerFixture):
        """get_games_on_date returns [] when no games are scheduled."""
        client = _make_scoreboard_client(mocker, [])

        result = await get_games_on_date(client, "2025-07-04")

        assert result == []

    async def test_returns_empty_list_when_scoreboard_is_none(
        self, mocker: MockerFixture
    ):
        """get_games_on_date returns [] when the API returns no scoreboard."""
        response = mocker.MagicMock()
        response.scoreboard = None
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        result = await get_games_on_date(client, "2025-07-04")

        assert result == []

    async def test_passes_date_to_endpoint(self, mocker: MockerFixture):
        """get_games_on_date passes the date string to ScoreboardV3."""
        client = _make_scoreboard_client(mocker, [])

        await get_games_on_date(client, "2025-01-15")

        endpoint = client.get.call_args[0][0]
        assert endpoint.game_date == "2025-01-15"

    async def test_returns_multiple_games(self, mocker: MockerFixture):
        """get_games_on_date returns all games on a busy night."""
        games = [mocker.MagicMock() for _ in range(10)]
        client = _make_scoreboard_client(mocker, games)

        result = await get_games_on_date(client, "2025-01-07")

        assert len(result) == 10


class TestGetTodaysGames:
    """Tests for get_todays_games convenience function."""

    async def test_returns_todays_games(self, mocker: MockerFixture):
        """get_todays_games returns games from today's scoreboard."""
        game = mocker.MagicMock()
        client = _make_scoreboard_client(mocker, [game])
        mock_date = mocker.patch("fastbreak.games.date")
        mock_date.today.return_value.isoformat.return_value = "2025-02-25"

        result = await get_todays_games(client)

        assert result == [game]

    async def test_passes_todays_date_to_endpoint(self, mocker: MockerFixture):
        """get_todays_games uses today's date in YYYY-MM-DD format."""
        client = _make_scoreboard_client(mocker, [])
        mock_date = mocker.patch("fastbreak.games.date")
        mock_date.today.return_value.isoformat.return_value = "2025-02-25"

        await get_todays_games(client)

        endpoint = client.get.call_args[0][0]
        assert endpoint.game_date == "2025-02-25"


def _make_summary_client(mocker: MockerFixture, summary):
    """Return a NBAClient whose .get() resolves to a mock BoxScoreSummaryResponse."""
    response = mocker.MagicMock()
    response.boxScoreSummary = summary
    client = NBAClient(session=mocker.MagicMock())
    client.get = mocker.AsyncMock(return_value=response)
    return client


class TestGetGameSummary:
    """Tests for get_game_summary standalone function."""

    async def test_returns_summary_for_game(self, mocker: MockerFixture):
        """get_game_summary returns the boxScoreSummary from the response."""
        summary = mocker.MagicMock()
        client = _make_summary_client(mocker, summary)

        result = await get_game_summary(client, "0022400001")

        assert result == summary

    async def test_passes_game_id_to_endpoint(self, mocker: MockerFixture):
        """get_game_summary passes the game_id to BoxScoreSummary."""
        client = _make_summary_client(mocker, mocker.MagicMock())

        await get_game_summary(client, "0022400001")

        endpoint = client.get.call_args[0][0]
        assert endpoint.game_id == "0022400001"


def _make_batch_client(mocker: MockerFixture, box_scores: dict):
    """Return a NBAClient whose .get_many() resolves to mock responses in order."""
    game_ids = list(box_scores.keys())
    responses = []
    for gid in game_ids:
        resp = mocker.MagicMock()
        resp.boxScoreTraditional = box_scores[gid]
        responses.append(resp)
    client = NBAClient(session=mocker.MagicMock())
    client.get_many = mocker.AsyncMock(return_value=responses)
    return client, game_ids


class TestGetBoxScores:
    """Tests for get_box_scores batch utility."""

    async def test_returns_dict_mapping_game_id_to_box_score(
        self, mocker: MockerFixture
    ):
        """get_box_scores returns a dict of game_id -> box score data."""
        bs1, bs2 = mocker.MagicMock(), mocker.MagicMock()
        client, game_ids = _make_batch_client(
            mocker, {"0022400001": bs1, "0022400002": bs2}
        )

        result = await get_box_scores(client, game_ids)

        assert result == {"0022400001": bs1, "0022400002": bs2}

    async def test_returns_empty_dict_for_no_game_ids(self, mocker: MockerFixture):
        """get_box_scores returns {} when given an empty list."""
        client = NBAClient(session=mocker.MagicMock())
        client.get_many = mocker.AsyncMock(return_value=[])

        result = await get_box_scores(client, [])

        assert result == {}

    async def test_calls_get_many_with_box_score_endpoints(self, mocker: MockerFixture):
        """get_box_scores passes BoxScoreTraditional endpoints to get_many."""
        client, game_ids = _make_batch_client(
            mocker, {"0022400001": mocker.MagicMock()}
        )

        await get_box_scores(client, game_ids)

        endpoints = client.get_many.call_args[0][0]
        assert len(endpoints) == 1
        assert endpoints[0].game_id == "0022400001"

    async def test_handles_single_game(self, mocker: MockerFixture):
        """get_box_scores works correctly for a single game ID."""
        bs = mocker.MagicMock()
        client, game_ids = _make_batch_client(mocker, {"0022400001": bs})

        result = await get_box_scores(client, game_ids)

        assert result == {"0022400001": bs}


def _make_pbp_client(mocker: MockerFixture, actions: list):
    """Return a NBAClient whose .get() resolves to a mock PlayByPlayResponse."""
    game = mocker.MagicMock()
    game.actions = actions
    response = mocker.MagicMock()
    response.game = game
    client = NBAClient(session=mocker.MagicMock())
    client.get = mocker.AsyncMock(return_value=response)
    return client


class TestGetPlayByPlay:
    """Tests for get_play_by_play standalone function."""

    async def test_returns_list_of_actions(self, mocker: MockerFixture):
        """get_play_by_play returns the list of play actions."""
        action = mocker.MagicMock()
        client = _make_pbp_client(mocker, [action])

        result = await get_play_by_play(client, "0022400001")

        assert result == [action]

    async def test_returns_empty_list_when_no_actions(self, mocker: MockerFixture):
        """get_play_by_play returns [] when no actions exist."""
        client = _make_pbp_client(mocker, [])

        result = await get_play_by_play(client, "0022400001")

        assert result == []

    async def test_passes_game_id_to_endpoint(self, mocker: MockerFixture):
        """get_play_by_play passes game_id to PlayByPlay."""
        client = _make_pbp_client(mocker, [])

        await get_play_by_play(client, "0022400001")

        endpoint = client.get.call_args[0][0]
        assert endpoint.game_id == "0022400001"
