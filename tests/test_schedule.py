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
    game_dates_from_schedule,
    get_season_schedule,
    get_team_schedule,
    is_back_to_back,
    is_home_game,
    rest_advantage,
    schedule_density,
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

    def test_three_day_gap_is_two(self):
        """Jan 15 → Jan 18 = 2 days rest (kills off-by-one in delta.days - 1)."""
        game_dates = [date(2025, 1, 15), date(2025, 1, 18)]
        assert days_rest_before_game(game_dates, 1) == 2

    def test_multi_day_gap_is_correct(self):
        """Larger gap: Jan 15 → Jan 20 = 4 days rest."""
        game_dates = [date(2025, 1, 15), date(2025, 1, 20)]
        assert days_rest_before_game(game_dates, 1) == 4

    def test_negative_index_raises(self):
        """Negative game_index raises IndexError (not silent wrap)."""
        game_dates = [date(2025, 1, 15), date(2025, 1, 16)]
        with pytest.raises(IndexError, match="game_index"):
            days_rest_before_game(game_dates, -1)

    def test_out_of_range_index_raises(self):
        """game_index >= len(game_dates) raises IndexError."""
        game_dates = [date(2025, 1, 15)]
        with pytest.raises(IndexError, match="game_index"):
            days_rest_before_game(game_dates, 1)


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

    def test_two_day_gap_is_false(self):
        """2 days rest != back-to-back (kills <= 0 mutated to <= 1)."""
        game_dates = [date(2025, 1, 15), date(2025, 1, 18)]
        assert is_back_to_back(game_dates, 1) is False

    def test_same_day_is_true(self):
        """Same date = 0 rest = back-to-back."""
        game_dates = [date(2025, 1, 15), date(2025, 1, 15)]
        assert is_back_to_back(game_dates, 1) is True


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


def _make_arena_game(
    game_id: str | None,
    arena_city: str | None,
    arena_state: str | None,
) -> MagicMock:
    """Build a MagicMock ScheduledGame with arena location fields set."""
    g = MagicMock()
    g.game_id = game_id
    g.arena_city = arena_city
    g.arena_state = arena_state
    return g


class TestArenaCoords:
    """Tests for _ARENA_COORDS completeness."""

    def test_covers_all_30_teams(self):
        """30 NBA + 4 WNBA-only arena entries."""
        from fastbreak.schedule import _ARENA_COORDS

        assert len(_ARENA_COORDS) == 34

    def test_all_coords_are_valid(self):
        """Each entry has (lat, lon, utc_offset) within plausible ranges."""
        from fastbreak.schedule import _ARENA_COORDS

        for (city, state), (lat, lon, tz) in _ARENA_COORDS.items():
            assert -90 <= lat <= 90, f"{city}, {state}: bad lat {lat}"
            assert -180 <= lon <= 180, f"{city}, {state}: bad lon {lon}"
            assert -12 <= tz <= 14, f"{city}, {state}: bad tz {tz}"


class TestHaversineMiles:
    """Tests for the _haversine_miles helper."""

    def test_same_point_is_zero(self):
        from fastbreak.schedule import _haversine_miles

        assert _haversine_miles(40.75, -73.99, 40.75, -73.99) == 0.0

    def test_la_to_boston_approx(self):
        """LAX → BOS great-circle is roughly 2,600 miles."""
        from fastbreak.schedule import _haversine_miles

        miles = _haversine_miles(34.043, -118.267, 42.366, -71.062)
        assert 2550 < miles < 2650


class TestTravelDistance:
    """Tests for the travel_distance function."""

    def _make_game(
        self,
        game_id: str,
        arena_city: str | None,
        arena_state: str | None,
    ) -> MagicMock:
        return _make_arena_game(game_id, arena_city, arena_state)

    def test_returns_none_for_first_game(self):
        from fastbreak.schedule import travel_distance

        games = [self._make_game("001", "Los Angeles", "CA")]
        assert travel_distance(games, "001") is None

    def test_returns_none_when_game_id_not_found(self):
        from fastbreak.schedule import travel_distance

        games = [self._make_game("001", "Los Angeles", "CA")]
        assert travel_distance(games, "999") is None

    def test_returns_none_when_arena_city_missing(self):
        from fastbreak.schedule import travel_distance

        games = [
            self._make_game("001", "Los Angeles", "CA"),
            self._make_game("002", None, "MA"),
        ]
        assert travel_distance(games, "002") is None

    def test_returns_none_when_city_not_in_lookup(self):
        """Neutral-site or unrecognised city returns None."""
        from fastbreak.schedule import travel_distance

        games = [
            self._make_game("001", "Los Angeles", "CA"),
            self._make_game("002", "London", "ENG"),
        ]
        assert travel_distance(games, "002") is None

    def test_la_to_boston_miles_and_tz(self):
        """LA → Boston: ~2,600 miles, +3h east."""
        from fastbreak.schedule import TravelLeg, travel_distance

        games = [
            self._make_game("001", "Los Angeles", "CA"),
            self._make_game("002", "Boston", "MA"),
        ]
        result = travel_distance(games, "002")
        assert isinstance(result, TravelLeg)
        assert 2550 < result.miles < 2650
        assert result.tz_shift == 3

    def test_boston_to_la_miles_and_tz(self):
        """Boston → LA: same distance, -3h west."""
        from fastbreak.schedule import travel_distance

        games = [
            self._make_game("001", "Boston", "MA"),
            self._make_game("002", "Los Angeles", "CA"),
        ]
        result = travel_distance(games, "002")
        assert result is not None
        assert 2550 < result.miles < 2650
        assert result.tz_shift == -3

    def test_same_arena_is_zero_miles_zero_tz(self):
        """Home game after home game: 0 miles, 0 tz shift."""
        from fastbreak.schedule import travel_distance

        games = [
            self._make_game("001", "Boston", "MA"),
            self._make_game("002", "Boston", "MA"),
        ]
        result = travel_distance(games, "002")
        assert result is not None
        assert result.miles == 0.0
        assert result.tz_shift == 0

    def test_middle_game_uses_correct_predecessor(self):
        """Game[2] leg is from game[1], not game[0]."""
        from fastbreak.schedule import travel_distance

        games = [
            self._make_game("001", "Boston", "MA"),
            self._make_game("002", "Los Angeles", "CA"),
            self._make_game("003", "Denver", "CO"),
        ]
        # Denver from LA, not Denver from Boston
        result = travel_distance(games, "003")
        assert result is not None
        # LA → Denver is ~850 miles; Boston → Denver would be ~1,750
        assert result.miles < 1000

    def test_symmetry_of_miles(self):
        """LA→Boston miles == Boston→LA miles."""
        from fastbreak.schedule import travel_distance

        la_to_bos = travel_distance(
            [
                self._make_game("001", "Los Angeles", "CA"),
                self._make_game("002", "Boston", "MA"),
            ],
            "002",
        )
        bos_to_la = travel_distance(
            [
                self._make_game("001", "Boston", "MA"),
                self._make_game("002", "Los Angeles", "CA"),
            ],
            "002",
        )
        assert la_to_bos is not None
        assert bos_to_la is not None
        assert abs(la_to_bos.miles - bos_to_la.miles) < 0.01


class TestTravelDistances:
    """Tests for the travel_distances bulk function."""

    def _make_game(
        self, game_id: str | None, city: str | None, state: str | None
    ) -> MagicMock:
        return _make_arena_game(game_id, city, state)

    def test_empty_list_returns_empty_dict(self):
        from fastbreak.schedule import travel_distances

        assert travel_distances([]) == {}

    def test_first_game_maps_to_none(self):
        from fastbreak.schedule import travel_distances

        games = [self._make_game("001", "Boston", "MA")]
        assert travel_distances(games) == {"001": None}

    def test_skips_games_with_none_game_id(self):
        from fastbreak.schedule import travel_distances

        games = [
            self._make_game(None, "Boston", "MA"),
            self._make_game("002", "Los Angeles", "CA"),
        ]
        result = travel_distances(games)
        assert None not in result
        assert "002" in result

    def test_full_schedule_single_pass(self):
        """All three games processed; distances match individual travel_distance calls."""
        from fastbreak.schedule import TravelLeg, travel_distance, travel_distances

        games = [
            self._make_game("001", "Boston", "MA"),
            self._make_game("002", "Los Angeles", "CA"),
            self._make_game("003", "Denver", "CO"),
        ]
        bulk = travel_distances(games)

        assert bulk["001"] is None
        assert isinstance(bulk["002"], TravelLeg)
        assert isinstance(bulk["003"], TravelLeg)
        assert bulk["002"] == travel_distance(games, "002")
        assert bulk["003"] == travel_distance(games, "003")

    def test_second_game_leg_matches_single_call(self):
        """Consistency: bulk[game_id] == travel_distance(games, game_id)."""
        from fastbreak.schedule import travel_distance, travel_distances

        games = [
            self._make_game("001", "Chicago", "IL"),
            self._make_game("002", "Miami", "FL"),
        ]
        bulk = travel_distances(games)
        single = travel_distance(games, "002")
        assert bulk["002"] == single

    def test_three_game_chain_order(self):
        """game[1] leg uses game[0], game[2] leg uses game[1] (not game[0])."""
        from fastbreak.schedule import travel_distances

        games = [
            self._make_game("001", "Boston", "MA"),
            self._make_game("002", "Los Angeles", "CA"),
            self._make_game("003", "San Francisco", "CA"),
        ]
        bulk = travel_distances(games)
        assert bulk["003"] is not None
        # SF leg should be from LA (~380 mi), not from Boston (~2700 mi)
        assert bulk["003"].miles < 500


def _make_scheduled_game(
    game_date_est: str | None,
    home_team_id: int | None = None,
    away_team_id: int | None = None,
    game_id: str | None = None,
) -> MagicMock:
    """Build a MagicMock ScheduledGame with date and team fields."""
    g = MagicMock()
    g.game_date_est = game_date_est
    g.game_id = game_id
    if home_team_id is None:
        g.home_team = None
    else:
        g.home_team = MagicMock()
        g.home_team.team_id = home_team_id
    if away_team_id is None:
        g.away_team = None
    else:
        g.away_team = MagicMock()
        g.away_team.team_id = away_team_id
    return g


class TestGameDatesFromSchedule:
    """Tests for game_dates_from_schedule."""

    def test_extracts_dates_in_order(self):
        """Three games produce three dates in chronological order."""
        games = [
            _make_scheduled_game("2025-01-10T00:00:00"),
            _make_scheduled_game("2025-01-12T00:00:00"),
            _make_scheduled_game("2025-01-15T00:00:00"),
        ]
        result = game_dates_from_schedule(games)
        assert result == [date(2025, 1, 10), date(2025, 1, 12), date(2025, 1, 15)]

    def test_skips_games_with_none_date(self):
        """Games with None game_date_est are excluded."""
        games = [
            _make_scheduled_game("2025-01-10T00:00:00"),
            _make_scheduled_game(None),
            _make_scheduled_game("2025-01-15T00:00:00"),
        ]
        result = game_dates_from_schedule(games)
        assert result == [date(2025, 1, 10), date(2025, 1, 15)]

    def test_empty_returns_empty(self):
        """Empty input list produces empty output."""
        assert game_dates_from_schedule([]) == []

    def test_truncates_iso_to_date(self):
        """ISO datetime string is truncated to date-only."""
        games = [_make_scheduled_game("2025-01-15T00:00:00")]
        result = game_dates_from_schedule(games)
        assert result == [date(2025, 1, 15)]

    def test_malformed_date_skipped_with_warning(self):
        """A malformed game_date_est is skipped, not raised."""
        games = [
            _make_scheduled_game("2025-01-10T00:00:00"),
            _make_scheduled_game("not-a-date"),
            _make_scheduled_game("2025-01-15T00:00:00"),
        ]
        result = game_dates_from_schedule(games)
        assert result == [date(2025, 1, 10), date(2025, 1, 15)]


class TestIsHomeGame:
    """Tests for is_home_game."""

    def test_true_when_home(self):
        """Returns True when team_id matches home_team.team_id."""
        game = _make_scheduled_game(
            "2025-01-15T00:00:00", home_team_id=1, away_team_id=2
        )
        assert is_home_game(game, team_id=1) is True

    def test_false_when_away(self):
        """Returns False when team_id matches only the away team."""
        game = _make_scheduled_game(
            "2025-01-15T00:00:00", home_team_id=1, away_team_id=2
        )
        assert is_home_game(game, team_id=2) is False

    def test_false_when_neither(self):
        """Returns False when team_id matches neither team."""
        game = _make_scheduled_game(
            "2025-01-15T00:00:00", home_team_id=1, away_team_id=2
        )
        assert is_home_game(game, team_id=99) is False

    def test_false_when_home_team_none(self):
        """Returns False when game.home_team is None."""
        game = _make_scheduled_game(
            "2025-01-15T00:00:00", home_team_id=None, away_team_id=2
        )
        assert is_home_game(game, team_id=2) is False


class TestRestAdvantage:
    """Tests for rest_advantage."""

    def test_positive_when_home_more_rested(self):
        """Home 2 days rest, away 0 → +2."""
        home_dates = [date(2025, 1, 10), date(2025, 1, 13)]
        away_dates = [date(2025, 1, 12), date(2025, 1, 13)]
        assert rest_advantage(home_dates, away_dates, date(2025, 1, 13)) == 2

    def test_negative_when_away_more_rested(self):
        """Home 0 days rest, away 2 → -2."""
        home_dates = [date(2025, 1, 12), date(2025, 1, 13)]
        away_dates = [date(2025, 1, 10), date(2025, 1, 13)]
        assert rest_advantage(home_dates, away_dates, date(2025, 1, 13)) == -2

    def test_zero_when_equal_rest(self):
        """Both teams with 1 day rest → 0."""
        home_dates = [date(2025, 1, 11), date(2025, 1, 13)]
        away_dates = [date(2025, 1, 11), date(2025, 1, 13)]
        assert rest_advantage(home_dates, away_dates, date(2025, 1, 13)) == 0

    def test_none_when_home_first_game(self):
        """game_date is the first game in home_dates → None (no prior rest info)."""
        home_dates = [date(2025, 1, 13)]
        away_dates = [date(2025, 1, 11), date(2025, 1, 13)]
        assert rest_advantage(home_dates, away_dates, date(2025, 1, 13)) is None

    def test_none_when_away_first_game(self):
        """game_date is the first game in away_dates → None."""
        home_dates = [date(2025, 1, 11), date(2025, 1, 13)]
        away_dates = [date(2025, 1, 13)]
        assert rest_advantage(home_dates, away_dates, date(2025, 1, 13)) is None

    def test_none_when_date_not_in_home(self):
        """game_date absent from home_dates → None."""
        home_dates = [date(2025, 1, 10), date(2025, 1, 12)]
        away_dates = [date(2025, 1, 11), date(2025, 1, 13)]
        assert rest_advantage(home_dates, away_dates, date(2025, 1, 13)) is None

    def test_none_when_date_not_in_away(self):
        """game_date absent from away_dates → None."""
        home_dates = [date(2025, 1, 11), date(2025, 1, 13)]
        away_dates = [date(2025, 1, 10), date(2025, 1, 12)]
        assert rest_advantage(home_dates, away_dates, date(2025, 1, 13)) is None


class TestScheduleDensity:
    """Tests for schedule_density."""

    def test_single_game_returns_1(self):
        """A lone game in the schedule → density 1."""
        dates = [date(2025, 1, 15)]
        assert schedule_density(dates, 0) == 1

    def test_back_to_back_within_window(self):
        """2 games in 2 consecutive days → density 2."""
        dates = [date(2025, 1, 14), date(2025, 1, 15)]
        assert schedule_density(dates, 1) == 2

    def test_three_in_four_days(self):
        """3 games in 4 days → density 3."""
        dates = [date(2025, 1, 12), date(2025, 1, 14), date(2025, 1, 15)]
        assert schedule_density(dates, 2) == 3

    def test_game_outside_window_excluded(self):
        """A game 8+ days before is outside default 7-day window."""
        dates = [date(2025, 1, 5), date(2025, 1, 14), date(2025, 1, 15)]
        assert schedule_density(dates, 2) == 2

    def test_boundary_exactly_at_window_edge(self):
        """Game exactly window-1 (6) days before is counted (kills < vs <=)."""
        dates = [date(2025, 1, 9), date(2025, 1, 15)]
        assert schedule_density(dates, 1, window=7) == 2

    def test_first_game_always_1(self):
        """Index 0 always returns 1 regardless of window."""
        dates = [date(2025, 1, 15), date(2025, 1, 16)]
        assert schedule_density(dates, 0) == 1

    def test_window_zero_raises(self):
        """window=0 raises ValueError."""
        dates = [date(2025, 1, 15)]
        with pytest.raises(ValueError, match="window"):
            schedule_density(dates, 0, window=0)

    def test_negative_index_raises(self):
        """Negative game_index raises IndexError."""
        dates = [date(2025, 1, 15)]
        with pytest.raises(IndexError, match="game_index"):
            schedule_density(dates, -1)

    def test_empty_list_raises(self):
        """Empty game_dates with index 0 raises IndexError."""
        with pytest.raises(IndexError, match="game_index"):
            schedule_density([], 0)


class TestGetSeasonSchedule:
    """Tests for get_season_schedule async function."""

    def _build_response(self, mocker: MockerFixture, game_dates_data: list | None):
        """Build a mock API response with optional league_schedule."""
        response = mocker.MagicMock()
        if game_dates_data is None:
            response.league_schedule = None
        else:
            league_schedule = mocker.MagicMock()
            league_schedule.game_dates = game_dates_data
            response.league_schedule = league_schedule
        return response

    async def test_calls_api_once(self, mocker: MockerFixture):
        """client.get is called exactly once."""
        response = self._build_response(mocker, [])
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        await get_season_schedule(client)

        client.get.assert_awaited_once()

    async def test_uses_schedule_endpoint(self, mocker: MockerFixture):
        """The endpoint passed to client.get is ScheduleLeagueV2."""
        from fastbreak.endpoints import ScheduleLeagueV2

        response = self._build_response(mocker, [])
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        await get_season_schedule(client)

        endpoint = client.get.call_args[0][0]
        assert isinstance(endpoint, ScheduleLeagueV2)

    async def test_returns_all_games_sorted(self, mocker: MockerFixture):
        """Games from multiple dates are returned sorted by game_date_est."""
        game_late = _make_scheduled_game(
            "2025-02-01T00:00:00", home_team_id=1, away_team_id=2
        )
        game_early = _make_scheduled_game(
            "2025-01-10T00:00:00", home_team_id=3, away_team_id=4
        )

        gd1 = mocker.MagicMock()
        gd1.games = [game_late]
        gd2 = mocker.MagicMock()
        gd2.games = [game_early]

        response = self._build_response(mocker, [gd1, gd2])
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        result = await get_season_schedule(client)

        assert result == [game_early, game_late]

    async def test_empty_when_league_schedule_none(self, mocker: MockerFixture):
        """Returns [] when league_schedule is None."""
        response = self._build_response(mocker, None)
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        result = await get_season_schedule(client)

        assert result == []

    async def test_logs_warning_when_none(self, mocker: MockerFixture):
        """Logs a warning when league_schedule is None."""
        response = self._build_response(mocker, None)
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)
        mock_logger = mocker.patch("fastbreak.schedule.logger")

        await get_season_schedule(client)

        mock_logger.warning.assert_called_once()

    async def test_explicit_season_forwarded(self, mocker: MockerFixture):
        """An explicit season argument is forwarded to the endpoint."""
        response = self._build_response(mocker, [])
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)

        await get_season_schedule(client, season="2025-26")

        from fastbreak.endpoints import ScheduleLeagueV2

        endpoint = client.get.call_args[0][0]
        assert isinstance(endpoint, ScheduleLeagueV2)
        assert endpoint.season == "2025-26"

    async def test_season_defaults_to_current(self, mocker: MockerFixture):
        """When season=None, get_season_from_date() is used."""
        response = self._build_response(mocker, [])
        client = NBAClient(session=mocker.MagicMock())
        client.get = mocker.AsyncMock(return_value=response)
        mock_season = mocker.patch(
            "fastbreak.schedule.get_season_from_date", return_value="2025-26"
        )

        await get_season_schedule(client)

        mock_season.assert_called_once()
        from fastbreak.endpoints import ScheduleLeagueV2

        endpoint = client.get.call_args[0][0]
        assert isinstance(endpoint, ScheduleLeagueV2)
        assert endpoint.season == "2025-26"
