"""Tests for schedule utilities."""

from __future__ import annotations

from datetime import date
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from fastbreak.clients.nba import NBAClient
from fastbreak.schedule import (
    _collect_team_games,
    _schedule_sort_key,
    days_rest_before_game,
    get_team_schedule,
    is_back_to_back,
)


class TestDaysRestBeforeGame:
    def test_same_day_is_zero(self):
        game_dates = [date(2025, 1, 15), date(2025, 1, 15)]
        assert days_rest_before_game(game_dates, 1) == 0

    def test_next_day_is_zero(self):
        """Back-to-back means 0 days rest."""
        game_dates = [date(2025, 1, 15), date(2025, 1, 16)]
        assert days_rest_before_game(game_dates, 1) == 0

    def test_one_day_gap_is_one(self):
        game_dates = [date(2025, 1, 15), date(2025, 1, 17)]
        assert days_rest_before_game(game_dates, 1) == 1

    def test_first_game_returns_none(self):
        game_dates = [date(2025, 1, 15)]
        assert days_rest_before_game(game_dates, 0) is None


class TestIsBackToBack:
    def test_consecutive_dates_is_back_to_back(self):
        game_dates = [date(2025, 1, 15), date(2025, 1, 16)]
        assert is_back_to_back(game_dates, 1) is True

    def test_one_day_off_is_not_back_to_back(self):
        game_dates = [date(2025, 1, 15), date(2025, 1, 17)]
        assert is_back_to_back(game_dates, 1) is False

    def test_first_game_is_not_back_to_back(self):
        game_dates = [date(2025, 1, 15), date(2025, 1, 16)]
        assert is_back_to_back(game_dates, 0) is False


class TestScheduleSortKey:
    """Tests for the _schedule_sort_key helper."""

    def test_returns_date_when_present(self):
        """Returns game_date_est string when it is set."""
        game = MagicMock()
        game.game_date_est = "2025-01-15"

        assert _schedule_sort_key(game) == "2025-01-15"

    def test_returns_sentinel_when_date_missing(self):
        """Returns '9999-99-99' sentinel when game_date_est is None."""
        game = MagicMock()
        game.game_date_est = None

        assert _schedule_sort_key(game) == "9999-99-99"

    def test_sentinel_sorts_after_any_real_date(self):
        """The sentinel sorts lexicographically after any valid YYYY-MM-DD date."""
        game_real = MagicMock()
        game_real.game_date_est = "2099-12-31"
        game_none = MagicMock()
        game_none.game_date_est = None

        assert _schedule_sort_key(game_none) > _schedule_sort_key(game_real)


class TestCollectTeamGames:
    """Tests for the _collect_team_games helper."""

    def _make_game(self, home_id: int | None, away_id: int | None) -> MagicMock:
        game = MagicMock()
        if home_id is None:
            game.home_team = None
        else:
            game.home_team = MagicMock()
            game.home_team.team_id = home_id
        if away_id is None:
            game.away_team = None
        else:
            game.away_team = MagicMock()
            game.away_team.team_id = away_id
        return game

    def _make_schedule(self, games_by_date: list[list]) -> MagicMock:
        schedule = MagicMock()
        game_dates = []
        for games in games_by_date:
            gd = MagicMock()
            gd.games = games
            game_dates.append(gd)
        schedule.game_dates = game_dates
        return schedule

    def test_returns_game_where_team_is_home(self):
        """Returns a game where the given team is the home team."""
        game = self._make_game(home_id=1, away_id=2)
        schedule = self._make_schedule([[game]])

        assert _collect_team_games(schedule, team_id=1) == [game]

    def test_returns_game_where_team_is_away(self):
        """Returns a game where the given team is the away team."""
        game = self._make_game(home_id=1, away_id=2)
        schedule = self._make_schedule([[game]])

        assert _collect_team_games(schedule, team_id=2) == [game]

    def test_excludes_game_not_involving_team(self):
        """Excludes games where neither team matches."""
        game = self._make_game(home_id=1, away_id=2)
        schedule = self._make_schedule([[game]])

        assert _collect_team_games(schedule, team_id=3) == []

    def test_handles_none_home_team(self):
        """game.home_team is None — away team should still match correctly."""
        game = self._make_game(home_id=None, away_id=2)
        schedule = self._make_schedule([[game]])

        assert _collect_team_games(schedule, team_id=2) == [game]
        assert _collect_team_games(schedule, team_id=99) == []

    def test_handles_none_away_team(self):
        """game.away_team is None — home team should still match correctly."""
        game = self._make_game(home_id=1, away_id=None)
        schedule = self._make_schedule([[game]])

        assert _collect_team_games(schedule, team_id=1) == [game]
        assert _collect_team_games(schedule, team_id=99) == []

    def test_collects_across_multiple_game_dates(self):
        """Gathers team games from multiple GameDate entries."""
        game1 = self._make_game(home_id=1, away_id=2)
        game2 = self._make_game(home_id=3, away_id=1)
        schedule = self._make_schedule([[game1], [game2]])

        result = _collect_team_games(schedule, team_id=1)

        assert result == [game1, game2]


class TestGetTeamSchedule:
    """Tests for the get_team_schedule async function."""

    async def test_returns_empty_when_league_schedule_is_none(
        self, mocker: MockerFixture
    ):
        """Returns [] when league_schedule is absent from the response."""
        response = mocker.MagicMock()
        response.league_schedule = None
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        result = await get_team_schedule(client, team_id=1)

        assert result == []

    async def test_logs_warning_when_league_schedule_is_none(
        self, mocker: MockerFixture
    ):
        """Emits a WARNING when league_schedule is None."""
        response = mocker.MagicMock()
        response.league_schedule = None
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)
        mock_logger = mocker.patch("fastbreak.schedule.logger")

        await get_team_schedule(client, team_id=1)

        mock_logger.warning.assert_called_once()

    async def test_returns_games_sorted_chronologically(self, mocker: MockerFixture):
        """Games are returned in chronological order regardless of input order."""
        game_later = mocker.MagicMock()
        game_later.game_date_est = "2025-01-20"
        game_later.home_team = mocker.MagicMock()
        game_later.home_team.team_id = 1
        game_later.away_team = mocker.MagicMock()
        game_later.away_team.team_id = 2

        game_earlier = mocker.MagicMock()
        game_earlier.game_date_est = "2025-01-10"
        game_earlier.home_team = mocker.MagicMock()
        game_earlier.home_team.team_id = 1
        game_earlier.away_team = mocker.MagicMock()
        game_earlier.away_team.team_id = 3

        game_date = mocker.MagicMock()
        game_date.games = [game_later, game_earlier]  # later game first in input

        league_schedule = mocker.MagicMock()
        league_schedule.game_dates = [game_date]

        response = mocker.MagicMock()
        response.league_schedule = league_schedule

        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        result = await get_team_schedule(client, team_id=1)

        assert result == [game_earlier, game_later]
