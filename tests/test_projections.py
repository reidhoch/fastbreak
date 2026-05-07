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

    with pytest.raises(ValueError, match="stdev must be positive"):
        normal_sf(x=0.0, mean=0.0, stdev=0.0)


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

    with pytest.raises(ValueError, match="lam must be non-negative"):
        poisson_sf(line=0.0, lam=-0.1)


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
            with pytest.raises(ValueError, match="missing e_def_rating"):
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
