"""Regenerate Empirical Bayes priors for fastbreak.projections.

Usage:
    uv run python scripts/compute_projection_priors.py

What it does:
    1. Calls ``fastbreak.projections.compute_priors_for_season`` to fetch
       LeagueDashPlayerStats, identify qualifying players, and compute
       between-/within-player variances per stat.
    2. Rewrites ``src/fastbreak/projections_priors.py`` with the real numbers.

This is a one-shot tool — not imported anywhere else in the library.
The compute logic itself lives in the library so callers can also
generate priors at runtime without re-running this script.
"""

from __future__ import annotations

import asyncio
import math
from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING, Final

from fastbreak.clients.nba import NBAClient
from fastbreak.projections import STATS, compute_priors_for_season

if TYPE_CHECKING:
    from collections.abc import Mapping

    from fastbreak.projections import ProjectionStat
    from fastbreak.projections_priors import StatPrior

SEASON: Final = "2025-26"
MIN_GAMES: Final = 30
MIN_MINUTES: Final = 15.0


def _write_priors_module(
    priors: Mapping[ProjectionStat, StatPrior],
) -> None:
    # Validate before writing: a zero/NaN/inf variance silently disables
    # shrinkage at projection time (and the .6f formatter would mask
    # near-zero values as 0.000000). StatPrior.__post_init__ already
    # rejects non-finite/non-positive variance, but the .6f truncation
    # threshold is stricter than "> 0", so re-check here.
    min_variance = 1e-6
    for stat in STATS:
        prior = priors[stat]
        for name, val in (("tau_sq", prior.tau_sq), ("sigma_sq", prior.sigma_sq)):
            if not math.isfinite(val) or val < min_variance:
                msg = (
                    f"computed {name} for {stat!r} is degenerate: {val!r} "
                    f"(must be finite and >= {min_variance})"
                )
                raise ValueError(msg)
    rows = []
    for stat in STATS:
        prior = priors[stat]
        rows.append(
            f'    "{stat}": StatPrior(tau_sq={prior.tau_sq:.6f}, '
            f"sigma_sq={prior.sigma_sq:.6f}, "
            f'season="{prior.season}", n_players={prior.n_players}, '
            f"n_games={prior.n_games}),"
        )
    content = dedent(
        '''\
        """Empirical Bayes priors for fastbreak.projections.

        This file is data, not logic. Regenerate via:
            uv run python scripts/compute_projection_priors.py

        Do not edit by hand — changes here will be overwritten.
        """

        from __future__ import annotations

        import math
        from dataclasses import dataclass
        from typing import Literal


        @dataclass(frozen=True, slots=True)
        class StatPrior:
            """Empirical Bayes prior for one stat."""

            tau_sq: float
            sigma_sq: float
            season: str
            n_players: int
            n_games: int

            def __post_init__(self) -> None:
                # Catch corruption at import time rather than at projection time:
                # NaN/inf would silently propagate through empirical_bayes_blend, and
                # zero/negative variance would degenerate the shrinkage to season_mean.
                for name, val in (("tau_sq", self.tau_sq), ("sigma_sq", self.sigma_sq)):
                    if not math.isfinite(val) or val <= 0:
                        msg = f"{name} must be finite and positive, got {val!r}"
                        raise ValueError(msg)
                if self.n_players < 1:
                    msg = f"n_players must be >= 1, got {self.n_players}"
                    raise ValueError(msg)
                if self.n_games < 1:
                    msg = f"n_games must be >= 1, got {self.n_games}"
                    raise ValueError(msg)
                if not self.season:
                    msg = "season must be a non-empty string"
                    raise ValueError(msg)


        STAT_PRIORS: dict[Literal["pts", "reb", "ast", "fg3m"], StatPrior] = {
        '''
    )
    content += "\n".join(rows) + "\n}\n"
    target = (
        Path(__file__).resolve().parent.parent
        / "src"
        / "fastbreak"
        / "projections_priors.py"
    )
    # Atomic write: a Ctrl-C / OOM / disk-full between target.open() and the
    # first flush would otherwise leave projections_priors.py truncated and
    # break every subsequent `from fastbreak.projections import ...`.
    tmp = target.with_suffix(target.suffix + ".tmp")
    tmp.write_text(content)
    tmp.replace(target)


async def main() -> None:
    # request_delay paces requests inside get_many() slots to avoid 429/timeouts
    # when fetching hundreds of game logs back-to-back.
    async with NBAClient(request_delay=1.0) as client:
        priors = await compute_priors_for_season(
            client,
            season=SEASON,
            min_games=MIN_GAMES,
            min_minutes=MIN_MINUTES,
        )
        _write_priors_module(priors)


if __name__ == "__main__":
    asyncio.run(main())
