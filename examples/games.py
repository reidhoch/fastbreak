"""Game flow and scoreline analysis examples.

Demonstrates fetching play-by-play data and building a score-line timeline
with game_flow(): final score, halftime score, largest lead, lead changes,
and close-finish detection.

Run:
    uv run python examples/games.py
"""

import asyncio
from datetime import UTC, datetime, timedelta

from fastbreak.clients import NBAClient
from fastbreak.games import game_flow, get_games_on_date, get_play_by_play

_CLOSE_GAME_MARGIN = 5  # points — within this margin counts as "close"
_CLOSE_GAME_WINDOW = 120  # seconds — final 2 minutes of the game


async def game_flow_summary(
    client: NBAClient,
    game_id: str,
    away: str,
    home: str,
) -> None:
    """Fetch PBP for one game and print a score-line summary.

    Shows how to use game_flow() to derive:
    - Final and halftime scores from flow[-1] and period filtering
    - Largest lead in each direction from margin min/max
    - Lead changes by detecting sign flips in consecutive margins
    - Close-finish detection using elapsed_seconds
    """
    actions = await get_play_by_play(client, game_id)
    flow = game_flow(actions)

    if not flow:
        print(f"  {away} @ {home}: no scoring data.")
        return

    last = flow[-1]
    winner = home if last.score_home > last.score_away else away
    print(f"\n{away} @ {home}")
    print(
        f"  Final:  {away} {last.score_away}  {home} {last.score_home}  ({winner} wins)"
    )

    # Halftime: last scoring event at end of Q2
    half = [p for p in flow if p.period <= 2]  # noqa: PLR2004
    if half:
        h = half[-1]
        print(f"  Half:   {away} {h.score_away}  {home} {h.score_home}")

    # Largest lead in each direction
    max_home = max(p.margin for p in flow)
    max_away = abs(min(p.margin for p in flow))
    leads = []
    if max_home > 0:
        leads.append(f"{home} +{max_home}")
    if max_away > 0:
        leads.append(f"{away} +{max_away}")
    if leads:
        print(f"  Big leads: {',  '.join(leads)}")

    # Lead changes: margin sign flips between consecutive scoring events
    lead_changes = sum(
        1
        for i in range(1, len(flow))
        if (flow[i - 1].margin > 0 and flow[i].margin < 0)
        or (flow[i - 1].margin < 0 and flow[i].margin > 0)
    )
    ties = sum(1 for p in flow if p.margin == 0)
    print(f"  Lead changes: {lead_changes}   Ties: {ties}")

    # Close finish: scoring events in the final 2 min of the game within 5 pts.
    # Uses elapsed_seconds so this works for regulation and OT games.
    close_late = [
        p
        for p in flow
        if p.elapsed_seconds >= last.elapsed_seconds - _CLOSE_GAME_WINDOW
        and abs(p.margin) <= _CLOSE_GAME_MARGIN
    ]
    if close_late:
        final_margin = abs(last.score_home - last.score_away)
        print(
            f"  Close finish: {len(close_late)} event(s) in final 2 min within {_CLOSE_GAME_MARGIN} pts"
            f"  (final margin: {final_margin})"
        )

    # Final 5 scoring plays
    print("  Last 5 plays:")
    for point in flow[-5:]:
        period_label = (
            f"Q{point.period}" if point.period <= 4 else f"OT{point.period - 4}"
        )
        margin_str = f"+{point.margin}" if point.margin > 0 else str(point.margin)
        print(
            f"    {period_label} {point.clock}  "
            f"{away} {point.score_away} - {home} {point.score_home}"
            f"  ({home} {margin_str})"
        )


async def main() -> None:
    yesterday = (
        datetime.now(tz=UTC).astimezone().date() - timedelta(days=1)
    ).isoformat()

    async with NBAClient() as client:
        games = await get_games_on_date(client, yesterday)

        if not games:
            print(f"No games on {yesterday}.")
            return

        print(f"Game Flow Analysis — {yesterday}  ({len(games)} game(s))")

        for game in games:
            if game.game_id is None:
                continue
            away = game.away_team.team_tricode if game.away_team else "AWY"
            home = game.home_team.team_tricode if game.home_team else "HME"
            await game_flow_summary(client, game.game_id, away, home)


if __name__ == "__main__":
    asyncio.run(main())
