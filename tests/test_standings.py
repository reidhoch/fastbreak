"""Tests for fastbreak.standings utility functions."""

from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from fastbreak.clients.nba import NBAClient
from fastbreak.standings import magic_number


def _make_standings_client(mocker: MockerFixture, standings: list):
    """Return NBAClient whose .get() resolves to a mock LeagueStandingsResponse."""
    response = mocker.MagicMock()
    response.standings = standings
    client = NBAClient(session=mocker.MagicMock())
    client.get = mocker.AsyncMock(return_value=response)
    return client


def _make_standing(mocker: MockerFixture, conference: str, playoff_rank: int):
    """Return a minimal mock TeamStanding."""
    s = mocker.MagicMock()
    s.conference = conference
    s.playoff_rank = playoff_rank
    return s


class TestGetStandings:
    """Tests for get_standings()."""

    async def test_returns_all_standings(self, mocker: MockerFixture):
        """get_standings returns all TeamStanding entries from the response."""
        from fastbreak.standings import get_standings

        entries = [mocker.MagicMock(), mocker.MagicMock()]
        client = _make_standings_client(mocker, entries)

        result = await get_standings(client)

        assert result == entries

    async def test_passes_season_to_endpoint(self, mocker: MockerFixture):
        """get_standings passes season to LeagueStandings endpoint."""
        from fastbreak.standings import get_standings

        client = _make_standings_client(mocker, [])

        await get_standings(client, season="2023-24")

        endpoint = client.get.call_args[0][0]
        assert endpoint.season == "2023-24"

    async def test_passes_season_type_to_endpoint(self, mocker: MockerFixture):
        """get_standings passes season_type to LeagueStandings endpoint."""
        from fastbreak.standings import get_standings

        client = _make_standings_client(mocker, [])

        await get_standings(client, season_type="Playoffs")

        endpoint = client.get.call_args[0][0]
        assert endpoint.season_type == "Playoffs"

    async def test_defaults_season_type_to_regular_season(self, mocker: MockerFixture):
        """get_standings defaults season_type to 'Regular Season'."""
        from fastbreak.standings import get_standings

        client = _make_standings_client(mocker, [])

        await get_standings(client)

        endpoint = client.get.call_args[0][0]
        assert endpoint.season_type == "Regular Season"


class TestGetConferenceStandings:
    """Tests for get_conference_standings()."""

    async def test_filters_to_east(self, mocker: MockerFixture):
        """get_conference_standings returns only East teams when conference='East'."""
        from fastbreak.standings import get_conference_standings

        east1 = _make_standing(mocker, "East", 1)
        east2 = _make_standing(mocker, "East", 2)
        west1 = _make_standing(mocker, "West", 1)
        client = _make_standings_client(mocker, [east1, west1, east2])

        result = await get_conference_standings(client, conference="East")

        assert all(s.conference == "East" for s in result)
        assert len(result) == 2

    async def test_filters_to_west(self, mocker: MockerFixture):
        """get_conference_standings returns only West teams when conference='West'."""
        from fastbreak.standings import get_conference_standings

        east1 = _make_standing(mocker, "East", 1)
        west1 = _make_standing(mocker, "West", 1)
        west2 = _make_standing(mocker, "West", 2)
        client = _make_standings_client(mocker, [east1, west1, west2])

        result = await get_conference_standings(client, conference="West")

        assert all(s.conference == "West" for s in result)
        assert len(result) == 2

    async def test_sorted_by_playoff_rank(self, mocker: MockerFixture):
        """get_conference_standings returns teams sorted by playoff_rank ascending."""
        from fastbreak.standings import get_conference_standings

        s3 = _make_standing(mocker, "East", 3)
        s1 = _make_standing(mocker, "East", 1)
        s2 = _make_standing(mocker, "East", 2)
        client = _make_standings_client(mocker, [s3, s1, s2])

        result = await get_conference_standings(client, conference="East")

        assert [s.playoff_rank for s in result] == [1, 2, 3]

    async def test_returns_empty_for_unknown_conference(self, mocker: MockerFixture):
        """get_conference_standings returns [] when no teams match."""
        from fastbreak.standings import get_conference_standings

        client = _make_standings_client(mocker, [_make_standing(mocker, "East", 1)])

        result = await get_conference_standings(client, conference="West")

        assert result == []

    async def test_forwards_season_to_endpoint(self, mocker: MockerFixture):
        """get_conference_standings passes season through to LeagueStandings."""
        from fastbreak.standings import get_conference_standings

        client = _make_standings_client(mocker, [])

        await get_conference_standings(client, conference="East", season="2023-24")

        endpoint = client.get.call_args[0][0]
        assert endpoint.season == "2023-24"

    async def test_forwards_season_type_to_endpoint(self, mocker: MockerFixture):
        """get_conference_standings passes season_type through to LeagueStandings."""
        from fastbreak.standings import get_conference_standings

        client = _make_standings_client(mocker, [])

        await get_conference_standings(
            client, conference="East", season_type="Playoffs"
        )

        endpoint = client.get.call_args[0][0]
        assert endpoint.season_type == "Playoffs"


class TestMagicNumber:
    """Tests for magic_number() — wins+losses needed to clinch a playoff spot."""

    def test_typical_mid_season_lead(self) -> None:
        """Leading team with 50W, opponent at 48W with 15 games left."""
        # max(0, 1 + 15 + 48 - 50) = 14
        result = magic_number(my_wins=50, opp_wins=48, opp_games_remaining=15)
        assert result == 14

    def test_already_clinched_returns_zero(self) -> None:
        """Returns 0 when opponent can no longer catch the leading team."""
        # Opponent has 59W but 0 games left; leader has 60W.
        # max(0, 1 + 0 + 59 - 60) = 0
        result = magic_number(my_wins=60, opp_wins=59, opp_games_remaining=0)
        assert result == 0

    def test_large_lead_with_no_games_remaining(self) -> None:
        """Opponent has no games left and is far behind — already clinched."""
        result = magic_number(my_wins=55, opp_wins=40, opp_games_remaining=0)
        assert result == 0

    def test_m1_means_any_result_clinches(self) -> None:
        """M=1: one more win OR one opponent loss clinches."""
        # max(0, 1 + 1 + 49 - 50) = 1
        result = magic_number(my_wins=50, opp_wins=49, opp_games_remaining=1)
        assert result == 1

    def test_equal_record_opponent_has_games_left(self) -> None:
        """Tied teams: opponent has games remaining, magic number > 1."""
        # max(0, 1 + 10 + 50 - 50) = 11
        result = magic_number(my_wins=50, opp_wins=50, opp_games_remaining=10)
        assert result == 11

    def test_result_is_int(self) -> None:
        """Magic number is always a non-negative integer."""
        result = magic_number(my_wins=48, opp_wins=45, opp_games_remaining=20)
        assert isinstance(result, int)
        assert result >= 0
