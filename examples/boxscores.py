"""Example: Fetching box scores with fastbreak.games.

Covers:
  - get_yesterdays_games    — convenience shortcut for yesterday's scoreboard
  - get_box_scores          — standard player/team box score
  - get_box_scores_advanced — pace, ORtg, DRtg, usage per player
  - get_box_scores_hustle   — contested shots, screen assists
  - get_box_scores_scoring  — shot-zone scoring distribution (% of pts)
"""

import asyncio

from fastbreak.clients import NBAClient
from fastbreak.games import (
    get_box_scores,
    get_box_scores_advanced,
    get_box_scores_hustle,
    get_box_scores_scoring,
    get_yesterdays_games,
)


async def main() -> None:
    async with NBAClient() as client:
        # ── 1. Yesterday's games via convenience helper ───────────────────
        print("=" * 60)
        print("Yesterday's games  (get_yesterdays_games)")
        print("=" * 60)
        games = await get_yesterdays_games(client)
        if not games:
            print("  No games yesterday.")
            return

        print(f"  {len(games)} game(s)\n")
        game_ids = [g.game_id for g in games if g.game_id]

        # ── 2. Standard box scores ────────────────────────────────────────
        print()
        print("=" * 60)
        print("Standard box scores  (get_box_scores)")
        print("=" * 60)
        box_scores = await get_box_scores(client, game_ids)
        for game_id, bxs in box_scores.items():
            away = bxs.awayTeam
            home = bxs.homeTeam
            print(
                f"  {away.teamTricode} @ {home.teamTricode}:"
                f"  {away.statistics.points} - {home.statistics.points}"
                f"  [{game_id}]"
            )

        # ── 3. Advanced box score (first game only) ───────────────────────
        first_id = game_ids[:1]
        print()
        print("=" * 60)
        print(f"Advanced box score  (get_box_scores_advanced)  [{first_id[0]}]")
        print("=" * 60)
        adv = await get_box_scores_advanced(client, first_id)
        data = adv[first_id[0]]
        all_players = data.homeTeam.players + data.awayTeam.players
        qualified = [
            p
            for p in all_players
            if p.statistics.minutes and p.statistics.minutes > "00:"
        ]
        qualified.sort(key=lambda p: p.statistics.offensiveRating, reverse=True)
        print(f"  {'Player':<25} {'ORTG':>5}  {'DRTG':>5}  {'USG%':>6}")
        print("  " + "-" * 46)
        for p in qualified[:8]:
            s = p.statistics
            print(
                f"  {p.firstName} {p.familyName:<18}"
                f" {s.offensiveRating:>5.1f}"
                f"  {s.defensiveRating:>5.1f}"
                f"  {s.usagePercentage:>6.3f}"
            )

        # ── 4. Hustle box score (first game only) ─────────────────────────
        print()
        print("=" * 60)
        print(f"Hustle box score  (get_box_scores_hustle)  [{first_id[0]}]")
        print("=" * 60)
        hustle = await get_box_scores_hustle(client, first_id)
        hdata = hustle[first_id[0]]
        hustle_players = hdata.home_team.players + hdata.away_team.players
        hustle_players.sort(
            key=lambda p: (
                p.statistics.contested_shots_2pt + p.statistics.contested_shots_3pt
            ),
            reverse=True,
        )
        print(f"  {'Player':<25} {'Con2':>4}  {'Con3':>4}  {'ScrAst':>6}")
        print("  " + "-" * 44)
        for p in hustle_players[:8]:
            s = p.statistics
            name = f"{p.first_name} {p.family_name}"
            print(
                f"  {name:<25}"
                f" {s.contested_shots_2pt:>4}"
                f"  {s.contested_shots_3pt:>4}"
                f"  {s.screen_assists:>6}"
            )

        # ── 5. Scoring distribution (first game only) ─────────────────────
        print()
        print("=" * 60)
        print(f"Scoring distribution  (get_box_scores_scoring)  [{first_id[0]}]")
        print("=" * 60)
        scoring = await get_box_scores_scoring(client, first_id)
        sdata = scoring[first_id[0]]
        score_players = sdata.homeTeam.players + sdata.awayTeam.players
        score_players.sort(
            key=lambda p: p.statistics.percentagePointsPaint,
            reverse=True,
        )
        print(f"  {'Player':<25} {'%Paint':>6}  {'%Fast':>5}  {'%3pt':>5}")
        print("  " + "-" * 46)
        for p in score_players[:8]:
            s = p.statistics
            print(
                f"  {p.firstName} {p.familyName:<18}"
                f" {s.percentagePointsPaint:>6.3f}"
                f"  {s.percentagePointsFastBreak:>5.3f}"
                f"  {s.percentagePoints3pt:>5.3f}"
            )


if __name__ == "__main__":
    asyncio.run(main())
