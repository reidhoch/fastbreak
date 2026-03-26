"""Player comparison examples.

Compares two NBA players side-by-side across box score stats, derived
efficiency metrics, and estimated advanced metrics.

Run:
    uv run python examples/compare_players.py
"""

import asyncio

from fastbreak.clients import NBAClient
from fastbreak.compare import (
    HIGHER_IS_WORSE,
    ComparisonResult,
    get_player_comparison,
    stat_leader,
)
from fastbreak.players import get_player_id

# Each metric is (label, attribute, format_spec, display_scale).
# scale=100.0 converts 0-1 fractions to human-readable percentages.
_BOX_METRICS: list[tuple[str, str, str, float]] = [
    ("PTS", "pts", ".1f", 1.0),
    ("REB", "reb", ".1f", 1.0),
    ("AST", "ast", ".1f", 1.0),
    ("STL", "stl", ".1f", 1.0),
    ("BLK", "blk", ".1f", 1.0),
    ("TOV", "tov", ".1f", 1.0),
    ("FG%", "fg_pct", ".1%", 1.0),
    ("3P%", "fg3_pct", ".1%", 1.0),
    ("FT%", "ft_pct", ".1%", 1.0),
    ("+/-", "plus_minus", ".1f", 1.0),
]

_DERIVED_METRICS: list[tuple[str, str, str, float]] = [
    ("TS%", "ts_pct", ".3f", 1.0),
    ("eFG%", "efg_pct", ".3f", 1.0),
    ("A/TO", "ast_tov", ".3f", 1.0),
    ("GmSc", "game_score", ".3f", 1.0),
    ("FTR", "ft_rate", ".3f", 1.0),
    ("3PR", "three_pt_rate", ".3f", 1.0),
]

_EST_METRICS: list[tuple[str, str, str, float]] = [
    ("ORTG", "e_off_rating", ".1f", 1.0),
    ("DRTG", "e_def_rating", ".1f", 1.0),
    ("NET", "e_net_rating", ".1f", 1.0),
    ("USG%", "e_usg_pct", ".1f", 100.0),
    ("PACE", "e_pace", ".1f", 1.0),
]


def _fmt(value: float | None, spec: str, scale: float = 1.0) -> str:
    return f"{value * scale:{spec}}" if value is not None else "N/A"


def _fmt_delta(value: float | None, spec: str, scale: float = 1.0) -> str:
    return f"{value * scale:+{spec}}" if value is not None else "N/A"


def _print_section(
    title: str,
    metrics: list[tuple[str, str, str, float]],
    result: ComparisonResult,
) -> None:
    a = result.player_a
    b = result.player_b
    print(f"\n{title:<8} {a.name:>12} {b.name:>12} {'Delta':>8} {'Leader':>12}")
    print("-" * 60)
    for label, attr, spec, scale in metrics:
        a_val = getattr(a, attr)
        b_val = getattr(b, attr)
        delta = result.deltas.get(attr)
        hiw = attr in HIGHER_IS_WORSE
        leader_id = stat_leader(a, b, attr, higher_is_worse=hiw)
        leader = (
            a.name
            if leader_id == a.player_id
            else b.name
            if leader_id == b.player_id
            else "—"
        )
        print(
            f"{label:<8} {_fmt(a_val, spec, scale):>12} "
            f"{_fmt(b_val, spec, scale):>12} "
            f"{_fmt_delta(delta, spec, scale):>8} {leader:>12}"
        )


async def compare_two_players(
    client: NBAClient,
    player_a_name: str,
    player_b_name: str,
    season: str = "2025-26",
) -> None:
    """Fetch and display a side-by-side comparison of two players."""
    pid_a = await get_player_id(client, player_a_name)
    pid_b = await get_player_id(client, player_b_name)

    if pid_a is None:
        print(f"Player not found: {player_a_name!r}")
        return
    if pid_b is None:
        print(f"Player not found: {player_b_name!r}")
        return

    result = await get_player_comparison(client, pid_a, pid_b, season=season)

    a = result.player_a
    b = result.player_b

    print(f"\nPlayer Comparison — {season} Regular Season")
    print(f"  {a.name}  vs  {b.name}")
    print("=" * 60)

    _print_section("Stat", _BOX_METRICS, result)
    _print_section("Derived", _DERIVED_METRICS, result)
    _print_section("Est.Adv", _EST_METRICS, result)

    e = result.edges
    summary = f"{a.name} leads {e.a_leads}, {b.name} leads {e.b_leads}, ties {e.ties}"
    if e.unavailable:
        summary += f", unavailable {e.unavailable}"
    print(f"\nEdge Summary: {summary}")


async def main() -> None:
    season = "2025-26"

    async with NBAClient() as client:
        await compare_two_players(client, "Jayson Tatum", "Luka Dončić", season)
        await compare_two_players(client, "Nikola Jokić", "Victor Wembanyama", season)


if __name__ == "__main__":
    asyncio.run(main())
