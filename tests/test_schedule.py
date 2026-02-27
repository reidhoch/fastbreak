"""Tests for schedule utilities."""

from __future__ import annotations

from datetime import date

from fastbreak.schedule import days_rest_before_game, is_back_to_back


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
