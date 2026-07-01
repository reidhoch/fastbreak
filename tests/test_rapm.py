"""Tests for fastbreak.rapm (Regularized Adjusted Plus-Minus)."""

import numpy as np
import pytest

from fastbreak.rapm import (
    Stint,
    build_design_matrix,
    RAPMRating,
    RAPMResult,
    compute_rapm,
    rapm_leaders,
)


def test_build_design_matrix_shape_and_signs():
    stints = [
        Stint(
            home_player_ids=(1, 2, 3, 4, 5),
            away_player_ids=(6, 7, 8, 9, 10),
            possessions=2.0,
            point_diff=4,
        ),
        Stint(
            home_player_ids=(1, 2, 3, 4, 11),
            away_player_ids=(6, 7, 8, 9, 12),
            possessions=4.0,
            point_diff=-2,
        ),
    ]
    X, y, w, player_ids = build_design_matrix(stints)

    # 12 unique players, 2 stints
    assert player_ids == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    assert X.shape == (2, 12)

    dense = X.toarray()
    col = {pid: i for i, pid in enumerate(player_ids)}
    # Stint 0: home 1-5 are +1, away 6-10 are -1, others 0
    assert dense[0, col[1]] == 1.0
    assert dense[0, col[6]] == -1.0
    assert dense[0, col[11]] == 0.0

    # y = point_diff / possessions * 100
    assert y[0] == pytest.approx(4 / 2.0 * 100)  # 200.0
    assert y[1] == pytest.approx(-2 / 4.0 * 100)  # -50.0
    # sample weight = possessions
    assert w[0] == pytest.approx(2.0)
    assert w[1] == pytest.approx(4.0)


def _balanced_stints():
    """Synthetic data with planted true ratings.

    True ratings (net pts/100): player 1 = +10, player 2 = -10, others 0.
    Each stint's point_diff is constructed so that the per-100 margin equals
    the sum of home true ratings minus the sum of away true ratings.
    """
    true = {1: 10.0, 2: -10.0, 3: 0.0, 4: 0.0, 5: 0.0, 6: 0.0, 7: 0.0, 8: 0.0}
    poss = 100.0  # makes per-100 margin == raw point_diff

    def margin(home, away):
        return int(round(sum(true[p] for p in home) - sum(true[p] for p in away)))

    pairs = [
        ((1, 3, 4, 5, 6), (2, 7, 8, 3, 4)),
        ((1, 7, 8, 3, 4), (2, 5, 6, 7, 8)),
        ((1, 5, 6, 7, 8), (2, 3, 4, 5, 6)),
        ((2, 3, 4, 5, 6), (1, 7, 8, 3, 4)),
        ((3, 4, 5, 6, 7), (8, 1, 2, 3, 4)),
        ((8, 1, 2, 3, 4), (3, 4, 5, 6, 7)),
    ]
    return [
        Stint(
            home_player_ids=h,
            away_player_ids=a,
            possessions=poss,
            point_diff=margin(h, a),
        )
        for h, a in pairs
    ]


def test_compute_rapm_recovers_signal_at_low_lambda():
    stints = _balanced_stints()
    result = compute_rapm(stints, lambda_=0.01)

    r1 = result.rating_for(1)
    r2 = result.rating_for(2)
    assert r1 is not None and r2 is not None
    # Player 1 is the strongest positive, player 2 the strongest negative.
    assert r1.rapm > 1.0
    assert r2.rapm < -1.0
    assert r1.rapm > r2.rapm


def test_compute_rapm_result_metadata():
    stints = _balanced_stints()
    result = compute_rapm(stints, lambda_=100.0)
    assert isinstance(result, RAPMResult)
    assert result.n_stints == len(stints)
    assert result.n_players == 8
    assert result.alpha == pytest.approx(100.0)
    # ratings sorted by rapm descending
    rapms = [r.rapm for r in result.ratings]
    assert rapms == sorted(rapms, reverse=True)
    # per-player accounting
    r1 = result.rating_for(1)
    assert r1.stint_count >= 1
    assert r1.possessions > 0.0


def test_compute_rapm_empty_returns_empty_result():
    result = compute_rapm([])
    assert result.ratings == ()
    assert result.n_stints == 0
    assert result.n_players == 0


def test_compute_rapm_rejects_nonpositive_possessions():
    bad = [
        Stint(
            home_player_ids=(1, 2, 3, 4, 5),
            away_player_ids=(6, 7, 8, 9, 10),
            possessions=0.0,
            point_diff=3,
        )
    ]
    with pytest.raises(ValueError, match="possessions"):
        compute_rapm(bad)


def test_rating_for_unknown_player_is_none():
    result = compute_rapm(_balanced_stints(), lambda_=100.0)
    assert result.rating_for(999) is None


def test_compute_rapm_cv_selects_alpha_from_grid():
    stints = _balanced_stints()
    grid = [1.0, 10.0, 100.0, 1000.0]
    result = compute_rapm(stints, alphas=grid)
    assert result.alpha in grid


def test_compute_rapm_empty_alphas_raises():
    with pytest.raises(ValueError, match="alphas"):
        compute_rapm(_balanced_stints(), alphas=[])


def test_larger_lambda_shrinks_spread():
    stints = _balanced_stints()
    small = compute_rapm(stints, lambda_=1.0)
    large = compute_rapm(stints, lambda_=100000.0)

    def spread(res):
        vals = [r.rapm for r in res.ratings]
        return max(vals) - min(vals)

    assert spread(large) < spread(small)


def test_rapm_leaders_top_n_and_sort():
    result = compute_rapm(_balanced_stints(), lambda_=100.0)
    leaders = rapm_leaders(result, top_n=3)
    assert len(leaders) == 3
    rapms = [r.rapm for r in leaders]
    assert rapms == sorted(rapms, reverse=True)
    assert leaders[0].player_id == 1  # strongest positive


def test_rapm_leaders_min_possessions_filter():
    result = compute_rapm(_balanced_stints(), lambda_=100.0)
    high = max(r.possessions for r in result.ratings)
    filtered = rapm_leaders(result, top_n=100, min_possessions=high + 1.0)
    assert filtered == []


def test_public_exports():
    import fastbreak

    assert fastbreak.Stint is Stint
    assert fastbreak.compute_rapm is compute_rapm
    assert fastbreak.rapm_leaders is rapm_leaders
    for name in ("RAPMRating", "RAPMResult", "build_design_matrix"):
        assert name in fastbreak.__all__


def test_compute_rapm_rejects_negative_lambda():
    stints = _balanced_stints()
    with pytest.raises(ValueError, match="lambda_"):
        compute_rapm(stints, lambda_=-1.0)


def test_compute_rapm_rejects_nonfinite_lambda():
    stints = _balanced_stints()
    with pytest.raises(ValueError, match="lambda_"):
        compute_rapm(stints, lambda_=float("nan"))
    with pytest.raises(ValueError, match="lambda_"):
        compute_rapm(stints, lambda_=float("inf"))


def test_validate_rejects_nonfinite_possessions():
    bad_nan = [
        Stint(
            home_player_ids=(1, 2, 3, 4, 5),
            away_player_ids=(6, 7, 8, 9, 10),
            possessions=float("nan"),
            point_diff=3,
        )
    ]
    with pytest.raises(ValueError, match="possessions"):
        compute_rapm(bad_nan)

    bad_inf = [
        Stint(
            home_player_ids=(1, 2, 3, 4, 5),
            away_player_ids=(6, 7, 8, 9, 10),
            possessions=float("inf"),
            point_diff=3,
        )
    ]
    with pytest.raises(ValueError, match="possessions"):
        compute_rapm(bad_inf)


def test_rapm_leaders_negative_top_n_returns_empty():
    result = compute_rapm(_balanced_stints(), lambda_=100.0)
    leaders = rapm_leaders(result, top_n=-1)
    assert leaders == []
