"""Regenerate Empirical Bayes priors for fastbreak.projections.

Usage:
    uv run python scripts/compute_projection_priors.py

What it does:
    1. Pulls the league-wide player stats (LeagueDashPlayerStats) for 2025-26
       to identify qualifying players (GP >= 30, MIN per game >= 15).
    2. Downloads each qualifying player's full PlayerGameLog for the season.
    3. Computes per-player game-to-game variance (sigma_sq), averaged across
       the pool.
    4. Computes between-player variance (tau_sq) of the pool's season means.
    5. Rewrites src/fastbreak/projections_priors.py with the real numbers.

This is a one-shot tool — not imported anywhere else in the library.
"""

from __future__ import annotations

import asyncio
import statistics
from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING, Final

from fastbreak.clients.nba import NBAClient
from fastbreak.endpoints import LeagueDashPlayerStats, PlayerGameLog

if TYPE_CHECKING:
    from fastbreak.models.player_game_log import PlayerGameLogEntry

SEASON: Final = "2025-26"
MIN_GAMES: Final = 30
MIN_MINUTES: Final = 15.0
STATS: Final = ("pts", "reb", "ast", "fg3m")


async def _fetch_eligible_player_ids(client: NBAClient) -> list[int]:
    resp = await client.get(LeagueDashPlayerStats(season=SEASON))
    eligible: list[int] = []
    for p in resp.players:
        if p.gp >= MIN_GAMES and p.min >= MIN_MINUTES:
            eligible.append(p.player_id)
    return eligible


async def _fetch_all_game_logs(
    client: NBAClient, player_ids: list[int]
) -> dict[int, list[PlayerGameLogEntry]]:
    endpoints = [PlayerGameLog(player_id=pid, season=SEASON) for pid in player_ids]
    responses = await client.get_many(endpoints, max_concurrency=3)
    return {pid: resp.games for pid, resp in zip(player_ids, responses, strict=True)}


def _compute_priors(
    logs: dict[int, list[PlayerGameLogEntry]],
) -> dict[str, tuple[float, float, int, int]]:
    """Return {stat: (tau_sq, sigma_sq, n_players, n_games)}."""
    result: dict[str, tuple[float, float, int, int]] = {}
    for stat in STATS:
        per_player_means: list[float] = []
        per_player_variances: list[float] = []
        total_games = 0
        for games in logs.values():
            if len(games) < 2:
                continue
            values = [float(getattr(g, stat)) for g in games]
            per_player_means.append(statistics.fmean(values))
            per_player_variances.append(statistics.variance(values))
            total_games += len(values)
        if len(per_player_means) < 10:
            msg = f"Insufficient player pool for {stat}: {len(per_player_means)}"
            raise RuntimeError(msg)
        tau_sq = statistics.variance(per_player_means)
        sigma_sq = statistics.fmean(per_player_variances)
        result[stat] = (tau_sq, sigma_sq, len(per_player_means), total_games)
    return result


def _write_priors_module(
    priors: dict[str, tuple[float, float, int, int]],
) -> None:
    rows = []
    for stat in STATS:
        tau_sq, sigma_sq, n_players, n_games = priors[stat]
        rows.append(
            f'    "{stat}": StatPrior(tau_sq={tau_sq:.4f}, sigma_sq={sigma_sq:.4f}, '
            f'season="{SEASON}", n_players={n_players}, n_games={n_games}),'
        )
    content = dedent(
        '''\
        """Empirical Bayes priors for fastbreak.projections.

        This file is data, not logic. Regenerate via:
            uv run python scripts/compute_projection_priors.py

        Do not edit by hand — changes here will be overwritten.
        """

        from __future__ import annotations

        from dataclasses import dataclass


        @dataclass(frozen=True, slots=True)
        class StatPrior:
            """Empirical Bayes prior for one stat."""

            tau_sq: float
            sigma_sq: float
            season: str
            n_players: int
            n_games: int


        STAT_PRIORS: dict[str, StatPrior] = {
        '''
    )
    content += "\n".join(rows) + "\n}\n"
    target = (
        Path(__file__).resolve().parent.parent
        / "src"
        / "fastbreak"
        / "projections_priors.py"
    )
    target.write_text(content)


async def main() -> None:
    # request_delay paces requests inside get_many() slots to avoid 429/timeouts
    # when fetching hundreds of game logs back-to-back.
    async with NBAClient(request_delay=1.0) as client:
        player_ids = await _fetch_eligible_player_ids(client)
        logs = await _fetch_all_game_logs(client, player_ids)
        priors = _compute_priors(logs)
        for _stat, (_tau_sq, _sigma_sq, _n_players, _n_games) in priors.items():
            pass
        _write_priors_module(priors)


if __name__ == "__main__":
    asyncio.run(main())
