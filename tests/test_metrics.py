"""Tests for derived basketball metrics."""

import pytest

from fastbreak.metrics import (
    FourFactors,
    LeagueAverages,
    ast_pct,
    ast_to_tov,
    blk_pct,
    dreb_pct,
    effective_fg_pct,
    four_factors,
    free_throw_rate,
    game_score,
    is_double_double,
    is_triple_double,
    oreb_pct,
    pace_adjusted_per,
    per,
    per_100,
    per_36,
    pythagorean_win_pct,
    relative_efg,
    relative_ts,
    rolling_avg,
    stl_pct,
    three_point_rate,
    tov_pct,
    true_shooting,
    usage_pct,
)


class TestTrueShooting:
    """Tests for true_shooting()."""

    def test_typical_efficient_scorer(self) -> None:
        """TS% for a player with 28pts on 18 FGA and 6 FTA."""
        result = true_shooting(pts=28, fga=18, fta=6)
        assert result == pytest.approx(0.678, abs=0.001)

    def test_zero_attempts_returns_none(self) -> None:
        """Returns None when there are no field goal or free throw attempts."""
        assert true_shooting(pts=0, fga=0, fta=0) is None

    def test_only_free_throws_no_field_goals(self) -> None:
        """TS% is computable when a player only takes free throws."""
        # pts=8, fga=0, fta=10: 8 / (2 * 0.44*10) = 8 / 8.8 ≈ 0.909
        result = true_shooting(pts=8, fga=0, fta=10)
        assert result == pytest.approx(0.909, abs=0.001)

    def test_perfect_shooting(self) -> None:
        """TS% of 1.0 for perfect field goal shooting with no FTAs."""
        # pts=2, fga=1, fta=0: 2 / (2 * 1) = 1.0
        result = true_shooting(pts=2, fga=1, fta=0)
        assert result == pytest.approx(1.0)


class TestEffectiveFgPct:
    """Tests for effective_fg_pct()."""

    def test_mixed_two_and_three_pointers(self) -> None:
        """eFG% weights 3-pointers correctly."""
        # fgm=10, fg3m=4, fga=20: (10 + 0.5*4) / 20 = 12/20 = 0.6
        result = effective_fg_pct(fgm=10, fg3m=4, fga=20)
        assert result == pytest.approx(0.6)

    def test_no_three_pointers_equals_fg_pct(self) -> None:
        """eFG% equals FG% when no 3-pointers are attempted."""
        result = effective_fg_pct(fgm=8, fg3m=0, fga=16)
        assert result == pytest.approx(0.5)

    def test_zero_fga_returns_none(self) -> None:
        """Returns None when there are no field goal attempts."""
        assert effective_fg_pct(fgm=0, fg3m=0, fga=0) is None

    def test_all_threes_boosts_above_fg_pct(self) -> None:
        """eFG% exceeds raw FG% when all made FGs are 3-pointers."""
        # fgm=5, fg3m=5, fga=10: (5 + 2.5) / 10 = 0.75 vs FG% of 0.5
        result = effective_fg_pct(fgm=5, fg3m=5, fga=10)
        assert result == pytest.approx(0.75)


class TestFreeThrowRate:
    """Tests for free_throw_rate()."""

    def test_typical_line(self) -> None:
        """FTr for 6 FTA on 18 FGA."""
        result = free_throw_rate(fta=6, fga=18)
        assert result == pytest.approx(0.333, abs=0.001)

    def test_zero_fga_returns_none(self) -> None:
        """Returns None when there are no field goal attempts."""
        assert free_throw_rate(fta=4, fga=0) is None

    def test_no_free_throws(self) -> None:
        """FTr of 0.0 when no free throws are attempted."""
        result = free_throw_rate(fta=0, fga=15)
        assert result == pytest.approx(0.0)

    def test_high_ftr_aggressive_attacker(self) -> None:
        """FTr above 1.0 is valid for players who draw many fouls."""
        result = free_throw_rate(fta=12, fga=10)
        assert result == pytest.approx(1.2)


class TestThreePointRate:
    """Tests for three_point_rate()."""

    def test_half_attempts_from_three(self) -> None:
        """3PAr for 9 three-point attempts on 18 total FGA."""
        result = three_point_rate(fg3a=9, fga=18)
        assert result == pytest.approx(0.5)

    def test_zero_fga_returns_none(self) -> None:
        """Returns None when there are no field goal attempts."""
        assert three_point_rate(fg3a=0, fga=0) is None

    def test_no_three_point_attempts(self) -> None:
        """3PAr of 0.0 for a player who never attempts threes."""
        result = three_point_rate(fg3a=0, fga=12)
        assert result == pytest.approx(0.0)

    def test_all_attempts_from_three(self) -> None:
        """3PAr of 1.0 for a player who only attempts threes."""
        result = three_point_rate(fg3a=8, fga=8)
        assert result == pytest.approx(1.0)


class TestTovPct:
    """Tests for tov_pct() — share of possessions ending in a turnover."""

    def test_typical_team_line(self) -> None:
        """TOV% for 14 turnovers on 88 FGA / 20 FTA."""
        # 14 / (88 + 0.44*20 + 14) = 14 / 110.8 ≈ 0.1264
        result = tov_pct(fga=88, fta=20, tov=14)
        assert result == pytest.approx(0.1264, abs=0.001)

    def test_zero_turnovers_returns_zero(self) -> None:
        """Player/team with no turnovers has 0.0 TOV%, not None."""
        result = tov_pct(fga=15, fta=4, tov=0)
        assert result == pytest.approx(0.0)

    def test_zero_denominator_returns_none(self) -> None:
        """Returns None when there was no offensive activity at all."""
        assert tov_pct(fga=0, fta=0, tov=0) is None

    def test_all_turnovers_returns_one(self) -> None:
        """If every possession ends in a turnover (fga=0, fta=0), TOV%=1.0."""
        result = tov_pct(fga=0, fta=0, tov=10)
        assert result == pytest.approx(1.0)

    def test_high_tov_player_exceeds_point_two(self) -> None:
        """A ball-handler with 5 TOV on 12 FGA / 3 FTA has a high TOV%."""
        # 5 / (12 + 1.32 + 5) = 5 / 18.32 ≈ 0.273
        result = tov_pct(fga=12, fta=3, tov=5)
        assert result == pytest.approx(0.273, abs=0.001)


class TestFourFactors:
    """Tests for four_factors() — Dean Oliver's Four Factors as a typed result."""

    # Shared inputs used across most tests
    _FGM, _FG3M, _FGA = 40, 12, 88
    _TOV, _FTA = 14, 20
    _OREB, _OPP_DREB = 10, 32

    def _call(self, **overrides: float) -> FourFactors:
        kwargs: dict[str, float] = dict(
            fgm=self._FGM,
            fg3m=self._FG3M,
            fga=self._FGA,
            tov=self._TOV,
            fta=self._FTA,
            oreb=self._OREB,
            opp_dreb=self._OPP_DREB,
        )
        kwargs.update(overrides)
        return four_factors(**kwargs)

    def test_efg_pct_correct(self) -> None:
        """eFG% = (FGM + 0.5*FG3M) / FGA."""
        # (40 + 0.5*12) / 88 = 46/88 ≈ 0.5227
        result = self._call()
        assert result.efg_pct == pytest.approx(0.5227, abs=0.001)

    def test_tov_pct_correct(self) -> None:
        """TOV% = TOV / (FGA + 0.44*FTA + TOV)."""
        # 14 / (88 + 8.8 + 14) = 14/110.8 ≈ 0.1264
        result = self._call()
        assert result.tov_pct == pytest.approx(0.1264, abs=0.001)

    def test_oreb_pct_correct(self) -> None:
        """Team OREB% = OREB / (OREB + opp_DREB)."""
        # 10 / (10 + 32) = 10/42 ≈ 0.2381
        result = self._call()
        assert result.oreb_pct == pytest.approx(0.2381, abs=0.001)

    def test_ftr_correct(self) -> None:
        """FTr = FTA / FGA."""
        # 20 / 88 ≈ 0.2273
        result = self._call()
        assert result.ftr == pytest.approx(0.2273, abs=0.001)

    def test_zero_fga_gives_none_for_efg_ftr_and_tov(self) -> None:
        """When FGA=0 and TOV=0, eFG%, FTr, and TOV% are all None."""
        result = self._call(fga=0, fta=0, tov=0)
        assert result.efg_pct is None
        assert result.ftr is None
        assert result.tov_pct is None

    def test_zero_rebounds_available_gives_none_for_oreb(self) -> None:
        """When both OREB and opp_DREB are zero, oreb_pct is None."""
        result = self._call(oreb=0, opp_dreb=0)
        assert result.oreb_pct is None

    def test_result_is_frozen(self) -> None:
        """FourFactors is immutable — attribute assignment raises."""
        result = self._call()
        with pytest.raises(AttributeError):
            result.efg_pct = 0.5  # type: ignore[misc]


class TestAstToTov:
    """Tests for ast_to_tov()."""

    def test_typical_playmaker(self) -> None:
        """AST/TOV ratio for 10 assists and 2 turnovers."""
        result = ast_to_tov(ast=10, tov=2)
        assert result == pytest.approx(5.0)

    def test_zero_turnovers_returns_none(self) -> None:
        """Returns None when turnovers are zero to avoid division by zero."""
        assert ast_to_tov(ast=8, tov=0) is None

    def test_zero_assists_zero_turnovers_returns_none(self) -> None:
        """Returns None when both are zero."""
        assert ast_to_tov(ast=0, tov=0) is None

    def test_below_one_is_poor_ratio(self) -> None:
        """AST/TOV below 1.0 for fewer assists than turnovers."""
        result = ast_to_tov(ast=3, tov=5)
        assert result == pytest.approx(0.6)


class TestGameScore:
    """Tests for game_score() — Hollinger's single-game efficiency metric."""

    def test_typical_all_around_line(self) -> None:
        """Game score for a solid all-around performance."""
        # pts=28, fgm=11, fga=19, ftm=7, fta=9,
        # oreb=1, dreb=8, stl=2, ast=8, blk=1, pf=3, tov=4
        result = game_score(
            pts=28,
            fgm=11,
            fga=19,
            ftm=7,
            fta=9,
            oreb=1,
            dreb=8,
            stl=2,
            ast=8,
            blk=1,
            pf=3,
            tov=4,
        )
        assert result == pytest.approx(24.5, abs=0.01)

    def test_scoreless_goose_egg(self) -> None:
        """Game score of 0.0 for a statless game."""
        result = game_score(
            pts=0,
            fgm=0,
            fga=0,
            ftm=0,
            fta=0,
            oreb=0,
            dreb=0,
            stl=0,
            ast=0,
            blk=0,
            pf=0,
            tov=0,
        )
        assert result == pytest.approx(0.0)

    def test_poor_shooting_line_is_negative(self) -> None:
        """Game score for an 0-12 shooting night is exactly -10.3."""
        # pts=2, fgm=0, fga=12, ftm=2, fta=2, oreb=0, dreb=2, stl=0, ast=1, blk=0, pf=3, tov=4
        # = 2 + 0 - 8.4 - 0 + 0 + 0.6 + 0 + 0.7 + 0 - 1.2 - 4 = -10.3
        result = game_score(
            pts=2,
            fgm=0,
            fga=12,
            ftm=2,
            fta=2,
            oreb=0,
            dreb=2,
            stl=0,
            ast=1,
            blk=0,
            pf=3,
            tov=4,
        )
        assert result == pytest.approx(-10.3)

    def test_dominant_scoring_line(self) -> None:
        """High-scoring efficient game produces exactly 37.0."""
        # 50pts, 20-30 FG, 10-10 FT, no other stats
        # = 50 + 8 - 21 - 0 = 37.0
        result = game_score(
            pts=50,
            fgm=20,
            fga=30,
            ftm=10,
            fta=10,
            oreb=0,
            dreb=0,
            stl=0,
            ast=0,
            blk=0,
            pf=0,
            tov=0,
        )
        assert result == pytest.approx(37.0)

    def test_mid_range_all_around_line(self) -> None:
        """Coefficient-level regression: solid all-around line computes exactly 15.5."""
        # pts=20, fgm=8, fga=16, ftm=4, fta=5, oreb=2, dreb=6, stl=1, ast=4, blk=1, pf=2, tov=3
        # = 20 + 3.2 - 11.2 - 0.4 + 1.4 + 1.8 + 1 + 2.8 + 0.7 - 0.8 - 3 = 15.5
        result = game_score(
            pts=20,
            fgm=8,
            fga=16,
            ftm=4,
            fta=5,
            oreb=2,
            dreb=6,
            stl=1,
            ast=4,
            blk=1,
            pf=2,
            tov=3,
        )
        assert result == pytest.approx(15.5)


class TestPer36:
    """Tests for per_36() normalization."""

    def test_normalizes_stat_to_36_minutes(self) -> None:
        """Scales 10 assists in 30 minutes to 12 per 36."""
        result = per_36(stat=10, minutes=30)
        assert result == pytest.approx(12.0)

    def test_zero_minutes_returns_none(self) -> None:
        """Returns None when minutes played is zero."""
        assert per_36(stat=10, minutes=0) is None

    def test_already_at_36_minutes_unchanged(self) -> None:
        """Stat is unchanged when minutes equal 36."""
        result = per_36(stat=15, minutes=36)
        assert result == pytest.approx(15.0)

    def test_zero_stat_returns_zero(self) -> None:
        """Returns 0.0 for a zero stat regardless of minutes."""
        result = per_36(stat=0, minutes=25)
        assert result == pytest.approx(0.0)


class TestPer100:
    """Tests for per_100() — normalize a counting stat to per-100-possessions."""

    def test_stat_at_100_possessions_is_unchanged(self) -> None:
        """A stat over exactly 100 possessions normalizes to itself."""
        result = per_100(stat=10, poss=100)
        assert result == pytest.approx(10.0)

    def test_scales_below_100_possessions_up(self) -> None:
        """25 points over 96.4 possessions scales above 25."""
        # 25 * 100 / 96.4 ≈ 25.934
        result = per_100(stat=25, poss=96.4)
        assert result == pytest.approx(25.934, abs=0.001)

    def test_zero_possessions_returns_none(self) -> None:
        """Returns None when possessions are zero."""
        assert per_100(stat=10, poss=0) is None

    def test_zero_stat_returns_zero(self) -> None:
        """Zero stat over any possessions is 0.0."""
        result = per_100(stat=0, poss=95)
        assert result == pytest.approx(0.0)

    def test_twice_the_possessions_halves_the_rate(self) -> None:
        """Doubling possessions halves the per-100 rate."""
        r1 = per_100(stat=20, poss=50)
        r2 = per_100(stat=20, poss=100)
        assert r1 is not None and r2 is not None
        assert r1 == pytest.approx(r2 * 2)


class TestPythagoreanWinPct:
    """Tests for pythagorean_win_pct() — expected win% from point differential."""

    def test_equal_scoring_is_dot_five(self) -> None:
        """A team that scores and allows equal points expects exactly 0.5."""
        result = pythagorean_win_pct(pts=110.0, opp_pts=110.0)
        assert result == pytest.approx(0.5)

    def test_better_offense_above_dot_five(self) -> None:
        """A team scoring more than it allows expects a win% above 0.5."""
        result = pythagorean_win_pct(pts=115.0, opp_pts=110.0)
        assert result is not None
        assert result > 0.5

    def test_known_value_with_default_exponent(self) -> None:
        """115 pts vs 110 pts with e=13.91 produces approx 0.650."""
        result = pythagorean_win_pct(pts=115.0, opp_pts=110.0)
        assert result == pytest.approx(0.650, abs=0.001)

    def test_custom_exponent_changes_result(self) -> None:
        """Passing exp=2 (original Pythagorean) produces a different result."""
        default = pythagorean_win_pct(pts=115.0, opp_pts=110.0)
        original = pythagorean_win_pct(pts=115.0, opp_pts=110.0, exp=2.0)
        assert default is not None and original is not None
        assert default != pytest.approx(original)

    def test_dominant_team_approaches_one(self) -> None:
        """A team scoring far more than it allows expects nearly 1.0."""
        result = pythagorean_win_pct(pts=130.0, opp_pts=90.0)
        assert result is not None
        assert result > 0.99

    def test_zero_pts_scored_returns_zero(self) -> None:
        """A team that scores nothing expects 0.0 win%."""
        result = pythagorean_win_pct(pts=0.0, opp_pts=100.0)
        assert result == pytest.approx(0.0)

    def test_both_zero_returns_none(self) -> None:
        """Returns None when both teams score 0 (degenerate / no-data case)."""
        assert pythagorean_win_pct(pts=0.0, opp_pts=0.0) is None


class TestIsDoubleDouble:
    """Tests for is_double_double()."""

    def test_points_and_rebounds(self) -> None:
        """20pts and 10reb is a double-double."""
        assert is_double_double(pts=20, reb=10, ast=5, stl=1, blk=0) is True

    def test_points_and_assists(self) -> None:
        """25pts and 11ast is a double-double."""
        assert is_double_double(pts=25, reb=3, ast=11, stl=2, blk=0) is True

    def test_only_one_category_at_ten(self) -> None:
        """Only reaching 10 in one category is not a double-double."""
        assert is_double_double(pts=10, reb=9, ast=5, stl=1, blk=0) is False

    def test_blocks_and_steals_count(self) -> None:
        """10blk and 10stl qualifies, though rare."""
        assert is_double_double(pts=5, reb=4, ast=0, stl=10, blk=10) is True

    def test_triple_double_also_qualifies(self) -> None:
        """A triple-double is also a double-double."""
        assert is_double_double(pts=10, reb=10, ast=10, stl=1, blk=0) is True

    def test_both_categories_at_exactly_ten(self) -> None:
        """Exactly 10 in exactly two categories is a double-double (boundary value)."""
        assert is_double_double(pts=10, reb=10, ast=9, stl=0, blk=0) is True


class TestIsTripleDouble:
    """Tests for is_triple_double()."""

    def test_classic_points_rebounds_assists(self) -> None:
        """20pts, 10reb, 10ast is a triple-double."""
        assert is_triple_double(pts=20, reb=10, ast=10, stl=1, blk=0) is True

    def test_only_two_categories(self) -> None:
        """20pts and 10reb without a third category at 10 is not a triple-double."""
        assert is_triple_double(pts=20, reb=10, ast=9, stl=2, blk=0) is False

    def test_requires_exactly_three_at_ten(self) -> None:
        """Exactly three categories at 10+ qualifies."""
        assert is_triple_double(pts=10, reb=10, ast=10, stl=0, blk=0) is True

    def test_five_categories_at_ten_qualifies(self) -> None:
        """Five-by-five (rare) also qualifies as a triple-double."""
        assert is_triple_double(pts=10, reb=10, ast=10, stl=10, blk=10) is True

    def test_nothing_at_ten(self) -> None:
        """No categories at 10 is not a triple-double."""
        assert is_triple_double(pts=9, reb=9, ast=9, stl=2, blk=1) is False

    def test_all_three_categories_at_exactly_ten(self) -> None:
        """Exactly 10 in exactly three categories is a triple-double (boundary value)."""
        assert is_triple_double(pts=10, reb=10, ast=10, stl=9, blk=0) is True


class TestUsagePct:
    """Tests for usage_pct() — player's share of team possessions while on floor."""

    def test_typical_high_usage_player(self) -> None:
        """Usage% for a player with 18 FGA, 6 FTA, 4 TOV in 30 min (team: 80/20/15 in 240 min)."""
        # player_poss = 18 + 0.44*6 + 4 = 24.64
        # team_poss  = 80 + 0.44*20 + 15 = 103.8
        # result = 24.64 * 48 / (30 * 103.8) = 0.3798
        result = usage_pct(
            fga=18,
            fta=6,
            tov=4,
            mp=30,
            team_fga=80,
            team_fta=20,
            team_tov=15,
            team_mp=240,
        )
        assert result == pytest.approx(0.3798, abs=0.001)

    def test_zero_player_minutes_returns_none(self) -> None:
        """Returns None when the player played zero minutes."""
        assert (
            usage_pct(
                fga=18,
                fta=6,
                tov=4,
                mp=0,
                team_fga=80,
                team_fta=20,
                team_tov=15,
                team_mp=240,
            )
            is None
        )

    def test_zero_team_possessions_returns_none(self) -> None:
        """Returns None when the team recorded no possessions."""
        assert (
            usage_pct(
                fga=0,
                fta=0,
                tov=0,
                mp=30,
                team_fga=0,
                team_fta=0,
                team_tov=0,
                team_mp=240,
            )
            is None
        )

    def test_zero_player_production_returns_zero(self) -> None:
        """Player who attempted nothing has 0.0 usage, not None."""
        result = usage_pct(
            fga=0,
            fta=0,
            tov=0,
            mp=30,
            team_fga=80,
            team_fta=20,
            team_tov=15,
            team_mp=240,
        )
        assert result == pytest.approx(0.0)

    def test_zero_team_mp_returns_zero(self) -> None:
        """team_mp=0 zeros the numerator, returning 0.0 (not None)."""
        # Numerator = player_poss * (0/5) = 0; denominator = mp*team_poss (non-zero).
        result = usage_pct(
            fga=18,
            fta=6,
            tov=4,
            mp=30,
            team_fga=80,
            team_fta=20,
            team_tov=15,
            team_mp=0,
        )
        assert result == pytest.approx(0.0)


class TestAstPct:
    """Tests for ast_pct() — share of teammate field goals a player assisted."""

    def test_typical_playmaking_guard(self) -> None:
        """AST% for 10 assists, 8 FGM, 36 min (team: 42 FGM in 240 min)."""
        # denominator = (36/48)*42 - 8 = 31.5 - 8 = 23.5
        # result = 10 / 23.5 = 0.4255
        result = ast_pct(ast=10, fgm=8, mp=36, team_fgm=42, team_mp=240)
        assert result == pytest.approx(0.4255, abs=0.001)

    def test_zero_assists_returns_zero(self) -> None:
        """Player with no assists has 0.0 AST%, not None."""
        result = ast_pct(ast=0, fgm=10, mp=36, team_fgm=42, team_mp=240)
        assert result == pytest.approx(0.0)

    def test_zero_player_minutes_returns_none(self) -> None:
        """Returns None when the player played zero minutes."""
        assert ast_pct(ast=5, fgm=8, mp=0, team_fgm=42, team_mp=240) is None

    def test_zero_team_minutes_returns_none(self) -> None:
        """Returns None when team minutes are zero (avoids divide-by-zero)."""
        assert ast_pct(ast=5, fgm=8, mp=36, team_fgm=42, team_mp=0) is None

    def test_non_positive_denominator_returns_none(self) -> None:
        """Returns None when computed denominator is zero or negative."""
        # Degenerate case: player made more FGs than team could have had while on floor
        assert ast_pct(ast=5, fgm=50, mp=36, team_fgm=5, team_mp=240) is None


class TestOrebPct:
    """Tests for oreb_pct() — player's share of available offensive rebounds."""

    def test_typical_offensive_rebounder(self) -> None:
        """OREB% for 3 offensive rebounds, 35 min (team: 12 OREB; opp: 28 DREB)."""
        # available = 12 + 28 = 40
        # result = 3 * 48 / (35 * 40) = 144 / 1400 = 0.1029
        result = oreb_pct(oreb=3, mp=35, team_oreb=12, opp_dreb=28, team_mp=240)
        assert result == pytest.approx(0.1029, abs=0.001)

    def test_zero_player_minutes_returns_none(self) -> None:
        """Returns None when the player played zero minutes."""
        assert oreb_pct(oreb=3, mp=0, team_oreb=12, opp_dreb=28, team_mp=240) is None

    def test_zero_available_rebounds_returns_none(self) -> None:
        """Returns None when no offensive rebounds were available."""
        assert oreb_pct(oreb=0, mp=35, team_oreb=0, opp_dreb=0, team_mp=240) is None

    def test_zero_player_orebs_returns_zero(self) -> None:
        """Player who grabbed no offensive rebounds has 0.0, not None."""
        result = oreb_pct(oreb=0, mp=35, team_oreb=12, opp_dreb=28, team_mp=240)
        assert result == pytest.approx(0.0)


class TestDrebPct:
    """Tests for dreb_pct() — player's share of available defensive rebounds."""

    def test_typical_defensive_rebounder(self) -> None:
        """DREB% for 8 defensive rebounds, 35 min (team: 32 DREB; opp: 10 OREB)."""
        # available = 32 + 10 = 42
        # result = 8 * 48 / (35 * 42) = 384 / 1470 = 0.2612
        result = dreb_pct(dreb=8, mp=35, team_dreb=32, opp_oreb=10, team_mp=240)
        assert result == pytest.approx(0.2612, abs=0.001)

    def test_zero_player_minutes_returns_none(self) -> None:
        """Returns None when the player played zero minutes."""
        assert dreb_pct(dreb=8, mp=0, team_dreb=32, opp_oreb=10, team_mp=240) is None

    def test_zero_available_rebounds_returns_none(self) -> None:
        """Returns None when no defensive rebounds were available."""
        assert dreb_pct(dreb=0, mp=35, team_dreb=0, opp_oreb=0, team_mp=240) is None

    def test_zero_player_drebs_returns_zero(self) -> None:
        """Player who grabbed no defensive rebounds has 0.0, not None."""
        result = dreb_pct(dreb=0, mp=35, team_dreb=32, opp_oreb=10, team_mp=240)
        assert result == pytest.approx(0.0)


class TestStlPct:
    """Tests for stl_pct() — player's share of opponent possessions ending in a steal."""

    def test_typical_perimeter_defender(self) -> None:
        """STL% for 2 steals in 35 min against 100 opponent possessions."""
        # result = 2 * 48 / (35 * 100) = 96 / 3500 = 0.02743
        result = stl_pct(stl=2, mp=35, team_mp=240, opp_poss=100)
        assert result == pytest.approx(0.02743, abs=0.0001)

    def test_zero_player_minutes_returns_none(self) -> None:
        """Returns None when the player played zero minutes."""
        assert stl_pct(stl=2, mp=0, team_mp=240, opp_poss=100) is None

    def test_zero_opponent_possessions_returns_none(self) -> None:
        """Returns None when opponent possessions are zero."""
        assert stl_pct(stl=2, mp=35, team_mp=240, opp_poss=0) is None

    def test_zero_steals_returns_zero(self) -> None:
        """Player with no steals has 0.0 STL%, not None."""
        result = stl_pct(stl=0, mp=35, team_mp=240, opp_poss=100)
        assert result == pytest.approx(0.0)


class TestBlkPct:
    """Tests for blk_pct() — player's share of opponent 2-point attempts blocked."""

    def test_typical_rim_protector(self) -> None:
        """BLK% for 2 blocks in 35 min against 60 opponent 2-point FGA."""
        # result = 2 * 48 / (35 * 60) = 96 / 2100 = 0.04571
        result = blk_pct(blk=2, mp=35, team_mp=240, opp_fg2a=60)
        assert result == pytest.approx(0.04571, abs=0.0001)

    def test_zero_player_minutes_returns_none(self) -> None:
        """Returns None when the player played zero minutes."""
        assert blk_pct(blk=2, mp=0, team_mp=240, opp_fg2a=60) is None

    def test_zero_opponent_two_point_attempts_returns_none(self) -> None:
        """Returns None when opponent had no 2-point attempts."""
        assert blk_pct(blk=2, mp=35, team_mp=240, opp_fg2a=0) is None

    def test_zero_blocks_returns_zero(self) -> None:
        """Player with no blocks has 0.0 BLK%, not None."""
        result = blk_pct(blk=0, mp=35, team_mp=240, opp_fg2a=60)
        assert result == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# League-average fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_league() -> LeagueAverages:
    """Simplified league averages for deterministic unit tests.

    Derived lg_pace = 85 - 10 + 12 + 0.44*20 = 95.8.
    Tests that need a pace ratio of exactly 1.0 should pass team_pace=95.8.
    """
    return LeagueAverages(
        lg_pts=100.0,
        lg_fga=85.0,
        lg_fta=20.0,
        lg_ftm=15.0,
        lg_oreb=10.0,
        lg_treb=40.0,
        lg_ast=24.0,
        lg_fgm=40.0,
        lg_fg3m=10.0,
        lg_tov=12.0,
        lg_pf=18.0,
    )


class TestLeagueAveragesValidation:
    """Tests that LeagueAverages rejects invalid construction arguments."""

    def _valid_kwargs(self) -> dict[str, float]:
        return dict(
            lg_pts=100.0,
            lg_fga=85.0,
            lg_fta=20.0,
            lg_ftm=15.0,
            lg_oreb=10.0,
            lg_treb=40.0,
            lg_ast=24.0,
            lg_fgm=40.0,
            lg_fg3m=10.0,
            lg_tov=12.0,
            lg_pf=18.0,
        )

    def test_negative_field_raises_value_error(self) -> None:
        """A negative field value raises ValueError at construction time."""
        kw = self._valid_kwargs()
        kw["lg_fga"] = -1.0
        with pytest.raises(ValueError, match="lg_fga"):
            LeagueAverages(**kw)

    def test_zero_lg_fga_raises_value_error(self) -> None:
        """lg_fga=0 raises ValueError because it is a denominator in efg and ts."""
        kw = self._valid_kwargs()
        kw["lg_fga"] = 0.0
        with pytest.raises(ValueError, match="lg_fga"):
            LeagueAverages(**kw)

    def test_zero_lg_treb_raises_value_error(self) -> None:
        """lg_treb=0 raises ValueError because it is the denominator in drb_pct."""
        kw = self._valid_kwargs()
        kw["lg_treb"] = 0.0
        with pytest.raises(ValueError, match="lg_treb"):
            LeagueAverages(**kw)

    def test_zero_lg_fgm_raises_value_error(self) -> None:
        """lg_fgm=0 raises ValueError because it appears in the factor denominator."""
        kw = self._valid_kwargs()
        kw["lg_fgm"] = 0.0
        with pytest.raises(ValueError, match="lg_fgm"):
            LeagueAverages(**kw)

    def test_zero_lg_ftm_raises_value_error(self) -> None:
        """lg_ftm=0 raises ValueError because it appears in the factor denominator."""
        kw = self._valid_kwargs()
        kw["lg_ftm"] = 0.0
        with pytest.raises(ValueError, match="lg_ftm"):
            LeagueAverages(**kw)

    def test_zero_lg_pf_raises_value_error(self) -> None:
        """lg_pf=0 raises ValueError because it is a denominator in pace_adjusted_per."""
        kw = self._valid_kwargs()
        kw["lg_pf"] = 0.0
        with pytest.raises(ValueError, match="lg_pf"):
            LeagueAverages(**kw)

    def test_zero_vop_denominator_raises_value_error(self) -> None:
        """lg_oreb==lg_fga collapses the vop denominator to zero."""
        kw = self._valid_kwargs()
        # Keep lg_oreb <= lg_treb (40) to avoid the cross-field guard.
        # lg_fga - lg_oreb + lg_tov + 0.44*lg_fta = 40 - 40 + 0 + 0 = 0
        kw["lg_fga"] = 40.0
        kw["lg_oreb"] = 40.0
        kw["lg_tov"] = 0.0
        kw["lg_fta"] = 0.0
        with pytest.raises(ValueError, match="vop"):
            LeagueAverages(**kw)

    def test_lg_oreb_exceeding_lg_treb_raises_value_error(self) -> None:
        """lg_oreb > lg_treb is physically impossible and raises ValueError."""
        kw = self._valid_kwargs()
        kw["lg_oreb"] = kw["lg_treb"] + 1.0  # 41.0 > 40.0
        with pytest.raises(ValueError, match="lg_oreb"):
            LeagueAverages(**kw)


class TestLeagueAverages:
    """Tests for LeagueAverages derived properties."""

    def test_vop(self, sample_league: LeagueAverages) -> None:
        """VOP = lg_pts / (lg_fga - lg_oreb + lg_tov + 0.44*lg_fta)."""
        # 100 / (85 - 10 + 12 + 8.8) = 100 / 95.8
        assert sample_league.vop == pytest.approx(1.04384, abs=0.0001)

    def test_drb_pct(self, sample_league: LeagueAverages) -> None:
        """DRB% = (lg_treb - lg_oreb) / lg_treb."""
        assert sample_league.drb_pct == pytest.approx(0.75)

    def test_ts(self, sample_league: LeagueAverages) -> None:
        """League TS% = lg_pts / (2 * (lg_fga + 0.44*lg_fta))."""
        # 100 / (2 * 93.8) = 100 / 187.6
        assert sample_league.ts == pytest.approx(0.5331, abs=0.0001)

    def test_efg(self, sample_league: LeagueAverages) -> None:
        """League eFG% = (lg_fgm + 0.5*lg_fg3m) / lg_fga."""
        # (40 + 5) / 85 = 45/85
        assert sample_league.efg == pytest.approx(0.5294, abs=0.0001)

    def test_factor(self, sample_league: LeagueAverages) -> None:
        """factor = 2/3 - (0.5*(lg_ast/lg_fgm)) / (2*(lg_fgm/lg_ftm))."""
        # 2/3 - (0.5*0.6) / (2*2.6667) = 0.6667 - 0.3/5.3333
        assert sample_league.factor == pytest.approx(0.6104, abs=0.0001)

    def test_factor_cross_check_with_transparent_arithmetic(self) -> None:
        """factor = 2/3 - 1/8 = 13/24 when lg_ast==lg_fgm and lg_fgm==2*lg_ftm."""
        # lg_ast=40, lg_fgm=40, lg_ftm=20:
        # factor = 2/3 - (0.5*1)/(2*2) = 2/3 - 1/8 = 16/24 - 3/24 = 13/24
        lg = LeagueAverages(
            lg_pts=100.0,
            lg_fga=85.0,
            lg_fta=20.0,
            lg_ftm=20.0,
            lg_oreb=10.0,
            lg_treb=40.0,
            lg_ast=40.0,
            lg_fgm=40.0,
            lg_fg3m=10.0,
            lg_tov=12.0,
            lg_pf=18.0,
        )
        assert lg.factor == pytest.approx(13 / 24)


class TestPaceAdjustedPer:
    """Tests for pace_adjusted_per() — PER before league normalization."""

    def test_typical_starter_line(self, sample_league: LeagueAverages) -> None:
        """aPER for a solid starter (20pts/8reb/5ast/35min) is in a reasonable range."""
        # team_pace == sample_league.lg_pace (95.8) so pace ratio = 1.0 exactly.
        # Pre-computed expected value: 0.5159
        result = pace_adjusted_per(
            fgm=8,
            fga=15,
            fg3m=2,
            ftm=4,
            fta=5,
            oreb=2,
            treb=8,
            ast=5,
            stl=1,
            blk=1,
            pf=3,
            tov=2,
            mp=35,
            team_ast=25,
            team_fgm=42,
            team_pace=95.8,
            lg=sample_league,
        )
        assert result == pytest.approx(0.5159, abs=0.001)

    def test_zero_player_minutes_returns_none(
        self, sample_league: LeagueAverages
    ) -> None:
        """Returns None when the player played zero minutes."""
        assert (
            pace_adjusted_per(
                fgm=8,
                fga=15,
                fg3m=2,
                ftm=4,
                fta=5,
                oreb=2,
                treb=8,
                ast=5,
                stl=1,
                blk=1,
                pf=3,
                tov=2,
                mp=0,
                team_ast=25,
                team_fgm=42,
                team_pace=100.0,
                lg=sample_league,
            )
            is None
        )

    def test_zero_team_fgm_returns_none(self, sample_league: LeagueAverages) -> None:
        """Returns None when team FGM is zero (avoids divide-by-zero in factor terms)."""
        assert (
            pace_adjusted_per(
                fgm=8,
                fga=15,
                fg3m=2,
                ftm=4,
                fta=5,
                oreb=2,
                treb=8,
                ast=5,
                stl=1,
                blk=1,
                pf=3,
                tov=2,
                mp=35,
                team_ast=25,
                team_fgm=0,
                team_pace=100.0,
                lg=sample_league,
            )
            is None
        )

    def test_zero_team_pace_returns_none(self, sample_league: LeagueAverages) -> None:
        """Returns None when team pace is zero (avoids divide-by-zero in pace ratio)."""
        assert (
            pace_adjusted_per(
                fgm=8,
                fga=15,
                fg3m=2,
                ftm=4,
                fta=5,
                oreb=2,
                treb=8,
                ast=5,
                stl=1,
                blk=1,
                pf=3,
                tov=2,
                mp=35,
                team_ast=25,
                team_fgm=42,
                team_pace=0.0,
                lg=sample_league,
            )
            is None
        )

    def test_three_pointer_only_line_exact_value(
        self, sample_league: LeagueAverages
    ) -> None:
        """5 three-pointers made, all other stats zero → aPER = 5.0 exactly."""
        # With team_ast=0, factor * team_ast/team_fgm = 0, so fg3m term = fg3m * 1.
        # uper = (1/1) * 5 = 5; team_pace == lg_pace (95.8) so pace ratio = 1 → result = 5.0.
        result = pace_adjusted_per(
            fgm=0,
            fga=0,
            fg3m=5,
            ftm=0,
            fta=0,
            oreb=0,
            treb=0,
            ast=0,
            stl=0,
            blk=0,
            pf=0,
            tov=0,
            mp=1,
            team_ast=0,
            team_fgm=10,
            team_pace=95.8,
            lg=sample_league,
        )
        assert result == pytest.approx(5.0)

    def test_faster_pace_boosts_per(self, sample_league: LeagueAverages) -> None:
        """Slower team pace reduces aPER; faster pace boosts it (pace adjustment)."""
        slow_team = pace_adjusted_per(
            fgm=8,
            fga=15,
            fg3m=2,
            ftm=4,
            fta=5,
            oreb=2,
            treb=8,
            ast=5,
            stl=1,
            blk=1,
            pf=3,
            tov=2,
            mp=35,
            team_ast=25,
            team_fgm=42,
            team_pace=110.0,
            lg=sample_league,
        )
        fast_team = pace_adjusted_per(
            fgm=8,
            fga=15,
            fg3m=2,
            ftm=4,
            fta=5,
            oreb=2,
            treb=8,
            ast=5,
            stl=1,
            blk=1,
            pf=3,
            tov=2,
            mp=35,
            team_ast=25,
            team_fgm=42,
            team_pace=90.0,
            lg=sample_league,
        )
        assert fast_team is not None and slow_team is not None
        assert fast_team > slow_team


class TestPer:
    """Tests for per() — normalizes aPER to league average of 15.0."""

    def test_league_average_player_gets_fifteen(self) -> None:
        """A player whose aPER equals the league average gets exactly PER 15.0."""
        assert per(aper=0.516, lg_aper=0.516) == pytest.approx(15.0)

    def test_above_average_player_exceeds_fifteen(self) -> None:
        """aPER 50% above league average yields PER of 22.5."""
        result = per(aper=0.774, lg_aper=0.516)
        assert result == pytest.approx(22.5, abs=0.01)

    def test_zero_lg_aper_returns_none(self) -> None:
        """Returns None when league average aPER is zero (avoids divide-by-zero)."""
        assert per(aper=0.516, lg_aper=0.0) is None

    def test_zero_aper_returns_zero(self) -> None:
        """A player with zero aPER gets PER of 0.0."""
        assert per(aper=0.0, lg_aper=0.516) == pytest.approx(0.0)


class TestRelativeTs:
    """Tests for relative_ts() — player TS% minus league average."""

    def test_above_average_shooter_is_positive(
        self, sample_league: LeagueAverages
    ) -> None:
        """Player TS% above league average returns positive value."""
        result = relative_ts(player_ts=0.60, lg=sample_league)
        assert result == pytest.approx(0.60 - sample_league.ts, abs=0.0001)
        assert result > 0

    def test_below_average_shooter_is_negative(
        self, sample_league: LeagueAverages
    ) -> None:
        """Player TS% below league average returns negative value."""
        result = relative_ts(player_ts=0.48, lg=sample_league)
        assert result == pytest.approx(0.48 - sample_league.ts, abs=0.0001)
        assert result < 0

    def test_league_average_shooter_returns_zero(
        self, sample_league: LeagueAverages
    ) -> None:
        """Player TS% equal to league average returns exactly 0.0."""
        assert relative_ts(
            player_ts=sample_league.ts, lg=sample_league
        ) == pytest.approx(0.0)

    def test_none_player_ts_returns_none(self, sample_league: LeagueAverages) -> None:
        """Returns None when player TS% is None (player had no attempts)."""
        assert relative_ts(player_ts=None, lg=sample_league) is None


class TestRelativeEfg:
    """Tests for relative_efg() — player eFG% minus league average."""

    def test_above_average_shooter_is_positive(
        self, sample_league: LeagueAverages
    ) -> None:
        """Player eFG% above league average returns positive value."""
        result = relative_efg(player_efg=0.58, lg=sample_league)
        assert result == pytest.approx(0.58 - sample_league.efg, abs=0.0001)
        assert result > 0

    def test_below_average_shooter_is_negative(
        self, sample_league: LeagueAverages
    ) -> None:
        """Player eFG% below league average returns negative value."""
        result = relative_efg(player_efg=0.46, lg=sample_league)
        assert result == pytest.approx(0.46 - sample_league.efg, abs=0.0001)
        assert result < 0

    def test_league_average_shooter_returns_zero(
        self, sample_league: LeagueAverages
    ) -> None:
        """Player eFG% equal to league average returns exactly 0.0."""
        assert relative_efg(
            player_efg=sample_league.efg, lg=sample_league
        ) == pytest.approx(0.0)

    def test_none_player_efg_returns_none(self, sample_league: LeagueAverages) -> None:
        """Returns None when player eFG% is None (player had no attempts)."""
        assert relative_efg(player_efg=None, lg=sample_league) is None


class TestOrtgDrtg:
    def test_ortg_basic(self):
        from fastbreak.metrics import ortg  # noqa: PLC0415

        result = ortg(pts=110, fga=90, oreb=10, tov=15, fta=20)
        assert result is not None
        poss = 90 - 10 + 15 + 0.44 * 20
        assert abs(result - 110 / poss * 100) < 0.01

    def test_ortg_zero_possessions_returns_none(self):
        from fastbreak.metrics import ortg  # noqa: PLC0415

        assert ortg(pts=0, fga=0, oreb=0, tov=0, fta=0) is None

    def test_drtg_basic(self):
        from fastbreak.metrics import drtg  # noqa: PLC0415

        result = drtg(opp_pts=105, opp_fga=88, opp_oreb=9, opp_tov=13, opp_fta=18)
        assert result is not None
        poss = 88 - 9 + 13 + 0.44 * 18
        assert abs(result - 105 / poss * 100) < 0.01

    def test_net_rtg_basic(self):
        from fastbreak.metrics import drtg, net_rtg, ortg  # noqa: PLC0415

        o = ortg(pts=110, fga=90, oreb=10, tov=15, fta=20)
        d = drtg(opp_pts=105, opp_fga=88, opp_oreb=9, opp_tov=13, opp_fta=18)
        assert net_rtg(ortg_val=o, drtg_val=d) == pytest.approx(o - d)

    def test_net_rtg_none_when_either_is_none(self):
        from fastbreak.metrics import net_rtg  # noqa: PLC0415

        assert net_rtg(ortg_val=None, drtg_val=110.0) is None
        assert net_rtg(ortg_val=110.0, drtg_val=None) is None

    def test_drtg_zero_possessions_returns_none(self):
        from fastbreak.metrics import drtg  # noqa: PLC0415

        assert drtg(opp_pts=0, opp_fga=0, opp_oreb=0, opp_tov=0, opp_fta=0) is None


class TestRollingAvg:
    """Tests for rolling_avg()."""

    def test_window_equals_list_length(self) -> None:
        """Single window spanning the entire list returns one result."""
        result = rolling_avg([10.0, 20.0, 30.0], window=3)
        assert result == [None, None, pytest.approx(20.0)]

    def test_window_of_one_returns_each_value(self) -> None:
        """Window=1 is a no-op — each position equals itself."""
        values = [5.0, 10.0, 15.0]
        result = rolling_avg(values, window=1)
        assert result == [pytest.approx(5.0), pytest.approx(10.0), pytest.approx(15.0)]

    def test_warm_up_positions_return_none(self) -> None:
        """Positions before the first full window are None."""
        result = rolling_avg([1.0, 2.0, 3.0, 4.0, 5.0], window=3)
        assert result[0] is None
        assert result[1] is None

    def test_correct_sliding_values(self) -> None:
        """Rolling average slides correctly across the list."""
        result = rolling_avg([1.0, 2.0, 3.0, 4.0, 5.0], window=3)
        assert result[2] == pytest.approx(2.0)  # (1+2+3)/3
        assert result[3] == pytest.approx(3.0)  # (2+3+4)/3
        assert result[4] == pytest.approx(4.0)  # (3+4+5)/3

    def test_none_in_values_propagates_none(self) -> None:
        """None input in any window position produces None output for that window."""
        result = rolling_avg([1.0, None, 3.0, 4.0, 5.0], window=3)
        assert result[2] is None  # window contains None
        assert result[3] is None  # window contains None
        assert result[4] == pytest.approx(4.0)  # (3+4+5)/3 — None no longer in window

    def test_all_none_returns_all_none(self) -> None:
        """All-None input returns all None."""
        result = rolling_avg([None, None, None], window=2)
        assert result == [None, None, None]

    def test_empty_list_returns_empty(self) -> None:
        """Empty input returns empty output."""
        assert rolling_avg([], window=3) == []

    def test_window_larger_than_list_returns_all_none(self) -> None:
        """Window larger than list means no complete window fits — all None."""
        result = rolling_avg([1.0, 2.0], window=5)
        assert result == [None, None]

    def test_invalid_window_raises(self) -> None:
        """window=0 raises ValueError with message naming the constraint."""
        with pytest.raises(ValueError, match="window must be >= 1, got 0"):
            rolling_avg([1.0, 2.0], window=0)

    def test_negative_window_raises(self) -> None:
        """Negative window also raises ValueError."""
        with pytest.raises(ValueError, match="window must be >= 1, got -5"):
            rolling_avg([1.0, 2.0], window=-5)


class TestPossessions:
    """Tests for possessions() — Dean Oliver possession estimate."""

    def test_typical_game(self) -> None:
        """Standard NBA game totals produce a value in the expected range."""
        from fastbreak.metrics import possessions  # noqa: PLC0415

        result = possessions(fga=88, oreb=10, tov=13, fta=20)
        assert result == pytest.approx(99.8, abs=0.01)

    def test_all_zeros_returns_zero(self) -> None:
        """All-zero inputs return 0.0 (no division — valid degenerate case)."""
        from fastbreak.metrics import possessions  # noqa: PLC0415

        assert possessions(fga=0, oreb=0, tov=0, fta=0) == 0.0

    def test_fta_weighted_by_0_44(self) -> None:
        """FTA contributes 0.44 per attempt, not 1.0."""
        from fastbreak.metrics import possessions  # noqa: PLC0415

        result = possessions(fga=0, oreb=0, tov=0, fta=100)
        assert result == pytest.approx(44.0)

    def test_oreb_reduces_possessions(self) -> None:
        """Offensive rebounds reclaim a possession so they subtract."""
        from fastbreak.metrics import possessions  # noqa: PLC0415

        base = possessions(fga=80, oreb=0, tov=10, fta=20)
        with_oreb = possessions(fga=80, oreb=10, tov=10, fta=20)
        assert with_oreb == pytest.approx(base - 10)


class TestAssistRatio:
    """Tests for assist_ratio() — assists per 100 offensive plays."""

    def test_typical_playmaker(self) -> None:
        """8 assists on a typical guard box line → ~27.8."""
        from fastbreak.metrics import assist_ratio  # noqa: PLC0415

        result = assist_ratio(ast=8, fga=16, fta=4, tov=3)
        # denominator = 16 + 0.44*4 + 8 + 3 = 28.76
        assert result == pytest.approx(8 / 28.76 * 100, abs=0.01)

    def test_all_zeros_returns_none(self) -> None:
        """No offensive activity → None."""
        from fastbreak.metrics import assist_ratio  # noqa: PLC0415

        assert assist_ratio(ast=0, fga=0, fta=0, tov=0) is None

    def test_only_assists_is_100(self) -> None:
        """Every offensive play is an assist → ratio is 100."""
        from fastbreak.metrics import assist_ratio  # noqa: PLC0415

        result = assist_ratio(ast=10, fga=0, fta=0, tov=0)
        assert result == pytest.approx(100.0)

    def test_zero_assists_is_zero(self) -> None:
        """No assists → ratio is 0.0."""
        from fastbreak.metrics import assist_ratio  # noqa: PLC0415

        result = assist_ratio(ast=0, fga=15, fta=5, tov=3)
        assert result == pytest.approx(0.0)

    def test_fta_weighted_by_0_44(self) -> None:
        """FTA contributes 0.44 each to the denominator."""
        from fastbreak.metrics import assist_ratio  # noqa: PLC0415

        # denominator = 0 + 0.44*20 + 5 + 0 = 13.8
        result = assist_ratio(ast=5, fga=0, fta=20, tov=0)
        assert result == pytest.approx(5 / 13.8 * 100, abs=0.01)


class TestOffensiveWinShares:
    """Tests for offensive_win_shares()."""

    def test_efficient_scorer_is_positive(self, sample_league: LeagueAverages) -> None:
        """A player scoring well above replacement level has positive OWS."""
        from fastbreak.metrics import offensive_win_shares  # noqa: PLC0415

        result = offensive_win_shares(pts=25, fga=16, fta=4, tov=3, lg=sample_league)
        assert result is not None
        assert result > 0

    def test_below_replacement_is_negative(self, sample_league: LeagueAverages) -> None:
        """A player using many possessions while scoring very little has negative OWS."""
        from fastbreak.metrics import offensive_win_shares  # noqa: PLC0415

        result = offensive_win_shares(pts=5, fga=16, fta=2, tov=3, lg=sample_league)
        assert result is not None
        assert result < 0

    def test_formula_components(self, sample_league: LeagueAverages) -> None:
        """Manually verify the three-step formula against the function output."""
        from fastbreak.metrics import offensive_win_shares  # noqa: PLC0415

        pts, fga, fta, tov = 20.0, 14.0, 6.0, 2.0
        player_poss = 0.96 * (fga + tov + 0.44 * fta)
        marginal = pts - 0.92 * sample_league.vop * player_poss
        expected = marginal / (0.32 * sample_league.lg_pts)

        result = offensive_win_shares(
            pts=pts, fga=fga, fta=fta, tov=tov, lg=sample_league
        )
        assert result == pytest.approx(expected, abs=1e-9)

    def test_zero_pts_zero_possessions_returns_zero_not_none(
        self, sample_league: LeagueAverages
    ) -> None:
        """All-zero inputs → marginal_offense=0, pts_per_win>0, result is 0.0."""
        from fastbreak.metrics import offensive_win_shares  # noqa: PLC0415

        result = offensive_win_shares(pts=0, fga=0, fta=0, tov=0, lg=sample_league)
        assert result == pytest.approx(0.0)

    def test_degenerate_lg_pts_returns_none(self) -> None:
        """lg.lg_pts == 0 → can't compute pts_per_win → None."""
        from fastbreak.metrics import LeagueAverages, offensive_win_shares  # noqa: PLC0415

        degenerate = LeagueAverages(
            lg_pts=0.0,
            lg_fga=85.0,
            lg_fta=20.0,
            lg_ftm=15.0,
            lg_oreb=10.0,
            lg_treb=40.0,
            lg_ast=24.0,
            lg_fgm=40.0,
            lg_fg3m=10.0,
            lg_tov=12.0,
            lg_pf=18.0,
        )
        assert offensive_win_shares(pts=20, fga=14, fta=6, tov=2, lg=degenerate) is None
