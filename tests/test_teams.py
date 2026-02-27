"""Tests for fastbreak.teams utility functions."""

from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from fastbreak.clients.nba import NBAClient
from fastbreak.teams import (
    TEAMS,
    TeamID,
    TeamInfo,
    get_league_averages,
    get_lineup_net_ratings,
    get_lineup_stats,
    get_team,
    get_team_game_log,
    get_team_id,
    get_team_stats,
    search_teams,
    teams_by_conference,
    teams_by_division,
)


class TestSearchTeams:
    """Tests for search_teams synchronous utility."""

    def test_finds_team_by_exact_abbreviation(self):
        """search_teams returns a match for an exact abbreviation."""
        results = search_teams("IND")
        assert len(results) >= 1
        assert results[0].abbreviation == "IND"

    def test_finds_team_by_partial_city(self):
        """search_teams returns matches for a partial city name."""
        results = search_teams("Indiana")
        assert any(t.abbreviation == "IND" for t in results)

    def test_finds_team_by_partial_name(self):
        """search_teams returns matches for a partial team name."""
        results = search_teams("Pacer")
        assert any(t.abbreviation == "IND" for t in results)

    def test_returns_list_of_team_info(self):
        """search_teams returns a list of TeamInfo objects."""
        results = search_teams("Lakers")
        assert all(isinstance(t, TeamInfo) for t in results)

    def test_empty_query_returns_empty_list(self):
        """search_teams returns [] for an empty query."""
        assert search_teams("") == []

    def test_whitespace_query_returns_empty_list(self):
        """search_teams returns [] for a whitespace-only query."""
        assert search_teams("   ") == []

    def test_no_match_returns_empty_list(self):
        """search_teams returns [] when nothing matches."""
        assert search_teams("zzznomatch") == []

    def test_respects_limit_parameter(self):
        """search_teams returns at most `limit` results."""
        results = search_teams("a", limit=2)
        assert len(results) <= 2

    def test_case_insensitive_abbreviation(self):
        """search_teams matches abbreviations case-insensitively."""
        assert search_teams("ind") == search_teams("IND")

    def test_case_insensitive_name(self):
        """search_teams matches team names case-insensitively."""
        lower = search_teams("lakers")
        upper = search_teams("Lakers")
        assert lower == upper

    def test_abbreviation_match_ranks_first(self):
        """Exact abbreviation match is returned as the first result."""
        results = search_teams("LAL")
        assert results[0].abbreviation == "LAL"

    def test_raises_for_zero_limit(self):
        """search_teams raises ValueError when limit=0."""
        with pytest.raises(ValueError, match="positive integer"):
            search_teams("Lakers", limit=0)

    def test_raises_for_negative_limit(self):
        """search_teams raises ValueError when limit is negative."""
        with pytest.raises(ValueError, match="positive integer"):
            search_teams("Lakers", limit=-1)

    def test_same_priority_sorted_alphabetically_by_abbreviation(self):
        """Teams at the same priority rank alphabetically by abbreviation."""
        # "LA" matches both LAC (Clippers) and LAL (Lakers) as abbreviation prefix
        results = search_teams("LA", limit=10)
        la_abbrs = [t.abbreviation for t in results if t.abbreviation in ("LAC", "LAL")]
        assert la_abbrs == ["LAC", "LAL"]  # LAC before LAL alphabetically


def _make_team_game_log_client(mocker: MockerFixture, games: list):
    """Return a NBAClient whose .get() resolves to a mock TeamGameLogResponse."""
    response = mocker.MagicMock()
    response.games = games
    client = NBAClient(session=mocker.MagicMock())
    client.get = mocker.AsyncMock(return_value=response)
    return client


class TestGetTeamGameLog:
    """Tests for get_team_game_log standalone function."""

    async def test_returns_game_log_entries(self, mocker: MockerFixture):
        """get_team_game_log returns the list of game log entries."""
        entry = mocker.MagicMock()
        client = _make_team_game_log_client(mocker, [entry])

        result = await get_team_game_log(client, team_id=1610612754)

        assert result == [entry]

    async def test_returns_empty_list_when_no_games(self, mocker: MockerFixture):
        """get_team_game_log returns [] when no games are found."""
        client = _make_team_game_log_client(mocker, [])

        result = await get_team_game_log(client, team_id=1610612754)

        assert result == []

    async def test_passes_team_id_to_endpoint(self, mocker: MockerFixture):
        """get_team_game_log passes team_id to TeamGameLog."""
        client = _make_team_game_log_client(mocker, [])

        await get_team_game_log(client, team_id=1610612754)

        endpoint = client.get.call_args[0][0]
        assert endpoint.team_id == 1610612754

    async def test_passes_season_to_endpoint(self, mocker: MockerFixture):
        """get_team_game_log passes season to TeamGameLog."""
        client = _make_team_game_log_client(mocker, [])

        await get_team_game_log(client, team_id=1610612754, season="2023-24")

        endpoint = client.get.call_args[0][0]
        assert endpoint.season == "2023-24"

    async def test_passes_season_type_to_endpoint(self, mocker: MockerFixture):
        """get_team_game_log passes season_type to TeamGameLog."""
        client = _make_team_game_log_client(mocker, [])

        await get_team_game_log(client, team_id=1610612754, season_type="Playoffs")

        endpoint = client.get.call_args[0][0]
        assert endpoint.season_type == "Playoffs"


def _make_team_stats_client(mocker: MockerFixture, teams: list):
    """Return a NBAClient whose .get() resolves to a mock LeagueDashTeamStatsResponse."""
    response = mocker.MagicMock()
    response.teams = teams
    client = NBAClient(session=mocker.MagicMock())
    client.get = mocker.AsyncMock(return_value=response)
    return client


class TestGetTeamStats:
    """Tests for get_team_stats standalone function."""

    async def test_returns_list_of_team_stats(self, mocker: MockerFixture):
        """get_team_stats returns the list of team stats rows."""
        row = mocker.MagicMock()
        client = _make_team_stats_client(mocker, [row])

        result = await get_team_stats(client)

        assert result == [row]

    async def test_returns_empty_list_when_no_teams(self, mocker: MockerFixture):
        """get_team_stats returns [] when no teams are returned."""
        client = _make_team_stats_client(mocker, [])

        result = await get_team_stats(client)

        assert result == []

    async def test_passes_season_to_endpoint(self, mocker: MockerFixture):
        """get_team_stats passes season to LeagueDashTeamStats."""
        client = _make_team_stats_client(mocker, [])

        await get_team_stats(client, season="2023-24")

        endpoint = client.get.call_args[0][0]
        assert endpoint.season == "2023-24"

    async def test_default_per_mode_is_per_game(self, mocker: MockerFixture):
        """get_team_stats defaults to PerGame."""
        client = _make_team_stats_client(mocker, [])

        await get_team_stats(client)

        endpoint = client.get.call_args[0][0]
        assert endpoint.per_mode == "PerGame"

    async def test_passes_per_mode_to_endpoint(self, mocker: MockerFixture):
        """get_team_stats passes per_mode to LeagueDashTeamStats."""
        client = _make_team_stats_client(mocker, [])

        await get_team_stats(client, per_mode="Totals")

        endpoint = client.get.call_args[0][0]
        assert endpoint.per_mode == "Totals"

    async def test_passes_season_type_to_endpoint(self, mocker: MockerFixture):
        """get_team_stats passes season_type to LeagueDashTeamStats."""
        client = _make_team_stats_client(mocker, [])

        await get_team_stats(client, season_type="Playoffs")

        endpoint = client.get.call_args[0][0]
        assert endpoint.season_type == "Playoffs"


def _make_lineup_client(mocker: MockerFixture, lineups: list):
    """Return a NBAClient whose .get() resolves to a mock TeamDashLineupsResponse."""
    response = mocker.MagicMock()
    response.lineups = lineups
    client = NBAClient(session=mocker.MagicMock())
    client.get = mocker.AsyncMock(return_value=response)
    return client


class TestGetLineupStats:
    """Tests for get_lineup_stats standalone function."""

    async def test_returns_list_of_lineup_stats(self, mocker: MockerFixture):
        """get_lineup_stats returns the list of lineup stats."""
        lineup = mocker.MagicMock()
        client = _make_lineup_client(mocker, [lineup])

        result = await get_lineup_stats(client, team_id=1610612754)

        assert result == [lineup]

    async def test_returns_empty_list_when_no_lineups(self, mocker: MockerFixture):
        """get_lineup_stats returns [] when no lineups returned."""
        client = _make_lineup_client(mocker, [])

        result = await get_lineup_stats(client, team_id=1610612754)

        assert result == []

    async def test_passes_team_id_to_endpoint(self, mocker: MockerFixture):
        """get_lineup_stats passes team_id to TeamDashLineups."""
        client = _make_lineup_client(mocker, [])

        await get_lineup_stats(client, team_id=1610612754)

        endpoint = client.get.call_args[0][0]
        assert endpoint.team_id == 1610612754

    async def test_default_group_quantity_is_5(self, mocker: MockerFixture):
        """get_lineup_stats defaults to 5-man lineups."""
        client = _make_lineup_client(mocker, [])

        await get_lineup_stats(client, team_id=1610612754)

        endpoint = client.get.call_args[0][0]
        assert endpoint.group_quantity == 5

    async def test_passes_group_quantity_to_endpoint(self, mocker: MockerFixture):
        """get_lineup_stats passes group_quantity to TeamDashLineups."""
        client = _make_lineup_client(mocker, [])

        await get_lineup_stats(client, team_id=1610612754, group_quantity=2)

        endpoint = client.get.call_args[0][0]
        assert endpoint.group_quantity == 2

    async def test_passes_season_to_endpoint(self, mocker: MockerFixture):
        """get_lineup_stats passes season to TeamDashLineups."""
        client = _make_lineup_client(mocker, [])

        await get_lineup_stats(client, team_id=1610612754, season="2023-24")

        endpoint = client.get.call_args[0][0]
        assert endpoint.season == "2023-24"


class TestTeamID:
    """Tests for TeamID enum."""

    def test_all_30_teams_exist(self) -> None:
        """All 30 NBA teams are defined."""
        assert len(TeamID) == 30

    def test_lakers_id(self) -> None:
        """Lakers have correct ID."""
        assert TeamID.LAKERS == 1610612747

    def test_celtics_id(self) -> None:
        """Celtics have correct ID."""
        assert TeamID.CELTICS == 1610612738

    def test_enum_is_int(self) -> None:
        """TeamID values can be used as integers."""
        assert int(TeamID.LAKERS) == 1610612747


class TestTeamsData:
    """Tests for TEAMS dictionary."""

    def test_all_30_teams_have_info(self) -> None:
        """All 30 teams have TeamInfo entries."""
        assert len(TEAMS) == 30

    def test_team_info_fields(self) -> None:
        """TeamInfo has all expected fields."""
        lakers = TEAMS[TeamID.LAKERS]
        assert lakers.id == TeamID.LAKERS
        assert lakers.abbreviation == "LAL"
        assert lakers.city == "Los Angeles"
        assert lakers.name == "Lakers"
        assert lakers.full_name == "Los Angeles Lakers"
        assert lakers.conference == "West"
        assert lakers.division == "Pacific"


class TestGetTeam:
    """Tests for get_team function."""

    def test_get_by_id(self) -> None:
        """Can get team by numeric ID."""
        team = get_team(1610612747)
        assert team is not None
        assert team.name == "Lakers"

    def test_get_by_abbreviation(self) -> None:
        """Can get team by abbreviation."""
        team = get_team("LAL")
        assert team is not None
        assert team.name == "Lakers"

    def test_get_by_abbreviation_lowercase(self) -> None:
        """Abbreviation lookup is case-insensitive."""
        team = get_team("lal")
        assert team is not None
        assert team.name == "Lakers"

    def test_get_by_name(self) -> None:
        """Can get team by name."""
        team = get_team("Lakers")
        assert team is not None
        assert team.abbreviation == "LAL"

    def test_get_by_name_lowercase(self) -> None:
        """Name lookup is case-insensitive."""
        team = get_team("lakers")
        assert team is not None
        assert team.abbreviation == "LAL"

    def test_get_by_city(self) -> None:
        """Can get team by city."""
        team = get_team("Boston")
        assert team is not None
        assert team.name == "Celtics"

    def test_get_unknown_returns_none(self) -> None:
        """Unknown identifier returns None."""
        assert get_team("Unknown") is None
        assert get_team(99999) is None

    def test_get_by_team_id_enum(self) -> None:
        """get_team accepts a TeamID enum value as the integer identifier."""
        team = get_team(TeamID.LAKERS)
        assert team is not None
        assert team.abbreviation == "LAL"


class TestGetTeamId:
    """Tests for get_team_id function."""

    def test_get_id_by_abbreviation(self) -> None:
        """Can get team ID by abbreviation."""
        assert get_team_id("LAL") == 1610612747

    def test_get_id_by_name(self) -> None:
        """Can get team ID by name."""
        assert get_team_id("Lakers") == 1610612747

    def test_get_id_by_city(self) -> None:
        """get_team_id returns the team ID when looking up by city name."""
        assert get_team_id("Boston") == TeamID.CELTICS

    def test_unknown_returns_none(self) -> None:
        """Unknown team returns None."""
        assert get_team_id("Unknown") is None


class TestTeamsByConference:
    """Tests for teams_by_conference function."""

    def test_east_has_15_teams(self) -> None:
        """Eastern Conference has 15 teams."""
        east = teams_by_conference("East")
        assert len(east) == 15

    def test_west_has_15_teams(self) -> None:
        """Western Conference has 15 teams."""
        west = teams_by_conference("West")
        assert len(west) == 15

    def test_case_insensitive(self) -> None:
        """Conference lookup is case-insensitive."""
        assert len(teams_by_conference("east")) == 15
        assert len(teams_by_conference("WEST")) == 15

    def test_celtics_in_east(self) -> None:
        """Celtics are in Eastern Conference."""
        east = teams_by_conference("East")
        team_names = [t.name for t in east]
        assert "Celtics" in team_names

    def test_lakers_in_west(self) -> None:
        """Lakers are in Western Conference."""
        west = teams_by_conference("West")
        team_names = [t.name for t in west]
        assert "Lakers" in team_names

    def test_raises_for_unknown_conference(self) -> None:
        """teams_by_conference raises ValueError for an unknown conference name."""
        with pytest.raises(ValueError, match="Unknown conference"):
            teams_by_conference("Northern")

    def test_raises_for_invalid_conference_name(self) -> None:
        """teams_by_conference raises ValueError for a plausible but wrong name."""
        with pytest.raises(ValueError, match="Unknown conference"):
            teams_by_conference("Eastern")


class TestTeamsByDivision:
    """Tests for teams_by_division function."""

    def test_atlantic_has_5_teams(self) -> None:
        """Atlantic Division has 5 teams."""
        atlantic = teams_by_division("Atlantic")
        assert len(atlantic) == 5

    def test_pacific_has_5_teams(self) -> None:
        """Pacific Division has 5 teams."""
        pacific = teams_by_division("Pacific")
        assert len(pacific) == 5

    def test_all_divisions_have_5_teams(self) -> None:
        """Each division has exactly 5 teams."""
        divisions = [
            "Atlantic",
            "Central",
            "Southeast",
            "Northwest",
            "Pacific",
            "Southwest",
        ]
        for division in divisions:
            teams = teams_by_division(division)
            assert len(teams) == 5, f"{division} should have 5 teams"

    def test_lakers_in_pacific(self) -> None:
        """Lakers are in Pacific Division."""
        pacific = teams_by_division("Pacific")
        team_names = [t.name for t in pacific]
        assert "Lakers" in team_names

    def test_raises_for_unknown_division(self) -> None:
        """teams_by_division raises ValueError for a division that no longer exists."""
        with pytest.raises(ValueError, match="Unknown division"):
            teams_by_division("Midwest")

    def test_raises_for_invalid_division_name(self) -> None:
        """teams_by_division raises ValueError for a plausible but wrong name."""
        with pytest.raises(ValueError, match="Unknown division"):
            teams_by_division("Northern")


def test_get_league_averages_exported():
    """get_league_averages is importable from teams."""
    from fastbreak.teams import get_league_averages  # noqa: PLC0415

    assert callable(get_league_averages)


def test_get_team_playtypes_exported():
    from fastbreak.teams import get_team_playtypes  # noqa: PLC0415

    assert callable(get_team_playtypes)


class TestLineupNetRating:
    def test_compute_lineup_net_rtg_basic(self):
        """Pure computation: net_rtg = plus_minus / minutes * 48."""
        from fastbreak.teams import _lineup_net_rtg  # noqa: PLC0415

        # 10 plus_minus, 100 minutes -> 10/100*48 = 4.8
        result = _lineup_net_rtg(plus_minus=10.0, minutes=100.0)
        assert abs(result - 4.8) < 0.001

    def test_compute_lineup_net_rtg_zero_minutes_returns_none(self):
        from fastbreak.teams import _lineup_net_rtg  # noqa: PLC0415

        assert _lineup_net_rtg(plus_minus=5.0, minutes=0.0) is None

    def test_get_lineup_net_ratings_exported(self):
        from fastbreak.teams import get_lineup_net_ratings  # noqa: PLC0415

        assert callable(get_lineup_net_ratings)


def _make_lineup_net_client(mocker: MockerFixture, lineups: list):
    """Return a NBAClient whose .get() resolves to a mock TeamDashLineupsResponse."""
    response = mocker.MagicMock()
    response.lineups = lineups
    client = NBAClient(session=mocker.MagicMock())
    client.get = mocker.AsyncMock(return_value=response)
    return client


class TestGetLineupNetRatings:
    """Tests for get_lineup_net_ratings standalone function."""

    def _make_lineup(self, mocker: MockerFixture, min: float, plus_minus: float):
        lineup = mocker.MagicMock()
        lineup.min = min
        lineup.plus_minus = plus_minus
        return lineup

    async def test_excludes_lineups_below_min_minutes(self, mocker: MockerFixture):
        """Lineups with minutes < min_minutes (default 10.0) are not returned."""
        lineup_ok = self._make_lineup(mocker, min=15.0, plus_minus=5.0)
        lineup_low = self._make_lineup(mocker, min=5.0, plus_minus=100.0)
        client = _make_lineup_net_client(mocker, [lineup_ok, lineup_low])

        result = await get_lineup_net_ratings(client, team_id=1610612747)

        assert len(result) == 1
        assert result[0][0] is lineup_ok

    async def test_results_sorted_descending_by_net_rating(self, mocker: MockerFixture):
        """Results are returned best-first (descending net rating)."""
        lineup_a = self._make_lineup(mocker, min=20.0, plus_minus=10.0)  # 24.0 net rtg
        lineup_b = self._make_lineup(mocker, min=20.0, plus_minus=5.0)  # 12.0 net rtg
        client = _make_lineup_net_client(
            mocker, [lineup_b, lineup_a]
        )  # b first in input

        result = await get_lineup_net_ratings(client, team_id=1610612747)

        assert result[0][0] is lineup_a  # higher net rating first
        assert result[1][0] is lineup_b

    async def test_custom_min_minutes_includes_more_lineups(
        self, mocker: MockerFixture
    ):
        """Setting min_minutes=0.0 includes lineups that would otherwise be filtered."""
        lineup = self._make_lineup(mocker, min=3.0, plus_minus=5.0)

        client_a = _make_lineup_net_client(mocker, [lineup])
        result_default = await get_lineup_net_ratings(client_a, team_id=1610612747)

        client_b = _make_lineup_net_client(mocker, [lineup])
        result_zero = await get_lineup_net_ratings(
            client_b, team_id=1610612747, min_minutes=0.0
        )

        assert result_default == []
        assert len(result_zero) == 1

    async def test_excludes_zero_minute_lineups_even_at_min_minutes_zero(
        self, mocker: MockerFixture
    ):
        """Lineups with minutes=0 are excluded because _lineup_net_rtg returns None."""
        lineup = self._make_lineup(mocker, min=0.0, plus_minus=5.0)
        client = _make_lineup_net_client(mocker, [lineup])

        result = await get_lineup_net_ratings(
            client, team_id=1610612747, min_minutes=0.0
        )

        assert result == []

    async def test_net_rating_value_is_correct(self, mocker: MockerFixture):
        """The computed net_rtg equals plus_minus / min * 48."""
        lineup = self._make_lineup(mocker, min=100.0, plus_minus=10.0)
        client = _make_lineup_net_client(mocker, [lineup])

        result = await get_lineup_net_ratings(client, team_id=1610612747)

        assert len(result) == 1
        assert abs(result[0][1] - 4.8) < 0.001  # 10 / 100 * 48


def _make_team_row(
    *,
    pts: float = 110.0,
    fga: float = 85.0,
    fta: float = 20.0,
    ftm: float = 16.0,
    oreb: float = 10.0,
    reb: float = 42.0,
    ast: float = 26.0,
    fgm: float = 38.0,
    fg3m: float = 12.0,
    tov: float = 14.0,
    pf: float = 20.0,
) -> MagicMock:
    row = MagicMock()
    row.pts = pts
    row.fga = fga
    row.fta = fta
    row.ftm = ftm
    row.oreb = oreb
    row.reb = reb
    row.ast = ast
    row.fgm = fgm
    row.fg3m = fg3m
    row.tov = tov
    row.pf = pf
    return row


class TestGetLeagueAverages:
    """Tests for get_league_averages standalone function."""

    async def test_raises_when_no_team_rows_returned(self, mocker: MockerFixture):
        """Raises ValueError when get_team_stats returns an empty list."""
        response = mocker.MagicMock()
        response.teams = []
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        with pytest.raises(ValueError, match="No team stats returned"):
            await get_league_averages(client)

    async def test_always_requests_per_game_mode(self, mocker: MockerFixture):
        """Always passes per_mode='PerGame' to the underlying endpoint."""
        row = _make_team_row()
        response = mocker.MagicMock()
        response.teams = [row]
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        await get_league_averages(client)

        endpoint = client.get.call_args[0][0]
        assert endpoint.per_mode == "PerGame"

    async def test_lg_pace_uses_possession_formula(self, mocker: MockerFixture):
        """lg_pace = fga - oreb + tov + 0.44 * fta (Dean Oliver formula)."""
        row = _make_team_row(fga=80.0, oreb=8.0, tov=12.0, fta=20.0)
        # expected: 80 - 8 + 12 + 0.44 * 20 = 92.8
        response = mocker.MagicMock()
        response.teams = [row]
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        result = await get_league_averages(client)

        assert abs(result.lg_pace - 92.8) < 0.01

    async def test_returns_league_averages_with_correct_pts(
        self, mocker: MockerFixture
    ):
        """lg_pts equals the mean of team point totals."""
        from fastbreak.metrics import LeagueAverages  # noqa: PLC0415

        row = _make_team_row(pts=115.0)
        response = mocker.MagicMock()
        response.teams = [row]
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        result = await get_league_averages(client)

        assert isinstance(result, LeagueAverages)
        assert result.lg_pts == 115.0
