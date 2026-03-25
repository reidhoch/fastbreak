"""Estimated advanced metrics examples.

Part 1 — pure computation (no client): demonstrate rank_estimated_metrics and
         find_player / find_team with mock data built inline.
Part 2 — live API: fetch all player estimated metrics and look up a single player
         (Tyrese Haliburton, player_id=1641705).
Part 3 — live API: fetch all team estimated metrics and look up a single team
         (Indiana Pacers, team_id=1610612754).
Part 4 — live API: build estimated leaderboards (top 10 by net rating, then
         top 5 by offensive rating) using rank_estimated_metrics.

Run:
    uv run python examples/estimated.py
"""

import asyncio

from fastbreak.clients import NBAClient
from fastbreak.estimated import (
    find_player,
    find_team,
    get_player_estimated_metrics,
    get_team_estimated_metrics,
    rank_estimated_metrics,
)
from fastbreak.models.player_estimated_metrics import PlayerEstimatedMetric
from fastbreak.models.team_estimated_metrics import TeamEstimatedMetric

_SEASON = "2025-26"


def _fmt(val: float | None, spec: str = ".1f") -> str:
    """Format a float, returning 'N/A' when None."""
    return format(val, spec) if val is not None else "N/A"


_MOCK_PLAYERS = [
    PlayerEstimatedMetric.model_validate(
        {
            "PLAYER_ID": 1641705,
            "PLAYER_NAME": "Tyrese Haliburton",
            "GP": 55,
            "W": 30,
            "L": 25,
            "W_PCT": 0.545,
            "MIN": 32.0,
            "E_OFF_RATING": 118.2,
            "E_DEF_RATING": 113.4,
            "E_NET_RATING": 4.8,
            "E_AST_RATIO": 41.3,
            "E_OREB_PCT": 0.021,
            "E_DREB_PCT": 0.148,
            "E_REB_PCT": 0.087,
            "E_TOV_PCT": 14.2,
            "E_USG_PCT": 0.261,
            "E_PACE": 101.7,
            "GP_RANK": 20,
            "W_RANK": 18,
            "L_RANK": 22,
            "W_PCT_RANK": 17,
            "MIN_RANK": 15,
            "E_OFF_RATING_RANK": 18,
            "E_DEF_RATING_RANK": 95,
            "E_NET_RATING_RANK": 22,
            "E_AST_RATIO_RANK": 3,
            "E_OREB_PCT_RANK": 180,
            "E_DREB_PCT_RANK": 210,
            "E_REB_PCT_RANK": 195,
            "E_TOV_PCT_RANK": 120,
            "E_USG_PCT_RANK": 45,
            "E_PACE_RANK": 12,
        }
    ),
    PlayerEstimatedMetric.model_validate(
        {
            "PLAYER_ID": 203999,
            "PLAYER_NAME": "Nikola Jokić",
            "GP": 60,
            "W": 38,
            "L": 22,
            "W_PCT": 0.633,
            "MIN": 33.0,
            "E_OFF_RATING": 127.5,
            "E_DEF_RATING": 114.1,
            "E_NET_RATING": 13.4,
            "E_AST_RATIO": 36.8,
            "E_OREB_PCT": 0.118,
            "E_DREB_PCT": 0.271,
            "E_REB_PCT": 0.194,
            "E_TOV_PCT": 12.1,
            "E_USG_PCT": 0.298,
            "E_PACE": 97.2,
            "GP_RANK": 8,
            "W_RANK": 5,
            "L_RANK": 18,
            "W_PCT_RANK": 3,
            "MIN_RANK": 4,
            "E_OFF_RATING_RANK": 1,
            "E_DEF_RATING_RANK": 110,
            "E_NET_RATING_RANK": 1,
            "E_AST_RATIO_RANK": 8,
            "E_OREB_PCT_RANK": 12,
            "E_DREB_PCT_RANK": 3,
            "E_REB_PCT_RANK": 2,
            "E_TOV_PCT_RANK": 85,
            "E_USG_PCT_RANK": 15,
            "E_PACE_RANK": 88,
        }
    ),
    PlayerEstimatedMetric.model_validate(
        {
            "PLAYER_ID": 1629029,
            "PLAYER_NAME": "Luka Dončić",
            "GP": 42,
            "W": 20,
            "L": 22,
            "W_PCT": 0.476,
            "MIN": 33.0,
            "E_OFF_RATING": 124.1,
            "E_DEF_RATING": 116.8,
            "E_NET_RATING": 7.3,
            "E_AST_RATIO": 33.2,
            "E_OREB_PCT": 0.043,
            "E_DREB_PCT": 0.212,
            "E_REB_PCT": 0.130,
            "E_TOV_PCT": 16.8,
            "E_USG_PCT": 0.341,
            "E_PACE": 98.5,
            "GP_RANK": 55,
            "W_RANK": 42,
            "L_RANK": 30,
            "W_PCT_RANK": 28,
            "MIN_RANK": 60,
            "E_OFF_RATING_RANK": 3,
            "E_DEF_RATING_RANK": 155,
            "E_NET_RATING_RANK": 8,
            "E_AST_RATIO_RANK": 12,
            "E_OREB_PCT_RANK": 95,
            "E_DREB_PCT_RANK": 25,
            "E_REB_PCT_RANK": 40,
            "E_TOV_PCT_RANK": 180,
            "E_USG_PCT_RANK": 2,
            "E_PACE_RANK": 75,
        }
    ),
]

_MOCK_TEAMS = [
    TeamEstimatedMetric.model_validate(
        {
            "TEAM_ID": 1610612754,
            "TEAM_NAME": "Indiana Pacers",
            "GP": 65,
            "W": 34,
            "L": 31,
            "W_PCT": 0.523,
            "MIN": 15730.0,
            "E_OFF_RATING": 116.8,
            "E_DEF_RATING": 115.2,
            "E_NET_RATING": 1.6,
            "E_PACE": 101.3,
            "E_AST_RATIO": 19.4,
            "E_OREB_PCT": 0.234,
            "E_DREB_PCT": 0.748,
            "E_REB_PCT": 0.491,
            "E_TM_TOV_PCT": 13.8,
            "GP_RANK": 5,
            "W_RANK": 16,
            "L_RANK": 14,
            "W_PCT_RANK": 18,
            "MIN_RANK": 5,
            "E_OFF_RATING_RANK": 8,
            "E_DEF_RATING_RANK": 22,
            "E_NET_RATING_RANK": 17,
            "E_AST_RATIO_RANK": 12,
            "E_OREB_PCT_RANK": 14,
            "E_DREB_PCT_RANK": 20,
            "E_REB_PCT_RANK": 18,
            "E_TM_TOV_PCT_RANK": 18,
            "E_PACE_RANK": 2,
        }
    ),
    TeamEstimatedMetric.model_validate(
        {
            "TEAM_ID": 1610612738,
            "TEAM_NAME": "Boston Celtics",
            "GP": 65,
            "W": 45,
            "L": 20,
            "W_PCT": 0.692,
            "MIN": 15730.0,
            "E_OFF_RATING": 122.4,
            "E_DEF_RATING": 109.7,
            "E_NET_RATING": 12.7,
            "E_PACE": 97.1,
            "E_AST_RATIO": 22.1,
            "E_OREB_PCT": 0.268,
            "E_DREB_PCT": 0.796,
            "E_REB_PCT": 0.532,
            "E_TM_TOV_PCT": 11.2,
            "GP_RANK": 5,
            "W_RANK": 1,
            "L_RANK": 29,
            "W_PCT_RANK": 1,
            "MIN_RANK": 5,
            "E_OFF_RATING_RANK": 2,
            "E_DEF_RATING_RANK": 2,
            "E_NET_RATING_RANK": 1,
            "E_AST_RATIO_RANK": 5,
            "E_OREB_PCT_RANK": 4,
            "E_DREB_PCT_RANK": 3,
            "E_REB_PCT_RANK": 2,
            "E_TM_TOV_PCT_RANK": 3,
            "E_PACE_RANK": 26,
        }
    ),
]


def part1_pure_computation() -> None:
    """Part 1: pure computation with mock data — no client needed."""
    print("=" * 60)
    print("Part 1 — Pure Computation (mock data)")
    print("=" * 60)

    print("\nrank_estimated_metrics — by e_net_rating (descending):")
    ranked = rank_estimated_metrics(_MOCK_PLAYERS, by="e_net_rating", min_gp=10)
    for i, p in enumerate(ranked, 1):
        print(f"  {i}. {p.player_name:<22} net={_fmt(p.e_net_rating, '+.1f')}  gp={p.gp}")

    print("\nrank_estimated_metrics — by e_off_rating (min 30 min/g):")
    off_ranked = rank_estimated_metrics(
        _MOCK_PLAYERS, by="e_off_rating", min_minutes=30.0
    )
    for i, p in enumerate(off_ranked, 1):
        print(f"  {i}. {p.player_name:<22} off={_fmt(p.e_off_rating)}  min={p.minutes:.1f}")

    print("\nfind_player — Tyrese Haliburton (player_id=1641705):")
    hali = find_player(_MOCK_PLAYERS, player_id=1641705)
    if hali:
        print(f"  Found: {hali.player_name}")
        print(f"    e_off_rating:   {_fmt(hali.e_off_rating)}  (rank #{hali.e_off_rating_rank})")
        print(f"    e_def_rating:   {_fmt(hali.e_def_rating)}  (rank #{hali.e_def_rating_rank})")
        print(f"    e_net_rating:   {_fmt(hali.e_net_rating, '+.1f')}  (rank #{hali.e_net_rating_rank})")
        print(f"    e_ast_ratio:    {_fmt(hali.e_ast_ratio)}  (rank #{hali.e_ast_ratio_rank})")
        print(f"    e_usg_pct:      {_fmt(hali.e_usg_pct, '.1%')}")
        print(f"    minutes:        {hali.minutes:.1f} (per-game avg)")

    missing = find_player(_MOCK_PLAYERS, player_id=9999999)
    print(f"\nfind_player — unknown ID 9999999: {missing}")

    print("\nfind_team — Indiana Pacers (team_id=1610612754):")
    pacers = find_team(_MOCK_TEAMS, team_id=1610612754)
    if pacers:
        print(f"  Found: {pacers.team_name}")
        print(f"    e_net_rating:    {_fmt(pacers.e_net_rating, '+.1f')}  (rank #{pacers.e_net_rating_rank})")
        print(f"    e_pace:          {_fmt(pacers.e_pace)}  (rank #{pacers.e_pace_rank})")
        print(f"    e_tm_tov_pct:    {_fmt(pacers.e_tm_tov_pct)}")

    print("\nTeams sorted by e_net_rating (mock, best first):")
    sorted_teams = sorted(
        _MOCK_TEAMS,
        key=lambda t: t.e_net_rating if t.e_net_rating is not None else float("-inf"),
        reverse=True,
    )
    for t in sorted_teams:
        print(f"  {t.team_name:<25} net={_fmt(t.e_net_rating, '+.1f')}")


async def part2_player_metrics(
    players: list[PlayerEstimatedMetric], season: str,
) -> None:
    """Part 2: look up Haliburton from pre-fetched player metrics."""
    print("\n" + "=" * 60)
    print(f"Part 2 — Player Estimated Metrics ({season})")
    print("=" * 60)

    print(f"  Total players returned: {len(players)}")

    hali = find_player(players, player_id=1641705)
    if hali is None:
        print("  Tyrese Haliburton not found — possibly injured/inactive this season.")
        return

    print(f"\n  {hali.player_name} — {season}")
    print(f"    GP / MIN:        {hali.gp} games / {hali.minutes:.1f} min/g")
    print(f"    W-L:             {hali.wins}-{hali.losses}  ({_fmt(hali.win_pct, '.3f')})")
    print()
    print(f"    e_off_rating:    {_fmt(hali.e_off_rating)}  (league rank #{hali.e_off_rating_rank})")
    print(f"    e_def_rating:    {_fmt(hali.e_def_rating)}  (league rank #{hali.e_def_rating_rank})")
    print(f"    e_net_rating:    {_fmt(hali.e_net_rating, '+.1f')}  (league rank #{hali.e_net_rating_rank})")
    print()
    print(f"    e_ast_ratio:     {_fmt(hali.e_ast_ratio)}  (league rank #{hali.e_ast_ratio_rank})")
    print(f"    e_usg_pct:       {_fmt(hali.e_usg_pct, '.1%')}  (league rank #{hali.e_usg_pct_rank})")
    print(f"    e_tov_pct:       {_fmt(hali.e_tov_pct)}  (league rank #{hali.e_tov_pct_rank})")
    print(f"    e_pace:          {_fmt(hali.e_pace)}  (league rank #{hali.e_pace_rank})")


async def part3_team_metrics(season: str = _SEASON) -> None:
    """Part 3: fetch all team estimated metrics and look up the Pacers."""
    print("\n" + "=" * 60)
    print(f"Part 3 — Team Estimated Metrics ({season})")
    print("=" * 60)

    async with NBAClient() as client:
        teams = await get_team_estimated_metrics(client, season=season)

    print(f"  Total teams returned: {len(teams)}")

    sorted_teams = sorted(
        teams,
        key=lambda t: t.e_net_rating if t.e_net_rating is not None else float("-inf"),
        reverse=True,
    )
    print("\n  League ranked by e_net_rating:")
    print(f"  {'#':<3} {'Team':<25} {'NET':>6} {'OFF':>6} {'DEF':>6} {'PACE':>6}")
    print("  " + "-" * 53)
    for rank, t in enumerate(sorted_teams, 1):
        print(
            f"  {rank:<3} {t.team_name:<25} {_fmt(t.e_net_rating, '+.1f'):>6}"
            f" {_fmt(t.e_off_rating):>6} {_fmt(t.e_def_rating):>6} {_fmt(t.e_pace):>6}"
        )

    pacers = find_team(teams, team_id=1610612754)
    if pacers is None:
        print("\n  Indiana Pacers not found.")
        return

    print(f"\n  {pacers.team_name} — {season}")
    print(f"    GP / MIN:        {pacers.gp} games / {pacers.minutes:.0f} minutes")
    print(f"    W-L:             {pacers.wins}-{pacers.losses}  ({_fmt(pacers.win_pct, '.3f')})")
    print()
    print(f"    e_net_rating:    {_fmt(pacers.e_net_rating, '+.1f')}  (rank #{pacers.e_net_rating_rank})")
    print(f"    e_off_rating:    {_fmt(pacers.e_off_rating)}  (rank #{pacers.e_off_rating_rank})")
    print(f"    e_def_rating:    {_fmt(pacers.e_def_rating)}  (rank #{pacers.e_def_rating_rank})")
    print(f"    e_pace:          {_fmt(pacers.e_pace)}  (rank #{pacers.e_pace_rank})")
    print(f"    e_tm_tov_pct:    {_fmt(pacers.e_tm_tov_pct)}  (rank #{pacers.e_tm_tov_pct_rank})")


async def part4_estimated_leaders(
    players: list[PlayerEstimatedMetric], season: str,
) -> None:
    """Part 4: leaderboards by net rating and by offensive rating."""
    print("\n" + "=" * 60)
    print(f"Part 4 — Estimated Metric Leaders ({season})")
    print("=" * 60)

    net_leaders = rank_estimated_metrics(players, by="e_net_rating", min_gp=20)[:10]
    off_leaders = rank_estimated_metrics(
        players, by="e_off_rating", min_gp=20, min_minutes=30.0
    )[:5]

    print(f"\n  Top 10 by e_net_rating (min 20 GP) — {season}")
    print(f"  {'#':<3} {'Player':<25} {'NET':>6} {'OFF':>6} {'DEF':>6} {'GP':>4}")
    print("  " + "-" * 51)
    for rank, p in enumerate(net_leaders, 1):
        print(
            f"  {rank:<3} {p.player_name:<25} {_fmt(p.e_net_rating, '+.1f'):>6}"
            f" {_fmt(p.e_off_rating):>6} {_fmt(p.e_def_rating):>6} {p.gp:>4}"
        )

    print(f"\n  Top 5 by e_off_rating (min 20 GP, 30 min/g) — {season}")
    print(f"  {'#':<3} {'Player':<25} {'OFF':>6} {'MIN':>6} {'GP':>4}")
    print("  " + "-" * 47)
    for rank, p in enumerate(off_leaders, 1):
        print(f"  {rank:<3} {p.player_name:<25} {_fmt(p.e_off_rating):>6} {p.minutes:>6.0f} {p.gp:>4}")


async def main() -> None:
    part1_pure_computation()

    # Fetch players once; reused by Parts 2 and 4 to avoid a redundant API call.
    async with NBAClient() as client:
        players = await get_player_estimated_metrics(client, season=_SEASON)

    await part2_player_metrics(players, _SEASON)
    await part3_team_metrics(_SEASON)
    await part4_estimated_leaders(players, _SEASON)


if __name__ == "__main__":
    asyncio.run(main())
