"""Example: Advanced player analytics from fastbreak.players."""

import asyncio
from datetime import datetime

from fastbreak.clients import NBAClient
from fastbreak.players import (
    get_career_game_logs,
    get_on_off_splits,
    get_player_playtypes,
)

HALIBURTON_ID = 1630169
PACERS_TEAM_ID = 1610612754


async def main() -> None:
    async with NBAClient() as client:
        # ── 1. Career game log ───────────────────────────────────────
        print("=" * 60)
        print("Tyrese Haliburton — career game log")
        print("=" * 60)
        entries = await get_career_game_logs(client, player_id=HALIBURTON_ID)
        print(f"  {len(entries)} career regular-season games\n")
        print("  Most recent 5:")
        recent = sorted(
            entries,
            key=lambda e: datetime.strptime(e.game_date, "%b %d, %Y"),  # noqa: DTZ007
            reverse=True,
        )[:5]
        for entry in recent:
            print(
                f"    {entry.game_date}  {entry.matchup}"
                f"  {entry.pts} pts / {entry.reb} reb / {entry.ast} ast"
                f"  {entry.wl or '?'}"
            )
        print()

        # ── 2. On/off splits ─────────────────────────────────────────
        print("=" * 60)
        print("Tyrese Haliburton — on/off splits (current season)")
        print("=" * 60)
        splits = await get_on_off_splits(
            client,
            player_id=HALIBURTON_ID,
            team_id=PACERS_TEAM_ID,
        )
        on_rows = splits["on"]
        off_rows = splits["off"]

        if on_rows:
            on = on_rows[0]
            print(f"  ON  court:  {on.pts:.1f} pts/g  +/- {on.plus_minus:+.1f}")
        else:
            print("  ON  court:  no data")

        if off_rows:
            off = off_rows[0]
            print(f"  OFF court:  {off.pts:.1f} pts/g  +/- {off.plus_minus:+.1f}")
        else:
            print("  OFF court:  no data")
        print()

        # ── 3. Play-type breakdown ───────────────────────────────────
        print("=" * 60)
        print("Tyrese Haliburton — offensive play types (by possessions)")
        print("=" * 60)
        playtypes = await get_player_playtypes(
            client,
            player_id=HALIBURTON_ID,
            type_grouping="offensive",
        )
        if not playtypes:
            print("  No play-type data available.")
        else:
            sorted_plays = sorted(playtypes, key=lambda p: p.poss, reverse=True)
            print(f"  {'Play Type':<20}  {'Poss':>6}  {'PPP':>5}  {'eFG%':>6}")
            print(f"  {'-' * 20}  {'-' * 6}  {'-' * 5}  {'-' * 6}")
            for p in sorted_plays[:8]:
                print(
                    f"  {p.play_type:<20}  {p.poss:6.0f}  {p.ppp:5.2f}"
                    f"  {p.efg_pct:6.3f}"
                )
        print()


if __name__ == "__main__":
    asyncio.run(main())
