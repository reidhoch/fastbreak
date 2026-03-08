"""Example: Schedule utilities from fastbreak.schedule."""

import asyncio
from datetime import date

from fastbreak.clients import NBAClient
from fastbreak.schedule import (
    days_rest_before_game,
    get_team_schedule,
    is_back_to_back,
    travel_distances,
)
from fastbreak.teams import get_team_id

_ind_id = get_team_id("IND")
if _ind_id is None:
    msg = "IND team not found"
    raise ValueError(msg)
IND_TEAM_ID: int = int(_ind_id)


def _tricode(team: object) -> str:
    """Return team tricode or '???' for missing team data."""
    return getattr(team, "team_tricode", "???")


async def main() -> None:
    async with NBAClient() as client:
        # ── 1. Full team schedule ────────────────────────────────────
        print("=" * 60)
        print("Indiana Pacers — 2025-26 schedule (first 10 games)")
        print("=" * 60)
        games = await get_team_schedule(client, team_id=IND_TEAM_ID, season="2025-26")
        print(f"  {len(games)} total games scheduled\n")
        for game in games[:10]:
            if not game.game_date_est:
                continue
            game_date = game.game_date_est[:10]
            away = _tricode(game.away_team)
            home = _tricode(game.home_team)
            status = game.game_status_text or ""
            print(f"  {game_date}  {away} @ {home}  {status}")
        print()

        # ── 2. Back-to-back detection ────────────────────────────────
        print("=" * 60)
        print("Pacers — back-to-backs in 2025-26")
        print("=" * 60)
        # Keep (game, date) pairs together to avoid parallel-list index drift
        valid_games = [
            (g, date.fromisoformat(g.game_date_est[:10]))
            for g in games
            if g.game_date_est
        ]
        game_dates = [d for _, d in valid_games]

        back_to_backs = [
            (i, game_dates[i])
            for i in range(len(game_dates))
            if is_back_to_back(game_dates, i)
        ]
        print(f"  {len(back_to_backs)} back-to-back games")
        for i, d in back_to_backs[:5]:
            rest = days_rest_before_game(game_dates, i)
            game, _ = valid_games[i]
            away = _tricode(game.away_team)
            home = _tricode(game.home_team)
            print(f"  Game {i + 1:3d}  {d}  {away} @ {home}  ({rest} days rest)")
        print()

        # ── 3. days_rest_before_game — inspect rest around an example stretch ──
        print("=" * 60)
        print("Rest days before each of the first 5 games")
        print("=" * 60)
        for i in range(min(5, len(game_dates))):
            rest = days_rest_before_game(game_dates, i)
            game, d = valid_games[i]
            away = _tricode(game.away_team)
            home = _tricode(game.home_team)
            rest_str = str(rest) if rest is not None else "first game"
            print(f"  Game {i + 1}  {d}  {away} @ {home}  rest={rest_str}")
        print()

        # ── 4. Travel distance ───────────────────────────────────────
        print("=" * 60)
        print("Pacers — travel legs for first 10 games")
        print("=" * 60)
        all_legs = travel_distances(games)
        for i, (game, d) in enumerate(valid_games[:10]):
            if not game.game_id:
                continue
            leg = all_legs.get(game.game_id)
            away = _tricode(game.away_team)
            home = _tricode(game.home_team)
            matchup = f"{away} @ {home}"
            if leg is None:
                travel_str = "n/a (first game or neutral site)"
            else:
                direction = (
                    "→E" if leg.tz_shift > 0 else "←W" if leg.tz_shift < 0 else "  "
                )
                travel_str = f"{leg.miles:>6.0f} mi  {direction}  tz {leg.tz_shift:+d}h"
            print(f"  Game {i + 1:3d}  {d}  {matchup:<14}  {travel_str}")
        print()

        # ── 5. Longest road trip leg in the season ───────────────────
        print("=" * 60)
        print("Pacers — longest single travel leg (full season)")
        print("=" * 60)
        away_legs = [
            (game, leg)
            for game in games
            if game.game_id
            and game.away_team is not None
            and game.away_team.team_id == IND_TEAM_ID  # Pacers traveled TO this game
            and (leg := all_legs.get(game.game_id)) is not None
        ]
        if away_legs:
            hardest = max(away_legs, key=lambda t: t[1].miles)
            g, leg = hardest
            away = _tricode(g.away_team)
            home = _tricode(g.home_team)
            print(f"  {(g.game_date_est or '')[:10]}  {away} @ {home}")
            print(f"  {leg.miles:.0f} miles, tz shift {leg.tz_shift:+d}h")
        print()


if __name__ == "__main__":
    asyncio.run(main())
