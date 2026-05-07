"""Live-API integration test for fastbreak.projections.

Run with:  uv run pytest -m live_api tests/test_projections_live.py
Skipped by default; requires network.
"""

from __future__ import annotations

from datetime import date

import pytest

from fastbreak.clients.nba import NBAClient
from fastbreak.projections import project_player


@pytest.mark.live_api
async def test_project_shai_vs_nuggets() -> None:
    async with NBAClient() as client:
        result = await project_player(
            client,
            player_id=1628983,  # Shai Gilgeous-Alexander
            player_name="Shai Gilgeous-Alexander",
            opponent_team_id=1610612743,  # Denver Nuggets
            is_home=True,
            game_date=date(2026, 5, 7),
            season="2025-26",
            days_rest=1,
            rolling_n=10,
        )

    assert set(result.stats.keys()) == {"pts", "reb", "ast", "fg3m"}
    pts = result.stats["pts"]
    reb = result.stats["reb"]
    ast = result.stats["ast"]
    fg3m = result.stats["fg3m"]

    # League-sane ranges.
    assert 5.0 <= pts.mean <= 50.0
    assert 0.0 <= reb.mean <= 25.0
    assert 0.0 <= ast.mean <= 20.0
    assert 0.0 <= fg3m.mean <= 10.0

    # prob_over saturation bounds — sanity at extremes.
    for sp in result.stats.values():
        assert sp.prob_over(-1000.0) == pytest.approx(1.0, abs=1e-6)
        assert sp.prob_over(1000.0) == pytest.approx(0.0, abs=1e-6)

    # Empirical Bayes invariant: blended mean near rolling/season, within
    # adjustment slack. Adjustments can push up to ~19% (opp 0.15 + rest 0.04).
    for sp in result.stats.values():
        lo, hi = sorted([sp.rolling_mean, sp.season_mean])
        assert lo * 0.80 <= sp.mean <= hi * 1.20
