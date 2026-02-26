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

    async def test_raises_for_zero_limit(self, mocker: MockerFixture):
        """search_players raises ValueError when limit=0."""
        client = _make_client(mocker)

        with pytest.raises(ValueError, match="positive integer"):
            await search_players(client, "Curry", limit=0)

        client.get.assert_not_called()

    async def test_raises_for_negative_limit(self, mocker: MockerFixture):
        """search_players raises ValueError when limit is negative."""
        client = _make_client(mocker)

        with pytest.raises(ValueError, match="positive integer"):
            await search_players(client, "Curry", limit=-5)

        client.get.assert_not_called()

    async def test_last_name_prefix_ranked_before_first_name_prefix(
        self, mocker: MockerFixture
    ):
        """Last-name prefix match (priority 1) ranks before first-name prefix (priority 2)."""
        # "james" matches LeBron James on last name (priority 1)
        # and James Brown on first name (priority 2)
        last_name_match = _make_player(mocker, 1, "LeBron", "James")
        first_name_match = _make_player(mocker, 2, "James", "Brown")
        # Provide in reverse expected order to confirm sorting, not insertion order
        client = _make_client(mocker, first_name_match, last_name_match)

        results = await search_players(client, "james")

        assert results[0].person_id == 1  # LeBron James (last-name prefix) first
        assert results[1].person_id == 2  # James Brown (first-name prefix) second

    async def test_exact_full_name_ranked_before_substring(self, mocker: MockerFixture):
        """Exact full-name match (priority 0) ranks before substring match (priority 3)."""
        # "james brown" exactly matches James Brown (priority 0)
        # and appears as substring in "james browning" (priority 3)
        exact_match = _make_player(mocker, 1, "James", "Brown")
        substring_match = _make_player(mocker, 2, "James", "Browning")
        client = _make_client(mocker, substring_match, exact_match)

        results = await search_players(client, "james brown")

        assert results[0].person_id == 1  # exact match first
        assert results[1].person_id == 2  # substring match second


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


from fastbreak.players import get_player_game_log


def _make_game_log_client(mocker: MockerFixture, games: list):
    """Return a NBAClient whose .get() resolves to a mock PlayerGameLogResponse."""
    response = mocker.MagicMock()
    response.games = games
    client = NBAClient(session=mocker.MagicMock())
    client.get = mocker.AsyncMock(return_value=response)
    return client


class TestGetPlayerGameLog:
    """Tests for get_player_game_log standalone function."""

    async def test_returns_game_log_entries(self, mocker: MockerFixture):
        """get_player_game_log returns the list of game log entries."""
        entry = mocker.MagicMock()
        client = _make_game_log_client(mocker, [entry])

        result = await get_player_game_log(client, player_id=201939)

        assert result == [entry]

    async def test_returns_empty_list_when_no_games(self, mocker: MockerFixture):
        """get_player_game_log returns [] when no games are found."""
        client = _make_game_log_client(mocker, [])

        result = await get_player_game_log(client, player_id=201939)

        assert result == []

    async def test_passes_player_id_to_endpoint(self, mocker: MockerFixture):
        """get_player_game_log passes player_id to PlayerGameLog."""
        client = _make_game_log_client(mocker, [])

        await get_player_game_log(client, player_id=201939)

        endpoint = client.get.call_args[0][0]
        assert endpoint.player_id == 201939

    async def test_passes_season_to_endpoint(self, mocker: MockerFixture):
        """get_player_game_log passes season to PlayerGameLog."""
        client = _make_game_log_client(mocker, [])

        await get_player_game_log(client, player_id=201939, season="2023-24")

        endpoint = client.get.call_args[0][0]
        assert endpoint.season == "2023-24"

    async def test_passes_season_type_to_endpoint(self, mocker: MockerFixture):
        """get_player_game_log passes season_type to PlayerGameLog."""
        client = _make_game_log_client(mocker, [])

        await get_player_game_log(client, player_id=201939, season_type="Playoffs")

        endpoint = client.get.call_args[0][0]
        assert endpoint.season_type == "Playoffs"


from fastbreak.players import get_player_stats


def _make_career_client(mocker: MockerFixture, career_response):
    """Return a NBAClient whose .get() resolves to a mock PlayerCareerStatsResponse."""
    client = NBAClient(session=mocker.MagicMock())
    client.get = mocker.AsyncMock(return_value=career_response)
    return client


class TestGetPlayerStats:
    """Tests for get_player_stats standalone function."""

    async def test_returns_full_career_response(self, mocker: MockerFixture):
        """get_player_stats returns the entire PlayerCareerStatsResponse."""
        response = mocker.MagicMock()
        client = _make_career_client(mocker, response)

        result = await get_player_stats(client, player_id=201939)

        assert result is response

    async def test_passes_player_id_to_endpoint(self, mocker: MockerFixture):
        """get_player_stats passes player_id to PlayerCareerStats."""
        client = _make_career_client(mocker, mocker.MagicMock())

        await get_player_stats(client, player_id=201939)

        endpoint = client.get.call_args[0][0]
        assert endpoint.player_id == 201939

    async def test_default_per_mode_is_per_game(self, mocker: MockerFixture):
        """get_player_stats defaults to PerGame stats."""
        client = _make_career_client(mocker, mocker.MagicMock())

        await get_player_stats(client, player_id=201939)

        endpoint = client.get.call_args[0][0]
        assert endpoint.per_mode == "PerGame"

    async def test_passes_per_mode_to_endpoint(self, mocker: MockerFixture):
        """get_player_stats passes per_mode to PlayerCareerStats."""
        client = _make_career_client(mocker, mocker.MagicMock())

        await get_player_stats(client, player_id=201939, per_mode="Totals")

        endpoint = client.get.call_args[0][0]
        assert endpoint.per_mode == "Totals"


from fastbreak.players import get_league_leaders


def _make_leaders_client(mocker: MockerFixture, leaders: list):
    """Return a NBAClient whose .get() resolves to a mock LeagueLeadersResponse."""
    response = mocker.MagicMock()
    response.leaders = leaders
    client = NBAClient(session=mocker.MagicMock())
    client.get = mocker.AsyncMock(return_value=response)
    return client


class TestGetLeagueLeaders:
    """Tests for get_league_leaders standalone function."""

    async def test_returns_list_of_leaders(self, mocker: MockerFixture):
        """get_league_leaders returns the full list of leaders."""
        leader = mocker.MagicMock()
        client = _make_leaders_client(mocker, [leader])

        result = await get_league_leaders(client)

        assert result == [leader]

    async def test_returns_empty_list_when_no_leaders(self, mocker: MockerFixture):
        """get_league_leaders returns [] when no leaders returned."""
        client = _make_leaders_client(mocker, [])

        result = await get_league_leaders(client)

        assert result == []

    async def test_default_stat_category_is_pts(self, mocker: MockerFixture):
        """get_league_leaders defaults to PTS category."""
        client = _make_leaders_client(mocker, [])

        await get_league_leaders(client)

        endpoint = client.get.call_args[0][0]
        assert endpoint.stat_category == "PTS"

    async def test_passes_stat_category_to_endpoint(self, mocker: MockerFixture):
        """get_league_leaders passes stat_category to LeagueLeaders."""
        client = _make_leaders_client(mocker, [])

        await get_league_leaders(client, stat_category="AST")

        endpoint = client.get.call_args[0][0]
        assert endpoint.stat_category == "AST"

    async def test_passes_season_to_endpoint(self, mocker: MockerFixture):
        """get_league_leaders passes season to LeagueLeaders."""
        client = _make_leaders_client(mocker, [])

        await get_league_leaders(client, season="2023-24")

        endpoint = client.get.call_args[0][0]
        assert endpoint.season == "2023-24"

    async def test_limit_truncates_results(self, mocker: MockerFixture):
        """get_league_leaders returns at most limit results."""
        leaders = [mocker.MagicMock() for _ in range(10)]
        client = _make_leaders_client(mocker, leaders)

        result = await get_league_leaders(client, limit=3)

        assert len(result) == 3
        assert result == leaders[:3]

    async def test_no_limit_returns_all(self, mocker: MockerFixture):
        """get_league_leaders returns all results when limit is None."""
        leaders = [mocker.MagicMock() for _ in range(10)]
        client = _make_leaders_client(mocker, leaders)

        result = await get_league_leaders(client)

        assert len(result) == 10

    async def test_raises_for_zero_limit(self, mocker: MockerFixture):
        """get_league_leaders raises ValueError when limit=0."""
        client = _make_leaders_client(mocker, [])

        with pytest.raises(ValueError, match="positive integer"):
            await get_league_leaders(client, limit=0)

    async def test_raises_for_negative_limit(self, mocker: MockerFixture):
        """get_league_leaders raises ValueError when limit is negative."""
        client = _make_leaders_client(mocker, [])

        with pytest.raises(ValueError, match="positive integer"):
            await get_league_leaders(client, limit=-1)

    async def test_raises_before_api_call(self, mocker: MockerFixture):
        """get_league_leaders raises ValueError without calling the API."""
        client = _make_leaders_client(mocker, [])

        with pytest.raises(ValueError, match="positive integer"):
            await get_league_leaders(client, limit=0)

        client.get.assert_not_called()


from fastbreak.players import get_hustle_stats


def _make_hustle_client(mocker: MockerFixture, players: list):
    """Return a NBAClient whose .get() resolves to a mock LeagueHustleStatsPlayerResponse."""
    response = mocker.MagicMock()
    response.players = players
    client = NBAClient(session=mocker.MagicMock())
    client.get = mocker.AsyncMock(return_value=response)
    return client


class TestGetHustleStats:
    """Tests for get_hustle_stats standalone function."""

    async def test_returns_matching_player(self, mocker: MockerFixture):
        """get_hustle_stats returns the hustle stats for the given player."""
        player = mocker.MagicMock()
        player.player_id = 201939
        client = _make_hustle_client(mocker, [player])

        result = await get_hustle_stats(client, player_id=201939)

        assert result is player

    async def test_returns_none_when_player_not_found(self, mocker: MockerFixture):
        """get_hustle_stats returns None when the player is not in the results."""
        player = mocker.MagicMock()
        player.player_id = 999
        client = _make_hustle_client(mocker, [player])

        result = await get_hustle_stats(client, player_id=201939)

        assert result is None

    async def test_returns_none_when_no_players(self, mocker: MockerFixture):
        """get_hustle_stats returns None for an empty response."""
        client = _make_hustle_client(mocker, [])

        result = await get_hustle_stats(client, player_id=201939)

        assert result is None

    async def test_passes_season_type_to_endpoint(self, mocker: MockerFixture):
        """get_hustle_stats passes season_type to LeagueHustleStatsPlayer."""
        client = _make_hustle_client(mocker, [])

        await get_hustle_stats(client, player_id=201939, season_type="Playoffs")

        endpoint = client.get.call_args[0][0]
        assert endpoint.season_type == "Playoffs"

    async def test_passes_season_to_endpoint(self, mocker: MockerFixture):
        """get_hustle_stats passes season to LeagueHustleStatsPlayer."""
        client = _make_hustle_client(mocker, [])

        await get_hustle_stats(client, player_id=201939, season="2023-24")

        endpoint = client.get.call_args[0][0]
        assert endpoint.season == "2023-24"
