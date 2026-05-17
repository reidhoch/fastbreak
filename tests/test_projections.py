"""Tests for fastbreak.projections."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest
from hypothesis import given, strategies as st


def test_imports() -> None:
    from fastbreak.projections import (
        PlayerProjection,
        ProjectionStat,
        StatProjection,
    )

    assert ProjectionStat.__args__ == ("pts", "reb", "ast", "fg3m")  # type: ignore[attr-defined]


def test_stat_projection_is_frozen() -> None:
    from fastbreak.projections import StatProjection

    sp = StatProjection(
        stat="pts",
        mean=25.0,
        stdev=6.0,
        distribution="normal",
        rolling_n=10,
        season_mean=24.0,
        rolling_mean=26.0,
        adjustments={},
    )
    with pytest.raises(FrozenInstanceError):
        sp.mean = 100.0  # type: ignore[misc]


def test_stat_projection_rejects_nan_mean() -> None:
    import math

    from fastbreak.projections import StatProjection

    with pytest.raises(ValueError, match="mean must be finite"):
        StatProjection(
            stat="pts",
            mean=math.nan,
            stdev=6.0,
            distribution="normal",
            rolling_n=10,
            season_mean=24.0,
            rolling_mean=26.0,
        )


def test_stat_projection_rejects_nonpositive_stdev() -> None:
    from fastbreak.projections import StatProjection

    with pytest.raises(ValueError, match="stdev must be a finite positive"):
        StatProjection(
            stat="pts",
            mean=25.0,
            stdev=0.0,
            distribution="normal",
            rolling_n=10,
            season_mean=24.0,
            rolling_mean=26.0,
        )


def test_stat_projection_rejects_negative_rolling_n() -> None:
    from fastbreak.projections import StatProjection

    with pytest.raises(ValueError, match="rolling_n must be >= 0"):
        StatProjection(
            stat="pts",
            mean=25.0,
            stdev=6.0,
            distribution="normal",
            rolling_n=-1,
            season_mean=24.0,
            rolling_mean=26.0,
        )


def test_stat_projection_rejects_inf_season_mean() -> None:
    import math

    from fastbreak.projections import StatProjection

    with pytest.raises(ValueError, match="season_mean must be finite"):
        StatProjection(
            stat="pts",
            mean=25.0,
            stdev=6.0,
            distribution="normal",
            rolling_n=10,
            season_mean=math.inf,
            rolling_mean=26.0,
        )


def test_player_projection_is_frozen() -> None:
    from datetime import date

    from fastbreak.projections import PlayerProjection

    pp = PlayerProjection(
        player_id=2544,
        player_name="LeBron James",
        opponent_team_id=1610612738,
        game_date=date(2026, 5, 7),
        is_home=True,
        stats={},
    )
    with pytest.raises(FrozenInstanceError):
        pp.player_id = 1  # type: ignore[misc]


def test_player_projection_rejects_invalid_ids() -> None:
    from datetime import date

    from fastbreak.projections import PlayerProjection

    with pytest.raises(ValueError, match="player_id must be >= 1"):
        PlayerProjection(
            player_id=0,
            player_name="X",
            opponent_team_id=1610612738,
            game_date=date(2026, 5, 7),
            is_home=True,
        )
    with pytest.raises(ValueError, match="opponent_team_id must be >= 1"):
        PlayerProjection(
            player_id=2544,
            player_name="X",
            opponent_team_id=-1,
            game_date=date(2026, 5, 7),
            is_home=True,
        )
    with pytest.raises(ValueError, match="player_name must be non-empty"):
        PlayerProjection(
            player_id=2544,
            player_name="",
            opponent_team_id=1610612738,
            game_date=date(2026, 5, 7),
            is_home=True,
        )


def test_player_projection_rejects_stat_key_mismatch() -> None:
    from datetime import date

    from fastbreak.projections import PlayerProjection, StatProjection

    sp_reb = StatProjection(
        stat="reb",
        mean=8.0,
        stdev=2.0,
        distribution="normal",
        rolling_n=10,
        season_mean=8.0,
        rolling_mean=8.0,
    )
    # Dict-key/projection-stat mismatch: lookup proj.stats["pts"] returns
    # a rebound projection. This is the most insidious case caught by the
    # post-init check.
    with pytest.raises(ValueError, match="stats\\['pts'\\].stat must equal 'pts'"):
        PlayerProjection(
            player_id=2544,
            player_name="LBJ",
            opponent_team_id=1610612738,
            game_date=date(2026, 5, 7),
            is_home=True,
            stats={"pts": sp_reb},
        )


def test_internal_mappings_are_immutable() -> None:
    """_STAT_DISTRIBUTION and _STDEV_FLOORS are MappingProxyType so a stray
    `module._STAT_DISTRIBUTION["pts"] = "poisson"` cannot poison the math
    for every subsequent projection in the same process."""
    import fastbreak.projections as p

    with pytest.raises(TypeError):
        p._STAT_DISTRIBUTION["pts"] = "poisson"  # type: ignore[index]
    with pytest.raises(TypeError):
        p._STDEV_FLOORS["pts"] = 999.0  # type: ignore[index]


def test_priors_writer_rejects_degenerate_variance(tmp_path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """The priors regeneration script must refuse to overwrite the live
    module with sub-microscopic variance values that the .6f formatter
    would round to 0.000000 (silently disabling shrinkage at projection
    time). NaN/inf cases are caught earlier by StatPrior.__post_init__,
    but the writer's stricter `>= 1e-6` threshold is its own tripwire."""
    import sys

    sys.path.insert(0, "scripts")
    import compute_projection_priors as cpp  # type: ignore[import-not-found]

    from fastbreak.projections_priors import StatPrior

    real_target = (
        cpp.Path(cpp.__file__).resolve().parent.parent
        / "src"
        / "fastbreak"
        / "projections_priors.py"
    )

    good = StatPrior(
        tau_sq=1.0, sigma_sq=1.0, season="2025-26", n_players=100, n_games=5000
    )
    # Below the 1e-6 writer threshold but above StatPrior's `> 0` floor.
    sub = StatPrior(
        tau_sq=1e-8, sigma_sq=1.0, season="2025-26", n_players=100, n_games=5000
    )

    priors = dict.fromkeys(cpp.STATS, good) | {"reb": sub}
    with pytest.raises(ValueError, match="degenerate"):
        cpp._write_priors_module(priors)

    # Sanity: the live file is untouched.
    assert real_target.exists()


def test_stats_tuple_matches_literal() -> None:
    """Catch drift between the STATS tuple and the ProjectionStat literal."""
    from typing import get_args

    from fastbreak.projections import STATS, ProjectionStat

    assert STATS == get_args(ProjectionStat)


# ---------- empirical_bayes_blend ----------


def test_blend_matches_textbook_formula() -> None:
    from fastbreak.projections import empirical_bayes_blend

    # w = tau_sq / (tau_sq + sigma_sq / n)
    # With tau_sq=1, sigma_sq=1, n=1 -> w = 0.5 -> midpoint.
    result = empirical_bayes_blend(
        rolling_mean=10.0, season_mean=20.0, n=1, tau_sq=1.0, sigma_sq=1.0
    )
    assert result == pytest.approx(15.0, abs=1e-9)


def test_blend_large_n_trusts_rolling() -> None:
    from fastbreak.projections import empirical_bayes_blend

    # As n -> infinity, weight on rolling_mean -> 1.
    result = empirical_bayes_blend(
        rolling_mean=30.0, season_mean=20.0, n=1000, tau_sq=1.0, sigma_sq=1.0
    )
    assert result == pytest.approx(30.0, rel=1e-3)


def test_blend_small_n_anchors_to_season() -> None:
    from fastbreak.projections import empirical_bayes_blend

    # As sigma_sq/n dominates, weight on rolling_mean -> 0.
    result = empirical_bayes_blend(
        rolling_mean=30.0, season_mean=20.0, n=1, tau_sq=0.01, sigma_sq=100.0
    )
    # w = 0.01 / (0.01 + 100) = ~1e-4 -> almost all season mean
    assert result == pytest.approx(20.0, rel=1e-3)


def test_blend_result_between_inputs() -> None:
    from fastbreak.projections import empirical_bayes_blend

    for n in (1, 5, 10, 50):
        result = empirical_bayes_blend(
            rolling_mean=10.0, season_mean=20.0, n=n, tau_sq=5.0, sigma_sq=10.0
        )
        assert 10.0 <= result <= 20.0


def test_blend_rejects_nonpositive_n() -> None:
    from fastbreak.projections import empirical_bayes_blend

    with pytest.raises(ValueError, match="n must be positive"):
        empirical_bayes_blend(10.0, 20.0, n=0, tau_sq=1.0, sigma_sq=1.0)


def test_blend_rejects_negative_variance() -> None:
    from fastbreak.projections import empirical_bayes_blend

    with pytest.raises(ValueError, match="variance"):
        empirical_bayes_blend(10.0, 20.0, n=5, tau_sq=-1.0, sigma_sq=1.0)
    with pytest.raises(ValueError, match="variance"):
        empirical_bayes_blend(10.0, 20.0, n=5, tau_sq=1.0, sigma_sq=-1.0)


def test_blend_rejects_nan_inputs() -> None:
    import math

    from fastbreak.projections import empirical_bayes_blend

    # NaN slips past `< 0` and `== 0` comparisons in CPython.
    for kwargs in (
        {"rolling_mean": math.nan, "season_mean": 20.0, "tau_sq": 1.0, "sigma_sq": 1.0},
        {"rolling_mean": 10.0, "season_mean": math.nan, "tau_sq": 1.0, "sigma_sq": 1.0},
        {
            "rolling_mean": 10.0,
            "season_mean": 20.0,
            "tau_sq": math.nan,
            "sigma_sq": 1.0,
        },
        {
            "rolling_mean": 10.0,
            "season_mean": 20.0,
            "tau_sq": 1.0,
            "sigma_sq": math.nan,
        },
    ):
        with pytest.raises(ValueError, match="must be finite"):
            empirical_bayes_blend(n=5, **kwargs)


def test_blend_rejects_inf_inputs() -> None:
    import math

    from fastbreak.projections import empirical_bayes_blend

    with pytest.raises(ValueError, match="must be finite"):
        empirical_bayes_blend(
            rolling_mean=math.inf,
            season_mean=20.0,
            n=5,
            tau_sq=1.0,
            sigma_sq=1.0,
        )


# ---------- empirical_bayes_blend: property-based ----------


@given(
    rolling=st.floats(
        min_value=-50, max_value=200, allow_nan=False, allow_infinity=False
    ),
    season=st.floats(
        min_value=-50, max_value=200, allow_nan=False, allow_infinity=False
    ),
    n=st.integers(min_value=1, max_value=100),
    tau_sq=st.floats(min_value=0.0, max_value=100, allow_nan=False),
    sigma_sq=st.floats(min_value=0.0, max_value=100, allow_nan=False),
)
def test_blend_always_between(
    rolling: float, season: float, n: int, tau_sq: float, sigma_sq: float
) -> None:
    from fastbreak.projections import empirical_bayes_blend

    result = empirical_bayes_blend(
        rolling, season, n=n, tau_sq=tau_sq, sigma_sq=sigma_sq
    )
    lo, hi = sorted([rolling, season])
    assert lo - 1e-9 <= result <= hi + 1e-9


@given(
    rolling=st.floats(
        min_value=-50, max_value=200, allow_nan=False, allow_infinity=False
    ),
    season=st.floats(
        min_value=-50, max_value=200, allow_nan=False, allow_infinity=False
    ),
    tau_sq=st.floats(min_value=0.01, max_value=100, allow_nan=False),
    sigma_sq=st.floats(min_value=0.01, max_value=100, allow_nan=False),
)
def test_blend_monotonic_in_n(
    rolling: float, season: float, tau_sq: float, sigma_sq: float
) -> None:
    from fastbreak.projections import empirical_bayes_blend

    # As n increases, |blended - rolling_mean| is non-increasing.
    small = empirical_bayes_blend(
        rolling, season, n=1, tau_sq=tau_sq, sigma_sq=sigma_sq
    )
    large = empirical_bayes_blend(
        rolling, season, n=100, tau_sq=tau_sq, sigma_sq=sigma_sq
    )
    assert abs(large - rolling) <= abs(small - rolling) + 1e-9


# ---------- normal_sf ----------


def test_normal_sf_symmetry() -> None:
    from fastbreak.projections import normal_sf

    # sf(mean) = 0.5
    assert normal_sf(x=0.0, mean=0.0, stdev=1.0) == pytest.approx(0.5, abs=1e-9)
    assert normal_sf(x=10.0, mean=10.0, stdev=3.0) == pytest.approx(0.5, abs=1e-9)


def test_normal_sf_known_values() -> None:
    from fastbreak.projections import normal_sf

    # 1 stdev above mean -> ~0.1587
    assert normal_sf(x=1.0, mean=0.0, stdev=1.0) == pytest.approx(0.15866, abs=1e-4)
    # 2 stdev above mean -> ~0.02275
    assert normal_sf(x=2.0, mean=0.0, stdev=1.0) == pytest.approx(0.02275, abs=1e-4)


def test_normal_sf_monotone_decreasing() -> None:
    from fastbreak.projections import normal_sf

    prev = 1.0
    for i in range(-20, 21):
        cur = normal_sf(x=i * 0.1, mean=0.0, stdev=1.0)
        assert cur <= prev + 1e-12
        prev = cur


def test_normal_sf_rejects_nonpositive_stdev() -> None:
    from fastbreak.projections import normal_sf

    with pytest.raises(ValueError, match="stdev must be a finite positive"):
        normal_sf(x=0.0, mean=0.0, stdev=0.0)


def test_normal_sf_rejects_nan_stdev() -> None:
    import math

    from fastbreak.projections import normal_sf

    # NaN slips past `stdev <= 0` because NaN comparisons are False —
    # without the explicit isfinite guard, the result silently propagates NaN.
    with pytest.raises(ValueError, match="stdev must be a finite positive"):
        normal_sf(x=0.0, mean=0.0, stdev=math.nan)


def test_normal_sf_rejects_inf_stdev() -> None:
    import math

    from fastbreak.projections import normal_sf

    with pytest.raises(ValueError, match="stdev must be a finite positive"):
        normal_sf(x=0.0, mean=0.0, stdev=math.inf)


def test_normal_sf_rejects_nan_x_or_mean() -> None:
    import math

    from fastbreak.projections import normal_sf

    with pytest.raises(ValueError, match="must not be NaN"):
        normal_sf(x=math.nan, mean=0.0, stdev=1.0)
    with pytest.raises(ValueError, match="must not be NaN"):
        normal_sf(x=0.0, mean=math.nan, stdev=1.0)


def test_normal_sf_accepts_inf_x_at_asymptote() -> None:
    import math

    from fastbreak.projections import normal_sf

    # +inf line: P(X > inf) = 0; -inf line: P(X > -inf) = 1.
    assert normal_sf(x=math.inf, mean=0.0, stdev=1.0) == 0.0
    assert normal_sf(x=-math.inf, mean=0.0, stdev=1.0) == 1.0


# ---------- poisson_sf ----------


def test_poisson_sf_lambda_zero_returns_zero() -> None:
    from fastbreak.projections import poisson_sf

    # P(X > 0 | lambda=0) = 0 exactly (mass all at 0)
    assert poisson_sf(line=0.0, lam=0.0) == pytest.approx(0.0, abs=1e-12)


def test_poisson_sf_known_values() -> None:
    from fastbreak.projections import poisson_sf

    # lambda=3, P(X > 3) = 1 - CDF(3, 3) ~ 0.3528
    assert poisson_sf(line=3.0, lam=3.0) == pytest.approx(0.3528, abs=1e-3)
    # P(X > 2 | lambda=3) ~ 0.5768
    assert poisson_sf(line=2.0, lam=3.0) == pytest.approx(0.5768, abs=1e-3)


def test_poisson_sf_fractional_line_floors() -> None:
    from fastbreak.projections import poisson_sf

    # P(X > 2.5) = P(X > 2) because X is integer-valued
    assert poisson_sf(line=2.5, lam=3.0) == pytest.approx(
        poisson_sf(line=2.0, lam=3.0), abs=1e-9
    )


def test_poisson_sf_negative_line_returns_one() -> None:
    from fastbreak.projections import poisson_sf

    # P(X > -1 | any lambda > 0) = 1
    assert poisson_sf(line=-1.0, lam=3.0) == pytest.approx(1.0, abs=1e-12)


def test_poisson_sf_rejects_negative_lambda() -> None:
    from fastbreak.projections import poisson_sf

    with pytest.raises(ValueError, match="lam must be a finite non-negative"):
        poisson_sf(line=0.0, lam=-0.1)


def test_poisson_sf_rejects_nan_lam() -> None:
    import math

    from fastbreak.projections import poisson_sf

    # NaN slips past `lam < 0` (NaN < 0 is False); without the guard the
    # body would compute exp(-NaN) = NaN and return a confident-looking 1.0.
    with pytest.raises(ValueError, match="lam must be a finite non-negative"):
        poisson_sf(line=2.5, lam=math.nan)


def test_poisson_sf_rejects_inf_lam() -> None:
    import math

    from fastbreak.projections import poisson_sf

    with pytest.raises(ValueError, match="lam must be a finite non-negative"):
        poisson_sf(line=2.5, lam=math.inf)


def test_poisson_sf_rejects_nan_line() -> None:
    import math

    from fastbreak.projections import poisson_sf

    with pytest.raises(ValueError, match="line must not be NaN"):
        poisson_sf(line=math.nan, lam=2.0)


def test_poisson_sf_inf_line_returns_zero() -> None:
    import math

    from fastbreak.projections import poisson_sf

    # P(X > inf) = 0 for any finite Poisson; previously this raised
    # OverflowError from math.floor(inf) before reaching any guard.
    assert poisson_sf(line=math.inf, lam=2.0) == 0.0


# ---------- adjust_for_opponent ----------


def test_opponent_tougher_than_average_suppresses_scoring() -> None:
    from fastbreak.projections import adjust_for_opponent

    # Lower def_rating = better defense. If opp_def_rating < league_avg, delta < 0.
    delta = adjust_for_opponent(
        blended_mean=25.0, stat="pts", opp_def_rating=105.0, league_avg_def_rating=112.0
    )
    assert delta < 0


def test_opponent_softer_than_average_inflates_scoring() -> None:
    from fastbreak.projections import adjust_for_opponent

    delta = adjust_for_opponent(
        blended_mean=25.0, stat="pts", opp_def_rating=118.0, league_avg_def_rating=112.0
    )
    assert delta > 0


def test_opponent_adjustment_clamped_at_15pct() -> None:
    from fastbreak.projections import adjust_for_opponent

    # Extreme defense rating — clamp should keep delta within ±15% of blended mean.
    delta_cold = adjust_for_opponent(
        blended_mean=25.0, stat="pts", opp_def_rating=50.0, league_avg_def_rating=112.0
    )
    delta_hot = adjust_for_opponent(
        blended_mean=25.0, stat="pts", opp_def_rating=200.0, league_avg_def_rating=112.0
    )
    assert abs(delta_cold) <= 25.0 * 0.15 + 1e-9
    assert abs(delta_hot) <= 25.0 * 0.15 + 1e-9


def test_opponent_only_applies_to_scoring_stats() -> None:
    from fastbreak.projections import adjust_for_opponent

    # Reb and ast are not adjusted by opponent def rating (v1 scope note).
    assert (
        adjust_for_opponent(
            blended_mean=8.0,
            stat="reb",
            opp_def_rating=105.0,
            league_avg_def_rating=112.0,
        )
        == 0.0
    )
    assert (
        adjust_for_opponent(
            blended_mean=8.0,
            stat="ast",
            opp_def_rating=105.0,
            league_avg_def_rating=112.0,
        )
        == 0.0
    )


def test_opponent_rejects_nan_opp_def_rating() -> None:
    import math

    import pytest

    from fastbreak.projections import adjust_for_opponent

    # NaN must not silently clamp to ±15% (CPython min/max do not preserve NaN).
    with pytest.raises(ValueError, match="opp_def_rating must be finite"):
        adjust_for_opponent(
            blended_mean=25.0,
            stat="pts",
            opp_def_rating=math.nan,
            league_avg_def_rating=110.0,
        )


def test_opponent_rejects_inf_league_avg() -> None:
    import math

    import pytest

    from fastbreak.projections import adjust_for_opponent

    with pytest.raises(ValueError, match="league_avg_def_rating must be finite"):
        adjust_for_opponent(
            blended_mean=25.0,
            stat="pts",
            opp_def_rating=110.0,
            league_avg_def_rating=math.inf,
        )


def test_opponent_skips_validation_for_non_scoring_stats() -> None:
    import math

    from fastbreak.projections import adjust_for_opponent

    # reb/ast short-circuit before the finite check; no need to validate
    # NaN ratings if they're not used.
    assert (
        adjust_for_opponent(
            blended_mean=8.0,
            stat="reb",
            opp_def_rating=math.nan,
            league_avg_def_rating=math.nan,
        )
        == 0.0
    )


# ---------- adjust_for_rest ----------


def test_rest_back_to_back_drops_scoring() -> None:
    from fastbreak.projections import adjust_for_rest

    delta = adjust_for_rest(blended_mean=25.0, stat="pts", days_rest=0)
    assert delta < 0


def test_rest_three_plus_days_boosts_scoring() -> None:
    from fastbreak.projections import adjust_for_rest

    delta = adjust_for_rest(blended_mean=25.0, stat="pts", days_rest=3)
    assert delta > 0


def test_rest_one_day_is_neutral() -> None:
    from fastbreak.projections import adjust_for_rest

    # 1 day rest = standard NBA spacing; no delta.
    assert adjust_for_rest(blended_mean=25.0, stat="pts", days_rest=1) == 0.0


def test_rest_none_returns_zero_adjustment() -> None:
    from fastbreak.projections import adjust_for_rest

    # None means "unknown rest" (e.g. first game of season): no adjustment.
    assert adjust_for_rest(blended_mean=25.0, stat="pts", days_rest=None) == 0.0


def test_rest_negative_raises() -> None:
    import pytest

    from fastbreak.projections import adjust_for_rest

    with pytest.raises(ValueError, match="days_rest must be >= 0"):
        adjust_for_rest(blended_mean=25.0, stat="pts", days_rest=-1)


# ---------- adjust_for_home ----------


def test_home_boosts_scoring_slightly() -> None:
    from fastbreak.projections import adjust_for_home

    delta_home = adjust_for_home(blended_mean=25.0, stat="pts", is_home=True)
    delta_away = adjust_for_home(blended_mean=25.0, stat="pts", is_home=False)
    assert delta_home > 0
    assert delta_away < 0
    assert abs(delta_home) <= 25.0 * 0.05 + 1e-9  # small bonus only


# ---------- StatProjection.prob_over ----------


def test_prob_over_normal_dispatch() -> None:
    from fastbreak.projections import StatProjection

    sp = StatProjection(
        stat="pts",
        mean=25.0,
        stdev=6.0,
        distribution="normal",
        rolling_n=10,
        season_mean=24.0,
        rolling_mean=26.0,
        adjustments={},
    )
    # Line equals mean -> 0.5
    assert sp.prob_over(25.0) == pytest.approx(0.5, abs=1e-6)
    assert sp.prob_over(-1000.0) == pytest.approx(1.0, abs=1e-9)
    assert sp.prob_over(1000.0) == pytest.approx(0.0, abs=1e-9)


def test_prob_over_poisson_dispatch() -> None:
    import math

    from fastbreak.projections import StatProjection, poisson_sf

    sp = StatProjection(
        stat="fg3m",
        mean=3.0,
        stdev=math.sqrt(3.0),
        distribution="poisson",
        rolling_n=10,
        season_mean=2.8,
        rolling_mean=3.2,
        adjustments={},
    )
    # Must match poisson_sf(3.0, 3.0) exactly.
    assert sp.prob_over(3.0) == pytest.approx(poisson_sf(line=3.0, lam=3.0))


def test_prob_over_unknown_distribution_raises() -> None:
    from fastbreak.projections import StatProjection

    # Bypass the frozen dataclass's __setattr__ to force an invalid distribution
    # and exercise the runtime dispatch guard.
    sp = StatProjection(
        stat="pts",
        mean=1.0,
        stdev=1.0,
        distribution="normal",
        rolling_n=1,
        season_mean=1.0,
        rolling_mean=1.0,
        adjustments={},
    )
    object.__setattr__(sp, "distribution", "cauchy")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="Unsupported distribution"):
        sp.prob_over(0.0)


# ---------- priors ----------


def test_priors_has_all_four_stats() -> None:
    from fastbreak.projections_priors import STAT_PRIORS

    assert set(STAT_PRIORS.keys()) == {"pts", "reb", "ast", "fg3m"}


def test_priors_positive_variance() -> None:
    from fastbreak.projections_priors import STAT_PRIORS

    for stat, prior in STAT_PRIORS.items():
        assert prior.tau_sq > 0, f"{stat}: tau_sq must be positive"
        assert prior.sigma_sq > 0, f"{stat}: sigma_sq must be positive"


def test_priors_have_provenance() -> None:
    from fastbreak.projections_priors import STAT_PRIORS

    for prior in STAT_PRIORS.values():
        assert prior.season  # non-empty string
        assert prior.n_players >= 10  # minimum pool size


def test_stat_prior_rejects_nan_tau_sq() -> None:
    import math

    from fastbreak.projections_priors import StatPrior

    with pytest.raises(ValueError, match="tau_sq must be finite and positive"):
        StatPrior(
            tau_sq=math.nan,
            sigma_sq=1.0,
            season="2025-26",
            n_players=10,
            n_games=300,
        )


def test_stat_prior_rejects_zero_sigma_sq() -> None:
    from fastbreak.projections_priors import StatPrior

    with pytest.raises(ValueError, match="sigma_sq must be finite and positive"):
        StatPrior(
            tau_sq=1.0,
            sigma_sq=0.0,
            season="2025-26",
            n_players=10,
            n_games=300,
        )


def test_stat_prior_rejects_empty_season() -> None:
    from fastbreak.projections_priors import StatPrior

    with pytest.raises(ValueError, match="season must be a non-empty"):
        StatPrior(
            tau_sq=1.0,
            sigma_sq=1.0,
            season="",
            n_players=10,
            n_games=300,
        )


def test_stat_prior_rejects_zero_sample_sizes() -> None:
    import pytest as _pytest

    from fastbreak.projections_priors import StatPrior

    with _pytest.raises(ValueError, match="n_players must be >= 1"):
        StatPrior(
            tau_sq=1.0,
            sigma_sq=1.0,
            season="2025-26",
            n_players=0,
            n_games=300,
        )
    with _pytest.raises(ValueError, match="n_games must be >= 1"):
        StatPrior(
            tau_sq=1.0,
            sigma_sq=1.0,
            season="2025-26",
            n_players=10,
            n_games=0,
        )


# ---------- project_player (mocked API) ----------


def test_project_player_returns_all_four_stats(mocker) -> None:
    """End-to-end with mocked endpoints; verify shape and basic invariants."""
    import anyio
    from datetime import date

    from fastbreak.clients.nba import NBAClient
    from fastbreak.projections import project_player

    # Minimal PlayerGameLog-style payload: 20 games of steady production.
    game_rows = [
        [
            f"002250000{i:02d}",  # Game_ID
            2544,  # Player_ID
            "22025",  # SEASON_ID
            f"2025-12-{i + 1:02d}",  # GAME_DATE
            "LAL vs. DEN",  # MATCHUP
            "W",  # WL
            35,  # MIN
            10,
            20,
            0.5,  # FGM, FGA, FG_PCT
            2,
            5,
            0.4,  # FG3M, FG3A, FG3_PCT
            5,
            6,
            0.833,  # FTM, FTA, FT_PCT
            1,
            6,
            7,  # OREB, DREB, REB
            8,  # AST
            1,
            1,
            3,
            2,  # STL, BLK, TOV, PF
            27,  # PTS
            5,  # PLUS_MINUS
            0,  # VIDEO_AVAILABLE
        ]
        for i in range(20)
    ]
    game_log_payload = {
        "resultSets": [
            {
                "name": "PlayerGameLog",
                "headers": [
                    "Game_ID",
                    "Player_ID",
                    "SEASON_ID",
                    "GAME_DATE",
                    "MATCHUP",
                    "WL",
                    "MIN",
                    "FGM",
                    "FGA",
                    "FG_PCT",
                    "FG3M",
                    "FG3A",
                    "FG3_PCT",
                    "FTM",
                    "FTA",
                    "FT_PCT",
                    "OREB",
                    "DREB",
                    "REB",
                    "AST",
                    "STL",
                    "BLK",
                    "TOV",
                    "PF",
                    "PTS",
                    "PLUS_MINUS",
                    "VIDEO_AVAILABLE",
                ],
                "rowSet": game_rows,
            }
        ]
    }
    team_est_payload = {
        "resultSet": {
            "name": "TeamEstimatedMetrics",
            "headers": [
                "TEAM_NAME",
                "TEAM_ID",
                "GP",
                "W",
                "L",
                "W_PCT",
                "MIN",
                "E_OFF_RATING",
                "E_DEF_RATING",
                "E_NET_RATING",
                "E_PACE",
                "E_AST_RATIO",
                "E_OREB_PCT",
                "E_DREB_PCT",
                "E_REB_PCT",
                "E_TM_TOV_PCT",
                "GP_RANK",
                "W_RANK",
                "L_RANK",
                "W_PCT_RANK",
                "MIN_RANK",
                "E_OFF_RATING_RANK",
                "E_DEF_RATING_RANK",
                "E_NET_RATING_RANK",
                "E_AST_RATIO_RANK",
                "E_OREB_PCT_RANK",
                "E_DREB_PCT_RANK",
                "E_REB_PCT_RANK",
                "E_TM_TOV_PCT_RANK",
                "E_PACE_RANK",
            ],
            "rowSet": [
                [
                    "Denver Nuggets",
                    1610612743,
                    82,
                    50,
                    32,
                    0.610,
                    3500.0,
                    118.0,
                    110.0,
                    8.0,
                    100.0,
                    1.8,
                    0.25,
                    0.75,
                    0.5,
                    0.13,
                    1,
                    5,
                    5,
                    5,
                    15,
                    3,
                    5,
                    4,
                    10,
                    12,
                    13,
                    11,
                    20,
                    18,
                ],
                [
                    "Los Angeles Lakers",
                    1610612747,
                    82,
                    45,
                    37,
                    0.549,
                    3500.0,
                    115.0,
                    112.0,
                    3.0,
                    99.0,
                    1.7,
                    0.24,
                    0.74,
                    0.49,
                    0.14,
                    2,
                    10,
                    10,
                    10,
                    16,
                    8,
                    10,
                    10,
                    12,
                    14,
                    15,
                    13,
                    18,
                    22,
                ],
            ],
        }
    }

    async def fake_get_many(self, endpoints, **kwargs):
        from fastbreak.endpoints import PlayerGameLog, TeamEstimatedMetrics

        out = []
        for ep in endpoints:
            if isinstance(ep, PlayerGameLog):
                out.append(ep.response_model.model_validate(game_log_payload))
            elif isinstance(ep, TeamEstimatedMetrics):
                out.append(ep.response_model.model_validate(team_est_payload))
            else:
                raise RuntimeError(f"Unexpected endpoint: {type(ep).__name__}")
        return out

    mocker.patch("fastbreak.clients.nba.NBAClient.get_many", fake_get_many)

    async def run() -> None:
        async with NBAClient() as client:
            result = await project_player(
                client,
                player_id=2544,
                player_name="LeBron James",
                opponent_team_id=1610612743,
                is_home=True,
                game_date=date(2026, 5, 7),
                season="2025-26",
                days_rest=1,
                rolling_n=10,
            )
        assert set(result.stats.keys()) == {"pts", "reb", "ast", "fg3m"}
        for sp in result.stats.values():
            assert sp.mean > 0
            assert sp.stdev > 0
            assert sp.rolling_n == 10
            # Blended mean must be near rolling/season (within adjustment slack).
            lo, hi = sorted([sp.rolling_mean, sp.season_mean])
            assert lo * 0.80 <= sp.mean <= hi * 1.20

    anyio.run(run)


@pytest.mark.parametrize("bad_rolling_n", [0, -1, -10])
def test_project_player_raises_on_non_positive_rolling_n(bad_rolling_n: int) -> None:
    """ValueError when rolling_n < 1 (negative values would silently re-slice)."""
    import anyio
    from datetime import date

    from fastbreak.clients.nba import NBAClient
    from fastbreak.projections import project_player

    async def run() -> None:
        async with NBAClient() as client:
            with pytest.raises(ValueError, match="rolling_n must be >= 1"):
                await project_player(
                    client,
                    player_id=2544,
                    player_name="LeBron James",
                    opponent_team_id=1610612743,
                    is_home=True,
                    game_date=date(2026, 5, 7),
                    season="2025-26",
                    days_rest=1,
                    rolling_n=bad_rolling_n,
                )

    anyio.run(run)


@pytest.mark.parametrize("bad_days_rest", [-1, -10])
def test_project_player_raises_on_negative_days_rest(bad_days_rest: int) -> None:
    """ValueError when days_rest is negative (was silently treated as 1-2 days)."""
    import anyio
    from datetime import date

    from fastbreak.clients.nba import NBAClient
    from fastbreak.projections import project_player

    async def run() -> None:
        async with NBAClient() as client:
            with pytest.raises(ValueError, match="days_rest must be >= 0"):
                await project_player(
                    client,
                    player_id=2544,
                    player_name="LeBron James",
                    opponent_team_id=1610612743,
                    is_home=True,
                    game_date=date(2026, 5, 7),
                    season="2025-26",
                    days_rest=bad_days_rest,
                    rolling_n=10,
                )

    anyio.run(run)


def test_project_player_raises_on_unsupported_stat() -> None:
    """ValueError at entry when `stats` contains an unsupported value.

    Mypy strict catches the typo at type-check time, but dynamic callers
    (config files, JSON) need a clear runtime error rather than a deep
    KeyError from STAT_PRIORS.
    """
    import anyio
    from datetime import date
    from typing import cast

    from fastbreak.clients.nba import NBAClient
    from fastbreak.projections import ProjectionStat, project_player

    async def run() -> None:
        async with NBAClient() as client:
            with pytest.raises(ValueError, match="unsupported stats"):
                await project_player(
                    client,
                    player_id=2544,
                    player_name="LeBron James",
                    opponent_team_id=1610612743,
                    is_home=True,
                    game_date=date(2026, 5, 7),
                    season="2025-26",
                    days_rest=1,
                    rolling_n=10,
                    stats=[cast("ProjectionStat", "stl")],
                )

    anyio.run(run)


def test_project_player_raises_on_empty_games(mocker) -> None:
    """ValueError when the player's game log returns zero games."""
    import anyio
    from datetime import date

    from fastbreak.clients.nba import NBAClient
    from fastbreak.projections import project_player

    empty_game_log_payload = {
        "resultSets": [
            {
                "name": "PlayerGameLog",
                "headers": [
                    "Game_ID",
                    "Player_ID",
                    "SEASON_ID",
                    "GAME_DATE",
                    "MATCHUP",
                    "WL",
                    "MIN",
                    "FGM",
                    "FGA",
                    "FG_PCT",
                    "FG3M",
                    "FG3A",
                    "FG3_PCT",
                    "FTM",
                    "FTA",
                    "FT_PCT",
                    "OREB",
                    "DREB",
                    "REB",
                    "AST",
                    "STL",
                    "BLK",
                    "TOV",
                    "PF",
                    "PTS",
                    "PLUS_MINUS",
                    "VIDEO_AVAILABLE",
                ],
                "rowSet": [],
            }
        ]
    }
    minimal_team_payload = {
        "resultSet": {
            "name": "TeamEstimatedMetrics",
            "headers": [
                "TEAM_NAME",
                "TEAM_ID",
                "GP",
                "W",
                "L",
                "W_PCT",
                "MIN",
                "E_OFF_RATING",
                "E_DEF_RATING",
                "E_NET_RATING",
                "E_PACE",
                "E_AST_RATIO",
                "E_OREB_PCT",
                "E_DREB_PCT",
                "E_REB_PCT",
                "E_TM_TOV_PCT",
                "GP_RANK",
                "W_RANK",
                "L_RANK",
                "W_PCT_RANK",
                "MIN_RANK",
                "E_OFF_RATING_RANK",
                "E_DEF_RATING_RANK",
                "E_NET_RATING_RANK",
                "E_AST_RATIO_RANK",
                "E_OREB_PCT_RANK",
                "E_DREB_PCT_RANK",
                "E_REB_PCT_RANK",
                "E_TM_TOV_PCT_RANK",
                "E_PACE_RANK",
            ],
            "rowSet": [
                [
                    "Denver Nuggets",
                    1610612743,
                    82,
                    50,
                    32,
                    0.610,
                    3500.0,
                    118.0,
                    110.0,
                    8.0,
                    100.0,
                    1.8,
                    0.25,
                    0.75,
                    0.5,
                    0.13,
                    1,
                    5,
                    5,
                    5,
                    15,
                    3,
                    5,
                    4,
                    10,
                    12,
                    13,
                    11,
                    20,
                    18,
                ],
            ],
        }
    }

    async def fake_get_many(self, endpoints, **kwargs):
        from fastbreak.endpoints import PlayerGameLog, TeamEstimatedMetrics

        out = []
        for ep in endpoints:
            if isinstance(ep, PlayerGameLog):
                out.append(ep.response_model.model_validate(empty_game_log_payload))
            elif isinstance(ep, TeamEstimatedMetrics):
                out.append(ep.response_model.model_validate(minimal_team_payload))
            else:
                raise RuntimeError(f"Unexpected endpoint: {type(ep).__name__}")
        return out

    mocker.patch("fastbreak.clients.nba.NBAClient.get_many", fake_get_many)

    async def run() -> None:
        async with NBAClient() as client:
            with pytest.raises(ValueError, match="No games found for player_id"):
                await project_player(
                    client,
                    player_id=2544,
                    player_name="LeBron James",
                    opponent_team_id=1610612743,
                    is_home=True,
                    game_date=date(2026, 5, 7),
                    season="2025-26",
                    days_rest=1,
                )

    anyio.run(run)


def test_project_player_raises_on_missing_team(mocker) -> None:
    """ValueError when the opponent team_id is absent from TeamEstimatedMetrics."""
    import anyio
    from datetime import date

    from fastbreak.clients.nba import NBAClient
    from fastbreak.projections import project_player

    # 3-game log for player 2544
    game_rows = [
        [
            f"002250000{i:02d}",
            2544,
            "22025",
            f"2025-12-{i + 1:02d}",
            "LAL vs. DEN",
            "W",
            35,
            10,
            20,
            0.5,
            2,
            5,
            0.4,
            5,
            6,
            0.833,
            1,
            6,
            7,
            8,
            1,
            1,
            3,
            2,
            27,
            5,
            0,
        ]
        for i in range(3)
    ]
    game_log_payload = {
        "resultSets": [
            {
                "name": "PlayerGameLog",
                "headers": [
                    "Game_ID",
                    "Player_ID",
                    "SEASON_ID",
                    "GAME_DATE",
                    "MATCHUP",
                    "WL",
                    "MIN",
                    "FGM",
                    "FGA",
                    "FG_PCT",
                    "FG3M",
                    "FG3A",
                    "FG3_PCT",
                    "FTM",
                    "FTA",
                    "FT_PCT",
                    "OREB",
                    "DREB",
                    "REB",
                    "AST",
                    "STL",
                    "BLK",
                    "TOV",
                    "PF",
                    "PTS",
                    "PLUS_MINUS",
                    "VIDEO_AVAILABLE",
                ],
                "rowSet": game_rows,
            }
        ]
    }
    # Team payload does NOT contain team_id=9999 (the opponent we'll ask for)
    team_payload = {
        "resultSet": {
            "name": "TeamEstimatedMetrics",
            "headers": [
                "TEAM_NAME",
                "TEAM_ID",
                "GP",
                "W",
                "L",
                "W_PCT",
                "MIN",
                "E_OFF_RATING",
                "E_DEF_RATING",
                "E_NET_RATING",
                "E_PACE",
                "E_AST_RATIO",
                "E_OREB_PCT",
                "E_DREB_PCT",
                "E_REB_PCT",
                "E_TM_TOV_PCT",
                "GP_RANK",
                "W_RANK",
                "L_RANK",
                "W_PCT_RANK",
                "MIN_RANK",
                "E_OFF_RATING_RANK",
                "E_DEF_RATING_RANK",
                "E_NET_RATING_RANK",
                "E_AST_RATIO_RANK",
                "E_OREB_PCT_RANK",
                "E_DREB_PCT_RANK",
                "E_REB_PCT_RANK",
                "E_TM_TOV_PCT_RANK",
                "E_PACE_RANK",
            ],
            "rowSet": [
                [
                    "Denver Nuggets",
                    1610612743,
                    82,
                    50,
                    32,
                    0.610,
                    3500.0,
                    118.0,
                    110.0,
                    8.0,
                    100.0,
                    1.8,
                    0.25,
                    0.75,
                    0.5,
                    0.13,
                    1,
                    5,
                    5,
                    5,
                    15,
                    3,
                    5,
                    4,
                    10,
                    12,
                    13,
                    11,
                    20,
                    18,
                ],
            ],
        }
    }

    async def fake_get_many(self, endpoints, **kwargs):
        from fastbreak.endpoints import PlayerGameLog, TeamEstimatedMetrics

        out = []
        for ep in endpoints:
            if isinstance(ep, PlayerGameLog):
                out.append(ep.response_model.model_validate(game_log_payload))
            elif isinstance(ep, TeamEstimatedMetrics):
                out.append(ep.response_model.model_validate(team_payload))
            else:
                raise RuntimeError(f"Unexpected endpoint: {type(ep).__name__}")
        return out

    mocker.patch("fastbreak.clients.nba.NBAClient.get_many", fake_get_many)

    async def run() -> None:
        async with NBAClient() as client:
            with pytest.raises(ValueError, match="Opponent team_id=9999 not found"):
                await project_player(
                    client,
                    player_id=2544,
                    player_name="LeBron James",
                    opponent_team_id=9999,  # not in team_payload
                    is_home=True,
                    game_date=date(2026, 5, 7),
                    season="2025-26",
                    days_rest=1,
                )

    anyio.run(run)


def test_project_player_raises_on_missing_def_rating(mocker) -> None:
    """ValueError when the opponent's e_def_rating is None."""
    import anyio
    from datetime import date

    from fastbreak.clients.nba import NBAClient
    from fastbreak.projections import project_player

    game_rows = [
        [
            f"002250000{i:02d}",
            2544,
            "22025",
            f"2025-12-{i + 1:02d}",
            "LAL vs. DEN",
            "W",
            35,
            10,
            20,
            0.5,
            2,
            5,
            0.4,
            5,
            6,
            0.833,
            1,
            6,
            7,
            8,
            1,
            1,
            3,
            2,
            27,
            5,
            0,
        ]
        for i in range(3)
    ]
    game_log_payload = {
        "resultSets": [
            {
                "name": "PlayerGameLog",
                "headers": [
                    "Game_ID",
                    "Player_ID",
                    "SEASON_ID",
                    "GAME_DATE",
                    "MATCHUP",
                    "WL",
                    "MIN",
                    "FGM",
                    "FGA",
                    "FG_PCT",
                    "FG3M",
                    "FG3A",
                    "FG3_PCT",
                    "FTM",
                    "FTA",
                    "FT_PCT",
                    "OREB",
                    "DREB",
                    "REB",
                    "AST",
                    "STL",
                    "BLK",
                    "TOV",
                    "PF",
                    "PTS",
                    "PLUS_MINUS",
                    "VIDEO_AVAILABLE",
                ],
                "rowSet": game_rows,
            }
        ]
    }
    # Opponent team 1610612743 present, but E_DEF_RATING is None
    team_payload = {
        "resultSet": {
            "name": "TeamEstimatedMetrics",
            "headers": [
                "TEAM_NAME",
                "TEAM_ID",
                "GP",
                "W",
                "L",
                "W_PCT",
                "MIN",
                "E_OFF_RATING",
                "E_DEF_RATING",
                "E_NET_RATING",
                "E_PACE",
                "E_AST_RATIO",
                "E_OREB_PCT",
                "E_DREB_PCT",
                "E_REB_PCT",
                "E_TM_TOV_PCT",
                "GP_RANK",
                "W_RANK",
                "L_RANK",
                "W_PCT_RANK",
                "MIN_RANK",
                "E_OFF_RATING_RANK",
                "E_DEF_RATING_RANK",
                "E_NET_RATING_RANK",
                "E_AST_RATIO_RANK",
                "E_OREB_PCT_RANK",
                "E_DREB_PCT_RANK",
                "E_REB_PCT_RANK",
                "E_TM_TOV_PCT_RANK",
                "E_PACE_RANK",
            ],
            "rowSet": [
                [
                    "Denver Nuggets",
                    1610612743,
                    82,
                    50,
                    32,
                    0.610,
                    3500.0,
                    118.0,
                    None,
                    8.0,
                    100.0,
                    1.8,
                    0.25,
                    0.75,
                    0.5,
                    0.13,
                    1,
                    5,
                    5,
                    5,
                    15,
                    3,
                    5,
                    4,
                    10,
                    12,
                    13,
                    11,
                    20,
                    18,
                ],
            ],
        }
    }

    async def fake_get_many(self, endpoints, **kwargs):
        from fastbreak.endpoints import PlayerGameLog, TeamEstimatedMetrics

        out = []
        for ep in endpoints:
            if isinstance(ep, PlayerGameLog):
                out.append(ep.response_model.model_validate(game_log_payload))
            elif isinstance(ep, TeamEstimatedMetrics):
                out.append(ep.response_model.model_validate(team_payload))
            else:
                raise RuntimeError(f"Unexpected endpoint: {type(ep).__name__}")
        return out

    mocker.patch("fastbreak.clients.nba.NBAClient.get_many", fake_get_many)

    async def run() -> None:
        async with NBAClient() as client:
            with pytest.raises(ValueError, match="invalid e_def_rating"):
                await project_player(
                    client,
                    player_id=2544,
                    player_name="LeBron James",
                    opponent_team_id=1610612743,
                    is_home=True,
                    game_date=date(2026, 5, 7),
                    season="2025-26",
                    days_rest=1,
                )

    anyio.run(run)


def test_project_player_rejects_partial_priors() -> None:
    """`priors` must be complete or omitted — no partial-dict merging.

    Validation fires before any API call, so this test needs no mock.
    """
    import anyio
    from datetime import date

    from fastbreak.clients.nba import NBAClient
    from fastbreak.projections import project_player
    from fastbreak.projections_priors import StatPrior

    partial = {
        "pts": StatPrior(
            tau_sq=1.0, sigma_sq=1.0, season="2025-26", n_players=10, n_games=300
        ),
    }

    async def run() -> None:
        async with NBAClient() as client:
            with pytest.raises(ValueError, match="priors must contain all of"):
                await project_player(
                    client,
                    player_id=2544,
                    player_name="LBJ",
                    opponent_team_id=1610612743,
                    is_home=True,
                    game_date=date(2026, 5, 7),
                    season="2025-26",
                    days_rest=1,
                    rolling_n=10,
                    priors=partial,  # type: ignore[arg-type]
                )

    anyio.run(run)


def test_project_player_uses_provided_priors(mocker) -> None:  # type: ignore[no-untyped-def]
    """When `priors` is provided, project_player uses it instead of STAT_PRIORS.

    We verify the override took effect by passing a `priors` dict whose
    tau_sq is enormous compared to sigma_sq — that pushes the EB weight
    near 1.0, so the blended mean ≈ rolling_mean (modulo small adjustments).
    Compared against the same call with default priors, the projected mean
    should differ noticeably for at least one stat.
    """
    import anyio
    from datetime import date

    from fastbreak.clients.nba import NBAClient
    from fastbreak.projections import STATS, project_player
    from fastbreak.projections_priors import StatPrior

    # 20 games of high scoring (~30 pts) — rolling_mean will diverge from
    # season_mean if the player has any variance pattern. We make games
    # alternate to ensure rolling != season.
    game_rows = [
        [
            f"002250000{i:02d}",
            2544,
            "22025",
            f"2025-12-{i + 1:02d}",
            "LAL vs. DEN",
            "W",
            35,
            10,
            20,
            0.5,
            2,
            5,
            0.4,
            5,
            6,
            0.833,
            1,
            6,
            7,
            8,
            1,
            1,
            3,
            2,
            # PTS alternates 30 / 20 so recent-10 mean differs from season mean
            30 if i < 10 else 20,
            5,
            0,
        ]
        for i in range(20)
    ]
    game_log_payload = {
        "resultSets": [
            {
                "name": "PlayerGameLog",
                "headers": [
                    "Game_ID",
                    "Player_ID",
                    "SEASON_ID",
                    "GAME_DATE",
                    "MATCHUP",
                    "WL",
                    "MIN",
                    "FGM",
                    "FGA",
                    "FG_PCT",
                    "FG3M",
                    "FG3A",
                    "FG3_PCT",
                    "FTM",
                    "FTA",
                    "FT_PCT",
                    "OREB",
                    "DREB",
                    "REB",
                    "AST",
                    "STL",
                    "BLK",
                    "TOV",
                    "PF",
                    "PTS",
                    "PLUS_MINUS",
                    "VIDEO_AVAILABLE",
                ],
                "rowSet": game_rows,
            }
        ]
    }
    team_est_payload = {
        "resultSet": {
            "name": "TeamEstimatedMetrics",
            "headers": [
                "TEAM_NAME",
                "TEAM_ID",
                "GP",
                "W",
                "L",
                "W_PCT",
                "MIN",
                "E_OFF_RATING",
                "E_DEF_RATING",
                "E_NET_RATING",
                "E_PACE",
                "E_AST_RATIO",
                "E_OREB_PCT",
                "E_DREB_PCT",
                "E_REB_PCT",
                "E_TM_TOV_PCT",
                "GP_RANK",
                "W_RANK",
                "L_RANK",
                "W_PCT_RANK",
                "MIN_RANK",
                "E_OFF_RATING_RANK",
                "E_DEF_RATING_RANK",
                "E_NET_RATING_RANK",
                "E_PACE_RANK",
                "E_AST_RATIO_RANK",
                "E_OREB_PCT_RANK",
                "E_DREB_PCT_RANK",
                "E_REB_PCT_RANK",
                "E_TM_TOV_PCT_RANK",
            ],
            "rowSet": [
                [
                    "Denver Nuggets",
                    1610612743,
                    82,
                    50,
                    32,
                    0.61,
                    3940,
                    115.0,
                    110.0,
                    5.0,
                    100.0,
                    1.7,
                    0.24,
                    0.74,
                    0.49,
                    0.14,
                    2,
                    10,
                    10,
                    10,
                    16,
                    8,
                    10,
                    10,
                    12,
                    14,
                    15,
                    13,
                    18,
                    22,
                ],
            ],
        }
    }

    async def fake_get_many(self, endpoints, **kwargs):  # type: ignore[no-untyped-def]
        from fastbreak.endpoints import PlayerGameLog, TeamEstimatedMetrics

        out = []
        for ep in endpoints:
            if isinstance(ep, PlayerGameLog):
                out.append(ep.response_model.model_validate(game_log_payload))
            elif isinstance(ep, TeamEstimatedMetrics):
                out.append(ep.response_model.model_validate(team_est_payload))
            else:
                msg = f"Unexpected endpoint: {type(ep).__name__}"
                raise RuntimeError(msg)
        return out

    mocker.patch("fastbreak.clients.nba.NBAClient.get_many", fake_get_many)

    # Heavy-rolling priors: huge tau_sq, tiny sigma_sq → EB weight ≈ 1.
    heavy_rolling = {
        stat: StatPrior(
            tau_sq=10_000.0,
            sigma_sq=0.001,
            season="2025-26",
            n_players=100,
            n_games=5000,
        )
        for stat in STATS
    }

    async def run() -> None:
        async with NBAClient() as client:
            default = await project_player(
                client,
                player_id=2544,
                player_name="LBJ",
                opponent_team_id=1610612743,
                is_home=True,
                game_date=date(2026, 5, 7),
                season="2025-26",
                days_rest=1,
                rolling_n=10,
            )
            override = await project_player(
                client,
                player_id=2544,
                player_name="LBJ",
                opponent_team_id=1610612743,
                is_home=True,
                game_date=date(2026, 5, 7),
                season="2025-26",
                days_rest=1,
                rolling_n=10,
                priors=heavy_rolling,
            )
        # The override priors must take effect — i.e. produce a different
        # projected mean than the default. The default already weights 10
        # games heavily, so the difference is small; we just need any
        # observable change to prove the priors kwarg was threaded through.
        assert override.stats["pts"].mean != default.stats["pts"].mean
        # Direction check: rolling_mean (30) > season_mean (25), and
        # heavy_rolling has weight ≈ 1, so override blends closer to 30.
        # Default's tau_sq is smaller, so default blends slightly toward 25.
        assert override.stats["pts"].mean > default.stats["pts"].mean

    anyio.run(run)


def test_compute_priors_for_season_rejects_invalid_thresholds() -> None:
    """min_games < 1 and min_minutes < 0 each fail before any API call."""
    import anyio

    from fastbreak.clients.nba import NBAClient
    from fastbreak.projections import compute_priors_for_season

    async def run() -> None:
        async with NBAClient() as client:
            with pytest.raises(ValueError, match="min_games must be >= 1"):
                await compute_priors_for_season(client, season="2025-26", min_games=0)
            with pytest.raises(ValueError, match="min_minutes must be >= 0"):
                await compute_priors_for_season(
                    client, season="2025-26", min_minutes=-1.0
                )

    anyio.run(run)


def test_compute_priors_from_logs_returns_complete_mapping() -> None:
    """The pure helper exercised directly: 12 synthetic players × 5 games each
    yields a mapping with all four STATS keys, each a valid StatPrior."""
    from fastbreak.projections import STATS, _compute_priors_from_logs

    class _FakeGame:
        def __init__(self, pts: float, reb: float, ast: float, fg3m: float) -> None:
            self.pts = pts
            self.reb = reb
            self.ast = ast
            self.fg3m = fg3m

    # Vary stats per player so variance is non-degenerate (above 1e-6 floor).
    logs = {
        100 + i: [
            _FakeGame(
                pts=20.0 + i + g,
                reb=5.0 + (i * 0.3) + (g * 0.2),
                ast=4.0 + (i * 0.4) + (g * 0.1),
                fg3m=2.0 + (i * 0.2) + (g * 0.3),
            )
            for g in range(5)
        ]
        for i in range(12)
    }

    priors = _compute_priors_from_logs(logs, season="2025-26")  # type: ignore[arg-type]
    assert set(priors.keys()) == set(STATS)
    for stat, prior in priors.items():
        assert prior.tau_sq > 0, stat
        assert prior.sigma_sq > 0, stat
        assert prior.n_players == 12, stat
        assert prior.n_games == 60, stat
        assert prior.season == "2025-26", stat


def test_compute_priors_from_logs_rejects_insufficient_pool() -> None:
    """Fewer than 10 qualifying players (each with >=2 games) fails per stat."""
    from fastbreak.projections import _compute_priors_from_logs

    class _FakeGame:
        def __init__(self, pts: float) -> None:
            self.pts = pts
            self.reb = 5.0
            self.ast = 4.0
            self.fg3m = 2.0

    logs = {i: [_FakeGame(pts=20.0 + i + g) for g in range(5)] for i in range(5)}

    with pytest.raises(ValueError, match="insufficient pool"):
        _compute_priors_from_logs(logs, season="2025-26")  # type: ignore[arg-type]


def test_compute_priors_for_season_returns_immutable_mapping() -> None:
    """The returned mapping must be MappingProxyType so callers can't mutate
    it and accidentally poison subsequent project_player calls."""
    from fastbreak.projections import _compute_priors_from_logs

    class _FakeGame:
        def __init__(self, pts: float, reb: float, ast: float, fg3m: float) -> None:
            self.pts = pts
            self.reb = reb
            self.ast = ast
            self.fg3m = fg3m

    # Vary every stat so per-player variance is non-zero for all four
    # (otherwise StatPrior.__post_init__ rejects tau_sq=0).
    logs = {
        100 + i: [
            _FakeGame(
                pts=20.0 + i + g,
                reb=5.0 + (i * 0.3) + (g * 0.2),
                ast=4.0 + (i * 0.4) + (g * 0.1),
                fg3m=2.0 + (i * 0.2) + (g * 0.3),
            )
            for g in range(5)
        ]
        for i in range(12)
    }
    priors = _compute_priors_from_logs(logs, season="2025-26")  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        priors["pts"] = priors["reb"]  # type: ignore[index]
