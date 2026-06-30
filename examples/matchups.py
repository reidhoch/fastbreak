"""Matchup analysis examples.

Demonstrates player-vs-player matchups, defensive assignments,
team matchup summaries, and per-game matchup breakdowns using
fastbreak.matchups.

Run:
    uv run python examples/matchups.py
"""

import asyncio

from fastbreak.clients import NBAClient
from fastbreak.matchups import (
    get_defensive_assignments,
    get_game_matchups,
    get_player_matchup_stats,
    get_player_vs_opponents,
    get_primary_defenders,
    get_team_matchup_summary,
    get_team_vs_opponents,
    matchup_ppp,
    rank_matchups,
    split_vs_opponent,
)
from fastbreak.seasons import get_season_from_date
from fastbreak.teams import get_team_id


async def primary_defenders_for_player(
    player_id: int, name: str, season: str | None = None
) -> None:
    """Print the top 5 defenders who guard a player the most."""
    season = season or get_season_from_date()

    async with NBAClient() as client:
        defenders = await get_primary_defenders(
            client, player_id=player_id, season=season, top_n=5
        )

    if not defenders:
        print(f"No matchup data for {name} ({season})")
        return

    print(f"\nPrimary Defenders — {name} ({season})")
    print(f"{'Defender':<25} {'Min':>5} {'Poss':>6} {'FG%':>6} {'FG3%':>6}")
    print("-" * 52)
    for d in defenders:
        fg_str = f"{d.matchup_fg_pct:.1%}" if d.matchup_fg_pct is not None else " N/A"
        fg3_str = (
            f"{d.matchup_fg3_pct:.1%}" if d.matchup_fg3_pct is not None else " N/A"
        )
        print(
            f"  {d.def_player_name:<23} {d.matchup_min:>5.1f} "
            f"{d.partial_poss:>6.1f} {fg_str:>6} {fg3_str:>6}"
        )


async def defender_assignment_profile(
    defender_id: int, name: str, season: str | None = None
) -> None:
    """Print who a defender guards the most."""
    season = season or get_season_from_date()

    async with NBAClient() as client:
        assignments = await get_defensive_assignments(
            client, defender_id=defender_id, season=season, top_n=5
        )

    if not assignments:
        print(f"No defensive assignment data for {name} ({season})")
        return

    print(f"\nDefensive Assignments — {name} ({season})")
    print(f"{'Guarding':<25} {'Min':>5} {'Poss':>6} {'FG%':>6} {'PPP':>6}")
    print("-" * 52)
    for a in assignments:
        fg_str = f"{a.matchup_fg_pct:.1%}" if a.matchup_fg_pct is not None else " N/A"
        ppp = matchup_ppp(a.player_pts, a.partial_poss)
        ppp_str = f"{ppp:.2f}" if ppp is not None else " N/A"
        print(
            f"  {a.off_player_name:<23} {a.matchup_min:>5.1f} "
            f"{a.partial_poss:>6.1f} {fg_str:>6} {ppp_str:>6}"
        )


async def team_vs_team(off_team: str, def_team: str, season: str | None = None) -> None:
    """Print matchup summary between two teams, ranked by PPP."""
    season = season or get_season_from_date()
    off_id = get_team_id(off_team)
    def_id = get_team_id(def_team)
    if off_id is None or def_id is None:
        print(f"Team not found: {off_team!r} or {def_team!r}")
        return

    async with NBAClient() as client:
        summary = await get_team_matchup_summary(
            client, off_team_id=off_id, def_team_id=def_id, season=season
        )

    ranked = rank_matchups(summary, min_poss=5.0, by="ppp", ascending=False)
    if not ranked:
        print(f"No matchup data: {off_team} vs {def_team} ({season})")
        return

    print(f"\n{off_team} vs {def_team} — Matchups by PPP ({season})")
    print(f"{'Offense':<20} {'vs Defender':<20} {'Poss':>6} {'FG%':>6} {'PPP':>6}")
    print("-" * 62)
    for m in ranked[:10]:
        fg_str = f"{m.matchup_fg_pct:.1%}" if m.matchup_fg_pct is not None else " N/A"
        ppp = matchup_ppp(m.player_pts, m.partial_poss)
        ppp_str = f"{ppp:.2f}" if ppp is not None else " N/A"
        print(
            f"  {m.off_player_name:<18} {m.def_player_name:<20} "
            f"{m.partial_poss:>6.1f} {fg_str:>6} {ppp_str:>6}"
        )


async def game_matchup_breakdown(game_id: str) -> None:
    """Print matchup data from a specific game."""
    async with NBAClient() as client:
        response = await get_game_matchups(client, game_id=game_id)

    data = response.box_score_matchups
    print(f"\nGame Matchups — {game_id}")

    for label, team in [("Home", data.home_team), ("Away", data.away_team)]:
        tricode = team.team_tricode or "???"
        print(f"\n  {label} ({tricode}):")
        if not team.players:
            print("    No matchup data available")
            continue

        for player in sorted(
            team.players,
            key=lambda p: max(
                (m.statistics.matchup_minutes_sort for m in p.matchups),
                default=0.0,
            ),
            reverse=True,
        )[:5]:
            if not player.matchups:
                continue
            top = max(
                player.matchups,
                key=lambda m: m.statistics.matchup_minutes_sort,
            )
            stats = top.statistics
            print(
                f"    {player.name_i:<15} guarded {top.name_i:<15} "
                f"— {stats.matchup_field_goals_made}/{stats.matchup_field_goals_attempted} "
                f"({stats.matchup_field_goals_percentage:.0%}), "
                f"{stats.partial_possessions:.1f} poss"
            )


async def head_to_head(
    player_id: int,
    vs_player_id: int,
    player_name: str,
    vs_name: str,
    season: str | None = None,
) -> None:
    """Print head-to-head stats with on/off court splits."""
    season = season or get_season_from_date()

    async with NBAClient() as client:
        response = await get_player_matchup_stats(
            client, player_id=player_id, vs_player_id=vs_player_id, season=season
        )

    print(f"\nHead-to-Head — {player_name} vs {vs_name} ({season})")

    if response.overall:
        print("\n  Overall:")
        for row in response.overall:
            if row.player_name and row.pts is not None:
                print(
                    f"    {row.player_name:<20} "
                    f"{row.pts:.1f} pts  {row.fg_pct:.1%} FG  "
                    f"{row.reb:.1f} reb  {row.ast:.1f} ast"
                )

    if response.on_off_court:
        print("\n  On/Off Court Splits:")
        for row in response.on_off_court:
            if row.court_status and row.pts is not None:
                status = "On " if row.court_status == "On" else "Off"
                print(
                    f"    {row.player_name or '?':<20} ({status} court): "
                    f"{row.pts:.1f} pts  {row.fg_pct:.1%} FG"
                )


async def player_opponent_splits(
    player_id: int,
    name: str,
    *,
    top_n: int = 8,
    season: str | None = None,
) -> None:
    """Print a player's scoring split against each opponent faced.

    Uses get_player_vs_opponents — the by_opponent set holds one row per team
    the player actually played, so a contender they haven't met yet is absent.
    """
    season = season or get_season_from_date()

    async with NBAClient() as client:
        response = await get_player_vs_opponents(
            client, player_id=player_id, season=season
        )

    opponents = sorted(response.by_opponent, key=lambda s: s.pts, reverse=True)
    if not opponents:
        print(f"No opponent split data for {name} ({season})")
        return

    overall_pts = response.overall.pts if response.overall else 0.0
    print(f"\nOpponent Splits — {name} ({season}), season avg {overall_pts:.1f} pts")
    print(f"{'Opponent':<24} {'GP':>3} {'PTS':>6} {'FG%':>6} {'+/-':>6}")
    print("-" * 50)
    for s in opponents[:top_n]:
        fg_str = f"{s.fg_pct:.1%}" if s.fg_pct is not None else " N/A"
        print(
            f"  {s.group_value!s:<22} {s.gp:>3} {s.pts:>6.1f} "
            f"{fg_str:>6} {s.plus_minus:>+6.1f}"
        )


async def team_matchup_history(
    team: str,
    opponent: str,
    *,
    season: str | None = None,
) -> None:
    """Print how a team has fared against one specific opponent this season.

    Demonstrates split_vs_opponent: resolve the opponent's row by team ID
    instead of scanning by name.
    """
    season = season or get_season_from_date()
    team_id = get_team_id(team)
    opp_id = get_team_id(opponent)
    if team_id is None or opp_id is None:
        print(f"Team not found: {team!r} or {opponent!r}")
        return

    async with NBAClient() as client:
        response = await get_team_vs_opponents(client, team_id=team_id, season=season)

    row = split_vs_opponent(response.by_opponent, opp_id)
    if row is None:
        print(f"{team} have not played {opponent} yet ({season})")
        return

    fg_str = f"{row.fg_pct:.1%}" if row.fg_pct is not None else "N/A"
    print(f"\n{team} vs {opponent} ({season})")
    print(
        f"  {row.gp} games: {row.w}-{row.losses}, "
        f"{row.pts:.1f} pts on {fg_str} FG, {row.plus_minus:+.1f} net"
    )


async def main() -> None:
    season = "2025-26"

    # 1. Who guards Jayson Tatum?
    await primary_defenders_for_player(
        player_id=1628369, name="Jayson Tatum", season=season
    )

    # 2. Who does Dyson Daniels guard?
    await defender_assignment_profile(
        defender_id=1630700, name="Dyson Daniels", season=season
    )

    # 3. Celtics vs Heat roster matchups
    await team_vs_team("Celtics", "Heat", season)

    # 4. Per-game matchup breakdown
    await game_matchup_breakdown("0022500571")

    # 5. Head-to-head deep dive
    await head_to_head(
        player_id=1628369,
        vs_player_id=1628389,
        player_name="Jayson Tatum",
        vs_name="Bam Adebayo",
        season=season,
    )

    # 6. How does a player score against each opponent?
    await player_opponent_splits(player_id=1628369, name="Jayson Tatum", season=season)

    # 7. A team's record against one specific opponent.
    await team_matchup_history("Celtics", "Heat", season=season)


if __name__ == "__main__":
    asyncio.run(main())
