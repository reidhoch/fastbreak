"""Tests for the game finder wrapper module."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest
from hypothesis import given, settings, strategies as st
from pytest_mock import MockerFixture

from fastbreak.clients.nba import NBAClient
from fastbreak.models.league_game_finder import GameFinderResult
from tests.strategies import XDIST_SUPPRESS, game_finder_result_st, wl_st

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_result(**overrides) -> GameFinderResult:
    """Build a GameFinderResult with sensible defaults, overridable per-field."""
    data = {
        "SEASON_ID": "22025",
        "TEAM_ID": 1,
        "TEAM_ABBREVIATION": "TST",
        "TEAM_NAME": "Test Team",
        "GAME_ID": "0022500001",
        "GAME_DATE": "2025-01-15",
        "MATCHUP": "TST vs. OPP",
        "WL": "W",
        "MIN": 240,
        "PTS": 100,
        "FGM": 40,
        "FGA": 80,
        "FG_PCT": 0.500,
        "FG3M": 10,
        "FG3A": 30,
        "FG3_PCT": 0.333,
        "FTM": 10,
        "FTA": 15,
        "FT_PCT": 0.667,
        "OREB": 10,
        "DREB": 30,
        "REB": 40,
        "AST": 25,
        "STL": 8,
        "BLK": 5,
        "TOV": 12,
        "PF": 20,
        "PLUS_MINUS": 5.0,
    }
    data.update(overrides)
    return GameFinderResult.model_validate(data)


# ---------------------------------------------------------------------------
# find_team_games
# ---------------------------------------------------------------------------


class TestFindTeamGames:
    """Tests for find_team_games()."""

    async def test_sets_player_or_team_to_t(self, mocker: MockerFixture):
        """Endpoint is constructed with player_or_team='T'."""
        from fastbreak.game_finder import find_team_games

        response = mocker.MagicMock()
        response.games = []
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        await find_team_games(client, team_id=1610612747)

        endpoint = client.get.call_args[0][0]
        assert endpoint.player_or_team == "T"

    async def test_converts_team_id_to_str(self, mocker: MockerFixture):
        """team_id int is converted to str on the endpoint."""
        from fastbreak.game_finder import find_team_games

        response = mocker.MagicMock()
        response.games = []
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        await find_team_games(client, team_id=1610612747)

        endpoint = client.get.call_args[0][0]
        assert endpoint.team_id == "1610612747"

    async def test_converts_vs_team_id_to_str(self, mocker: MockerFixture):
        """vs_team_id int is converted to str on the endpoint."""
        from fastbreak.game_finder import find_team_games

        response = mocker.MagicMock()
        response.games = []
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        await find_team_games(client, team_id=1, vs_team_id=1610612738)

        endpoint = client.get.call_args[0][0]
        assert endpoint.vs_team_id == "1610612738"

    async def test_converts_gt_thresholds_to_str(self, mocker: MockerFixture):
        """All gt_* int thresholds are converted to str on the endpoint."""
        from fastbreak.game_finder import find_team_games

        response = mocker.MagicMock()
        response.games = []
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        await find_team_games(
            client,
            team_id=1,
            gt_pts=100,
            gt_reb=50,
            gt_ast=25,
            gt_stl=10,
            gt_blk=5,
        )

        endpoint = client.get.call_args[0][0]
        assert endpoint.gt_pts == "100"
        assert endpoint.gt_reb == "50"
        assert endpoint.gt_ast == "25"
        assert endpoint.gt_stl == "10"
        assert endpoint.gt_blk == "5"

    async def test_passes_season_through(self, mocker: MockerFixture):
        """season is passed directly to the endpoint."""
        from fastbreak.game_finder import find_team_games

        response = mocker.MagicMock()
        response.games = []
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        await find_team_games(client, team_id=1, season="2024-25")

        endpoint = client.get.call_args[0][0]
        assert endpoint.season == "2024-25"

    async def test_passes_season_type_through(self, mocker: MockerFixture):
        """season_type is passed directly to the endpoint."""
        from fastbreak.game_finder import find_team_games

        response = mocker.MagicMock()
        response.games = []
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        await find_team_games(client, team_id=1, season_type="Playoffs")

        endpoint = client.get.call_args[0][0]
        assert endpoint.season_type == "Playoffs"

    async def test_passes_date_filters_through(self, mocker: MockerFixture):
        """date_from and date_to are passed directly to the endpoint."""
        from fastbreak.game_finder import find_team_games

        response = mocker.MagicMock()
        response.games = []
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        await find_team_games(
            client, team_id=1, date_from="01/01/2025", date_to="01/31/2025"
        )

        endpoint = client.get.call_args[0][0]
        assert endpoint.date_from == "01/01/2025"
        assert endpoint.date_to == "01/31/2025"

    async def test_passes_outcome_through(self, mocker: MockerFixture):
        """outcome is passed directly to the endpoint."""
        from fastbreak.game_finder import find_team_games

        response = mocker.MagicMock()
        response.games = []
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        await find_team_games(client, team_id=1, outcome="W")

        endpoint = client.get.call_args[0][0]
        assert endpoint.outcome == "W"

    async def test_location_not_sent_to_endpoint(self, mocker: MockerFixture):
        """location is NOT forwarded to the endpoint (filtered client-side instead)."""
        from fastbreak.game_finder import find_team_games

        response = mocker.MagicMock()
        response.games = [_make_result(MATCHUP="TST vs. OPP")]
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        await find_team_games(client, team_id=1, location="Home")

        endpoint = client.get.call_args[0][0]
        assert endpoint.location is None

    async def test_location_filters_home_games(self, mocker: MockerFixture):
        """location='Home' keeps only games with 'vs.' in matchup."""
        from fastbreak.game_finder import find_team_games

        response = mocker.MagicMock()
        response.games = [
            _make_result(MATCHUP="TST vs. OPP", GAME_ID="0022500001"),
            _make_result(MATCHUP="TST @ OPP", GAME_ID="0022500002"),
        ]
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        result = await find_team_games(client, team_id=1, location="Home")

        assert len(result) == 1
        assert result[0].game_id == "0022500001"

    async def test_location_filters_road_games(self, mocker: MockerFixture):
        """location='Road' keeps only games with '@' in matchup."""
        from fastbreak.game_finder import find_team_games

        response = mocker.MagicMock()
        response.games = [
            _make_result(MATCHUP="TST vs. OPP", GAME_ID="0022500001"),
            _make_result(MATCHUP="TST @ OPP", GAME_ID="0022500002"),
        ]
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        result = await find_team_games(client, team_id=1, location="Road")

        assert len(result) == 1
        assert result[0].game_id == "0022500002"

    async def test_location_excludes_none_matchup(self, mocker: MockerFixture):
        """Games with matchup=None are excluded when location is specified."""
        from fastbreak.game_finder import find_team_games

        response = mocker.MagicMock()
        response.games = [
            _make_result(MATCHUP="TST vs. OPP", GAME_ID="0022500001"),
            _make_result(MATCHUP=None, GAME_ID="0022500002"),
        ]
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        result = await find_team_games(client, team_id=1, location="Home")

        assert len(result) == 1
        assert result[0].game_id == "0022500001"

    async def test_returns_games_list(self, mocker: MockerFixture):
        """Returns the response.games list."""
        from fastbreak.game_finder import find_team_games

        games = [_make_result(), _make_result(GAME_ID="0022500002")]
        response = mocker.MagicMock()
        response.games = games
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        result = await find_team_games(client, team_id=1)

        assert result is games

    async def test_returns_empty_list_when_no_games(self, mocker: MockerFixture):
        """Returns empty list when API returns no matching games."""
        from fastbreak.game_finder import find_team_games

        response = mocker.MagicMock()
        response.games = []
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        result = await find_team_games(client, team_id=1)

        assert result == []

    async def test_omits_none_params(self, mocker: MockerFixture):
        """Optional params default to None on the endpoint when not provided."""
        from fastbreak.game_finder import find_team_games

        response = mocker.MagicMock()
        response.games = []
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        await find_team_games(client, team_id=1)

        endpoint = client.get.call_args[0][0]
        assert endpoint.vs_team_id is None
        assert endpoint.season is None
        assert endpoint.gt_pts is None


# ---------------------------------------------------------------------------
# find_player_games
# ---------------------------------------------------------------------------


class TestFindPlayerGames:
    """Tests for find_player_games()."""

    async def test_sets_player_or_team_to_p(self, mocker: MockerFixture):
        """Endpoint is constructed with player_or_team='P'."""
        from fastbreak.game_finder import find_player_games

        response = mocker.MagicMock()
        response.games = []
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        await find_player_games(client, player_id=201939)

        endpoint = client.get.call_args[0][0]
        assert endpoint.player_or_team == "P"

    async def test_converts_player_id_to_str(self, mocker: MockerFixture):
        """player_id int is converted to str on the endpoint."""
        from fastbreak.game_finder import find_player_games

        response = mocker.MagicMock()
        response.games = []
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        await find_player_games(client, player_id=201939)

        endpoint = client.get.call_args[0][0]
        assert endpoint.player_id == "201939"

    async def test_converts_team_id_to_str(self, mocker: MockerFixture):
        """Optional team_id int is converted to str on the endpoint."""
        from fastbreak.game_finder import find_player_games

        response = mocker.MagicMock()
        response.games = []
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        await find_player_games(client, player_id=201939, team_id=1610612744)

        endpoint = client.get.call_args[0][0]
        assert endpoint.team_id == "1610612744"

    async def test_converts_vs_team_id_to_str(self, mocker: MockerFixture):
        """vs_team_id int is converted to str on the endpoint."""
        from fastbreak.game_finder import find_player_games

        response = mocker.MagicMock()
        response.games = []
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        await find_player_games(client, player_id=1, vs_team_id=1610612738)

        endpoint = client.get.call_args[0][0]
        assert endpoint.vs_team_id == "1610612738"

    async def test_passes_season_through(self, mocker: MockerFixture):
        """season is passed directly to the endpoint."""
        from fastbreak.game_finder import find_player_games

        response = mocker.MagicMock()
        response.games = []
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        await find_player_games(client, player_id=1, season="2025-26")

        endpoint = client.get.call_args[0][0]
        assert endpoint.season == "2025-26"

    async def test_converts_gt_pts_to_str(self, mocker: MockerFixture):
        """gt_pts int is converted to str on the endpoint."""
        from fastbreak.game_finder import find_player_games

        response = mocker.MagicMock()
        response.games = []
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        await find_player_games(client, player_id=1, gt_pts=30)

        endpoint = client.get.call_args[0][0]
        assert endpoint.gt_pts == "30"

    async def test_returns_games_list(self, mocker: MockerFixture):
        """Returns the response.games list."""
        from fastbreak.game_finder import find_player_games

        games = [_make_result()]
        response = mocker.MagicMock()
        response.games = games
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        result = await find_player_games(client, player_id=1)

        assert result is games

    async def test_returns_empty_list_when_no_games(self, mocker: MockerFixture):
        """Returns empty list when API returns no matching games."""
        from fastbreak.game_finder import find_player_games

        response = mocker.MagicMock()
        response.games = []
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        result = await find_player_games(client, player_id=1)

        assert result == []


# ---------------------------------------------------------------------------
# aggregate_games
# ---------------------------------------------------------------------------


class TestAggregateGames:
    """Tests for aggregate_games()."""

    def test_empty_list_returns_zeroed_averages(self):
        """Empty input returns GameAverages with 0.0 counting stats and None pcts."""
        from fastbreak.game_finder import aggregate_games

        result = aggregate_games([])

        assert result.pts == 0.0
        assert result.reb == 0.0
        assert result.ast == 0.0
        assert result.stl == 0.0
        assert result.blk == 0.0
        assert result.tov == 0.0
        assert result.fg_pct is None
        assert result.fg3_pct is None
        assert result.ft_pct is None
        assert result.plus_minus is None

    def test_single_game_identity(self):
        """Single game returns its own stats as averages."""
        from fastbreak.game_finder import aggregate_games

        game = _make_result(PTS=25, REB=10, AST=5, STL=2, BLK=1, TOV=3)
        result = aggregate_games([game])

        assert result.pts == 25.0
        assert result.reb == 10.0
        assert result.ast == 5.0
        assert result.stl == 2.0
        assert result.blk == 1.0
        assert result.tov == 3.0

    def test_two_games_averages(self):
        """Two games produce arithmetic mean for each stat."""
        from fastbreak.game_finder import aggregate_games

        g1 = _make_result(PTS=20, REB=8, AST=4, STL=2, BLK=1, TOV=2)
        g2 = _make_result(PTS=30, REB=12, AST=6, STL=4, BLK=3, TOV=4)
        result = aggregate_games([g1, g2])

        assert result.pts == pytest.approx(25.0)
        assert result.reb == pytest.approx(10.0)
        assert result.ast == pytest.approx(5.0)
        assert result.stl == pytest.approx(3.0)
        assert result.blk == pytest.approx(2.0)
        assert result.tov == pytest.approx(3.0)

    def test_averages_pct_fields(self):
        """Percentage fields are averaged from non-None values."""
        from fastbreak.game_finder import aggregate_games

        g1 = _make_result(FG_PCT=0.500, FG3_PCT=0.400, FT_PCT=0.800)
        g2 = _make_result(FG_PCT=0.600, FG3_PCT=0.300, FT_PCT=0.900)
        result = aggregate_games([g1, g2])

        assert result.fg_pct == pytest.approx(0.550)
        assert result.fg3_pct == pytest.approx(0.350)
        assert result.ft_pct == pytest.approx(0.850)

    def test_none_pct_excluded_from_average(self):
        """Games with None pct are excluded; average computed from non-None only."""
        from fastbreak.game_finder import aggregate_games

        g1 = _make_result(FG_PCT=0.500, FG3_PCT=None, FT_PCT=0.800)
        g2 = _make_result(FG_PCT=0.600, FG3_PCT=None, FT_PCT=0.900)
        result = aggregate_games([g1, g2])

        assert result.fg_pct == pytest.approx(0.550)
        assert result.fg3_pct is None
        assert result.ft_pct == pytest.approx(0.850)

    def test_averages_plus_minus(self):
        """plus_minus is averaged from non-None values."""
        from fastbreak.game_finder import aggregate_games

        g1 = _make_result(PLUS_MINUS=10.0)
        g2 = _make_result(PLUS_MINUS=-6.0)
        result = aggregate_games([g1, g2])

        assert result.plus_minus == pytest.approx(2.0)

    def test_plus_minus_none_excluded(self):
        """plus_minus None values are excluded from the average."""
        from fastbreak.game_finder import aggregate_games

        g1 = _make_result(PLUS_MINUS=10.0)
        g2 = _make_result(PLUS_MINUS=None)
        result = aggregate_games([g1, g2])

        assert result.plus_minus == pytest.approx(10.0)

    def test_return_type_is_frozen(self):
        """GameAverages is a frozen dataclass."""
        from fastbreak.game_finder import aggregate_games

        result = aggregate_games([_make_result()])
        with pytest.raises(FrozenInstanceError):
            result.pts = 999  # type: ignore[misc]

    def test_game_averages_is_frozen_dataclass(self):
        """GameAverages has frozen=True in its dataclass params."""
        from fastbreak.game_finder import GameAverages

        assert GameAverages.__dataclass_params__.frozen is True

    def test_game_averages_uses_slots(self):
        """GameAverages uses __slots__ for memory efficiency."""
        from fastbreak.game_finder import GameAverages

        assert hasattr(GameAverages, "__slots__")


# ---------------------------------------------------------------------------
# streak_games
# ---------------------------------------------------------------------------


class TestStreakGames:
    """Tests for streak_games()."""

    def test_empty_returns_empty(self):
        """Empty input returns empty list."""
        from fastbreak.game_finder import streak_games

        assert streak_games([]) == []

    def test_single_win(self):
        """One win game produces one streak of length 1."""
        from fastbreak.game_finder import streak_games

        result = streak_games([_make_result(WL="W")])

        assert len(result) == 1
        assert len(result[0]) == 1
        assert result[0][0].wl == "W"

    def test_single_loss(self):
        """One loss game produces one streak of length 1."""
        from fastbreak.game_finder import streak_games

        result = streak_games([_make_result(WL="L")])

        assert len(result) == 1
        assert result[0][0].wl == "L"

    def test_alternating_wl(self):
        """W, L, W, L produces four streaks of length 1 each."""
        from fastbreak.game_finder import streak_games

        games = [_make_result(WL=wl) for wl in ["W", "L", "W", "L"]]
        result = streak_games(games)

        assert len(result) == 4
        assert all(len(s) == 1 for s in result)

    def test_consecutive_wins(self):
        """W, W, W produces one streak of length 3."""
        from fastbreak.game_finder import streak_games

        games = [_make_result(WL="W") for _ in range(3)]
        result = streak_games(games)

        assert len(result) == 1
        assert len(result[0]) == 3

    def test_consecutive_losses(self):
        """L, L, L produces one streak of length 3."""
        from fastbreak.game_finder import streak_games

        games = [_make_result(WL="L") for _ in range(3)]
        result = streak_games(games)

        assert len(result) == 1
        assert len(result[0]) == 3

    def test_mixed_streaks(self):
        """W, W, L, L, L, W produces three streaks: 2W, 3L, 1W."""
        from fastbreak.game_finder import streak_games

        games = [_make_result(WL=wl) for wl in ["W", "W", "L", "L", "L", "W"]]
        result = streak_games(games)

        assert len(result) == 3
        assert len(result[0]) == 2
        assert result[0][0].wl == "W"
        assert len(result[1]) == 3
        assert result[1][0].wl == "L"
        assert len(result[2]) == 1
        assert result[2][0].wl == "W"

    def test_none_wl_breaks_streak(self):
        """Games with wl=None break the current streak and are excluded."""
        from fastbreak.game_finder import streak_games

        games = [
            _make_result(WL="W"),
            _make_result(WL=None),
            _make_result(WL="W"),
        ]
        result = streak_games(games)

        assert len(result) == 2
        assert len(result[0]) == 1
        assert len(result[1]) == 1

    def test_total_equals_input_minus_nones(self):
        """Sum of streak lengths equals number of non-None wl games."""
        from fastbreak.game_finder import streak_games

        games = [
            _make_result(WL="W"),
            _make_result(WL="W"),
            _make_result(WL=None),
            _make_result(WL="L"),
        ]
        result = streak_games(games)
        total = sum(len(s) for s in result)

        assert total == 3  # 2W + 1L, None excluded


# ---------------------------------------------------------------------------
# summarize_record
# ---------------------------------------------------------------------------


class TestSummarizeRecord:
    """Tests for summarize_record()."""

    def test_empty_list(self):
        """Empty input returns Record(0, 0, 0.0)."""
        from fastbreak.game_finder import summarize_record

        result = summarize_record([])

        assert result.wins == 0
        assert result.losses == 0
        assert result.win_pct == 0.0

    def test_all_wins(self):
        """All W games give win_pct=1.0."""
        from fastbreak.game_finder import summarize_record

        games = [_make_result(WL="W") for _ in range(5)]
        result = summarize_record(games)

        assert result.wins == 5
        assert result.losses == 0
        assert result.win_pct == 1.0

    def test_all_losses(self):
        """All L games give win_pct=0.0."""
        from fastbreak.game_finder import summarize_record

        games = [_make_result(WL="L") for _ in range(5)]
        result = summarize_record(games)

        assert result.wins == 0
        assert result.losses == 5
        assert result.win_pct == 0.0

    def test_mixed_record(self):
        """3W + 2L gives win_pct=0.6."""
        from fastbreak.game_finder import summarize_record

        games = [_make_result(WL=wl) for wl in ["W", "W", "W", "L", "L"]]
        result = summarize_record(games)

        assert result.wins == 3
        assert result.losses == 2
        assert result.win_pct == pytest.approx(0.6)

    def test_none_wl_excluded(self):
        """Games with wl=None are not counted."""
        from fastbreak.game_finder import summarize_record

        games = [_make_result(WL="W"), _make_result(WL=None), _make_result(WL="L")]
        result = summarize_record(games)

        assert result.wins == 1
        assert result.losses == 1
        assert result.win_pct == pytest.approx(0.5)

    def test_return_type_is_frozen(self):
        """Record is a frozen dataclass."""
        from fastbreak.game_finder import summarize_record

        result = summarize_record([_make_result()])
        with pytest.raises(FrozenInstanceError):
            result.wins = 999  # type: ignore[misc]

    def test_record_uses_slots(self):
        """Record uses __slots__ for memory efficiency."""
        from fastbreak.game_finder import Record

        assert hasattr(Record, "__slots__")

    def test_win_pct_is_float(self):
        """win_pct is always a float."""
        from fastbreak.game_finder import summarize_record

        result = summarize_record([_make_result(WL="W")])
        assert isinstance(result.win_pct, float)


# ---------------------------------------------------------------------------
# Property-based tests
# ---------------------------------------------------------------------------


class TestGameFinderPBT:
    """Property-based tests for game finder helpers."""

    # --- aggregate_games ---

    @settings(suppress_health_check=XDIST_SUPPRESS)
    @given(game=game_finder_result_st())
    def test_aggregate_single_game_identity(self, game: GameFinderResult):
        """Aggregating a single game returns its own counting stats."""
        from fastbreak.game_finder import aggregate_games

        result = aggregate_games([game])

        assert result.pts == pytest.approx(float(game.pts))
        assert result.reb == pytest.approx(float(game.reb))
        assert result.ast == pytest.approx(float(game.ast))
        assert result.stl == pytest.approx(float(game.stl))
        assert result.blk == pytest.approx(float(game.blk))
        assert result.tov == pytest.approx(float(game.tov))

    @settings(suppress_health_check=XDIST_SUPPRESS)
    @given(games=st.lists(game_finder_result_st(), min_size=1, max_size=10))
    def test_aggregate_non_negative_counting_stats(self, games: list[GameFinderResult]):
        """All averaged counting stats are non-negative."""
        from fastbreak.game_finder import aggregate_games

        result = aggregate_games(games)

        assert result.pts >= 0
        assert result.reb >= 0
        assert result.ast >= 0
        assert result.stl >= 0
        assert result.blk >= 0
        assert result.tov >= 0

    @settings(suppress_health_check=XDIST_SUPPRESS)
    @given(games=st.lists(game_finder_result_st(), min_size=1, max_size=10))
    def test_aggregate_pct_bounded(self, games: list[GameFinderResult]):
        """Averaged pct fields are in [0, 1] when non-None."""
        from fastbreak.game_finder import aggregate_games

        result = aggregate_games(games)

        for pct in (result.fg_pct, result.fg3_pct, result.ft_pct):
            if pct is not None:
                assert 0.0 <= pct <= 1.0

    # --- streak_games ---

    @settings(suppress_health_check=XDIST_SUPPRESS)
    @given(games=st.lists(game_finder_result_st(), min_size=0, max_size=15))
    def test_streak_total_equals_non_none_count(self, games: list[GameFinderResult]):
        """Sum of streak lengths equals number of games with non-None wl."""
        from fastbreak.game_finder import streak_games

        result = streak_games(games)
        total = sum(len(s) for s in result)
        expected = sum(1 for g in games if g.wl is not None)

        assert total == expected

    @settings(suppress_health_check=XDIST_SUPPRESS)
    @given(games=st.lists(game_finder_result_st(), min_size=1, max_size=15))
    def test_each_streak_has_uniform_wl(self, games: list[GameFinderResult]):
        """Every streak contains games with the same wl value."""
        from fastbreak.game_finder import streak_games

        result = streak_games(games)

        for streak in result:
            wl_values = {g.wl for g in streak}
            assert len(wl_values) == 1

    @settings(suppress_health_check=XDIST_SUPPRESS)
    @given(games=st.lists(game_finder_result_st(), min_size=1, max_size=15))
    def test_consecutive_streaks_differ_when_no_none_wl(
        self, games: list[GameFinderResult]
    ):
        """Adjacent streaks differ when input has no None wl values."""
        from hypothesis import assume

        from fastbreak.game_finder import streak_games

        assume(all(g.wl is not None for g in games))
        result = streak_games(games)

        for i in range(len(result) - 1):
            assert result[i][0].wl != result[i + 1][0].wl

    # --- summarize_record ---

    @settings(suppress_health_check=XDIST_SUPPRESS)
    @given(games=st.lists(game_finder_result_st(), min_size=0, max_size=15))
    def test_wins_plus_losses_equals_counted_games(self, games: list[GameFinderResult]):
        """wins + losses equals number of games with non-None wl."""
        from fastbreak.game_finder import summarize_record

        result = summarize_record(games)
        expected = sum(1 for g in games if g.wl is not None)

        assert result.wins + result.losses == expected

    @settings(suppress_health_check=XDIST_SUPPRESS)
    @given(games=st.lists(game_finder_result_st(), min_size=1, max_size=15))
    def test_win_pct_in_range(self, games: list[GameFinderResult]):
        """win_pct is always between 0.0 and 1.0."""
        from fastbreak.game_finder import summarize_record

        result = summarize_record(games)

        assert 0.0 <= result.win_pct <= 1.0

    @settings(suppress_health_check=XDIST_SUPPRESS)
    @given(wl=wl_st, n=st.integers(min_value=1, max_value=20))
    def test_all_same_wl_gives_extreme_pct(self, wl: str, n: int):
        """All W → 1.0, all L → 0.0 (kills == vs != mutations)."""
        from fastbreak.game_finder import summarize_record

        games = [_make_result(WL=wl) for _ in range(n)]
        result = summarize_record(games)

        if wl == "W":
            assert result.win_pct == 1.0
        else:
            assert result.win_pct == 0.0
