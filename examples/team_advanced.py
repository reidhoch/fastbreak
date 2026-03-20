"""Example: Advanced team analytics from fastbreak.teams."""

import asyncio

from fastbreak.clients import NBAClient
from fastbreak.teams import (
    get_league_averages,
    get_lineup_net_ratings,
    get_team_on_off_summary,
    get_team_playtypes,
    on_off_net_rating_delta,
    search_teams,
)

IND = search_teams("IND")[0]


async def main() -> None:
    async with NBAClient() as client:
        # ── 1. League averages ───────────────────────────────────────
        print("=" * 60)
        print("League averages (current season, per-game)")
        print("=" * 60)
        lg = await get_league_averages(client)
        print(f"  PPG:   {lg.lg_pts:.1f}")
        print(f"  FGA:   {lg.lg_fga:.1f}")
        print(f"  3PM:   {lg.lg_fg3m:.1f}")
        print(f"  FTA:   {lg.lg_fta:.1f}")
        print(f"  OReb:  {lg.lg_oreb:.1f}")
        print(f"  AST:   {lg.lg_ast:.1f}")
        print(f"  TOV:   {lg.lg_tov:.1f}")
        print(f"  Pace:  {lg.lg_pace:.1f}  (est. possessions/game)")
        print()

        # ── 2. Team play-type breakdown ──────────────────────────────
        print("=" * 60)
        print(f"{IND.full_name} — offensive play types (by possessions)")
        print("=" * 60)
        playtypes = await get_team_playtypes(
            client,
            team_id=int(IND.id),
            type_grouping="offensive",
        )
        if not playtypes:
            print("  No play-type data available.")
            print("  (Synergy play-type data isn't available through the public API)")
        else:
            sorted_plays = sorted(playtypes, key=lambda p: p.poss, reverse=True)
            print(f"  {'Play Type':<20}  {'Poss':>6}  {'PPP':>5}  {'eFG%':>6}")
            print(f"  {'-' * 20}  {'-' * 6}  {'-' * 5}  {'-' * 6}")
            for p in sorted_plays[:8]:
                print(
                    f"  {p.play_type:<20}  {p.poss:6.0f}  {p.ppp:5.2f}"
                    f"  {p.efg_pct:6.3f}",
                )
        print()

        # ── 3. Lineup net ratings ────────────────────────────────────
        print("=" * 60)
        print(f"{IND.full_name} — top 10 lineups by net rating (avg ≥10 min/g)")
        print("=" * 60)
        lineups = await get_lineup_net_ratings(
            client,
            team_id=int(IND.id),
            min_minutes=10.0,
        )
        if not lineups:
            print("  No lineups meet the minutes threshold.")
        else:
            print(f"  {'Lineup':<55}  {'GP':>3}  {'Net RTG':>7}")
            print(f"  {'-' * 55}  {'-' * 3}  {'-' * 7}")
            for lineup, net in lineups[:10]:
                print(f"  {lineup.group_name:<55}  {lineup.gp:3d}  {net:+7.1f}")
        print()

        # ── 4. Player on/off court impact ──────────────────────────────
        print("=" * 60)
        print(f"{IND.full_name} — player on/off court impact (net rating)")
        print("=" * 60)
        on_off = await get_team_on_off_summary(client, team_id=int(IND.id))

        # Build (player_name, on_row, off_row) triples
        on_rows = {r.vs_player_name: r for r in on_off.players_on_court}
        off_rows = {r.vs_player_name: r for r in on_off.players_off_court}
        players = sorted(on_rows.keys())

        print(f"  {'Player':<25} {'On NR':>7} {'Off NR':>7} {'Delta':>7}")
        print(f"  {'-' * 25}  {'-' * 7} {'-' * 7} {'-' * 7}")
        for name in players:
            on_row = on_rows.get(name)
            off_row = off_rows.get(name)
            if on_row and off_row:
                delta = on_off_net_rating_delta(on_row.net_rating, off_row.net_rating)
                print(
                    f"  {name:<25} {on_row.net_rating:>+7.1f} "
                    f"{off_row.net_rating:>+7.1f} {delta:>+7.1f}",
                )
        print()


if __name__ == "__main__":
    asyncio.run(main())
