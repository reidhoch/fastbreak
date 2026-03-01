"""Example: Computing derived metrics with fastbreak.metrics.

Part 1 — pure computation: basic efficiency metrics (no network needed).
Part 2 — pure computation: rate stats & playmaking ratios.
Part 3 — pure computation: on-floor impact metrics with team context.
Part 4 — pure computation: full PER calculation (pace-adjusted + normalized).
Part 5 — live API: game score leaderboard for yesterday's games.
Part 6 — live API: usage & on-floor impact from real box score data.
Part 7 — pure computation: team offensive / defensive / net ratings.
Part 8 — pure computation: rolling averages with DNP and warm-up handling.
"""

import asyncio
from datetime import UTC, datetime, timedelta

from fastbreak.clients import NBAClient
from fastbreak.games import get_box_scores, get_games_on_date
from fastbreak.metrics import (
    LeagueAverages,
    ast_pct,
    ast_to_tov,
    blk_pct,
    dreb_pct,
    drtg,
    effective_fg_pct,
    free_throw_rate,
    game_score,
    is_double_double,
    is_triple_double,
    net_rtg,
    oreb_pct,
    ortg,
    pace_adjusted_per,
    per,
    per_36,
    relative_efg,
    relative_ts,
    rolling_avg,
    stl_pct,
    three_point_rate,
    true_shooting,
    usage_pct,
)

# ---------------------------------------------------------------------------
# Approximate 2024-25 NBA league averages.
# Swap in real values from LeagueDashTeamStats / LeagueDashPlayerStats for
# production use.
# ---------------------------------------------------------------------------
NBA_2024_25 = LeagueAverages(
    lg_pts=115.0,
    lg_fga=90.0,
    lg_fta=22.0,
    lg_ftm=17.0,
    lg_oreb=10.0,
    lg_treb=43.0,
    lg_ast=28.0,
    lg_fgm=42.0,
    lg_fg3m=13.0,
    lg_tov=14.0,
    lg_pf=20.0,
)


# ---------------------------------------------------------------------------
# Part 1: basic efficiency metrics — no API call required
# ---------------------------------------------------------------------------


def demo_single_line() -> None:
    """Show several metrics computed from one box score line."""
    print("=" * 60)
    print("Metrics demo — illustrative triple-double line")
    print("=" * 60)

    # Stat line: 28 pts, 12 reb, 10 ast, 2 stl, 2 blk (on 11-18 FG, 2-5 3P, 4-5 FT)
    pts = 28
    fgm, fga = 11, 18
    fg3m, fg3a = 2, 5
    ftm, fta = 4, 5
    oreb, dreb = 3, 9
    ast, stl, blk = 10, 2, 2
    pf, tov = 2, 3

    gs = game_score(
        pts=pts,
        fgm=fgm,
        fga=fga,
        ftm=ftm,
        fta=fta,
        oreb=oreb,
        dreb=dreb,
        stl=stl,
        ast=ast,
        blk=blk,
        pf=pf,
        tov=tov,
    )
    ts = true_shooting(pts=pts, fga=fga, fta=fta)
    efg = effective_fg_pct(fgm=fgm, fg3m=fg3m, fga=fga)
    rel_ts = relative_ts(ts, NBA_2024_25)
    rel_efg = relative_efg(efg, NBA_2024_25)

    print(f"  Line:  {pts} pts  {oreb + dreb} reb  {ast} ast  {stl} stl  {blk} blk")
    print(f"  FG:    {fgm}/{fga}  3P: {fg3m}/{fg3a}  FT: {ftm}/{fta}")
    print()
    print(f"  Game Score:       {gs:+.1f}   (avg ≈ 10, elite ≈ 30+)")
    print(
        f"  True Shooting%:   {ts:.3f}   (league avg {NBA_2024_25.ts:.3f},"
        f" rel {rel_ts:+.3f})"
        if ts is not None and rel_ts is not None
        else "  True Shooting%:   n/a"
    )
    print(
        f"  Eff. FG%:         {efg:.3f}   (league avg {NBA_2024_25.efg:.3f},"
        f" rel {rel_efg:+.3f})"
        if efg is not None and rel_efg is not None
        else "  Eff. FG%:         n/a"
    )
    print(
        f"  Double-double:    {is_double_double(pts=pts, reb=oreb + dreb, ast=ast, stl=stl, blk=blk)}"
    )
    print(
        f"  Triple-double:    {is_triple_double(pts=pts, reb=oreb + dreb, ast=ast, stl=stl, blk=blk)}"
    )
    print()


# ---------------------------------------------------------------------------
# Part 2: rate stats & playmaking ratios — no API call required
# ---------------------------------------------------------------------------


def demo_rate_stats() -> None:
    """Compare rate stats across three contrasting player archetypes."""
    print("=" * 60)
    print("Rate stats — three player archetypes")
    print("=" * 60)

    players = [
        {
            "name": "Stretch 4 (35 min)",
            "pts": 18,
            "reb": 6,
            "ast": 3,
            "fgm": 6,
            "fga": 13,
            "fg3a": 8,
            "ftm": 3,
            "fta": 3,
            "tov": 1,
            "mp": 35,
        },
        {
            "name": "Paint scorer (28 min)",
            "pts": 22,
            "reb": 9,
            "ast": 2,
            "fgm": 9,
            "fga": 15,
            "fg3a": 0,
            "ftm": 4,
            "fta": 7,
            "tov": 2,
            "mp": 28,
        },
        {
            "name": "Point guard (34 min)",
            "pts": 16,
            "reb": 3,
            "ast": 10,
            "fgm": 6,
            "fga": 14,
            "fg3a": 6,
            "ftm": 2,
            "fta": 3,
            "tov": 4,
            "mp": 34,
        },
    ]

    def _fmt(v: float | None) -> str:
        return f"{v:.3f}" if v is not None else "  n/a"

    header = f"  {'Player':<22} {'pts/36':>7} {'reb/36':>7} {'ast/36':>7} {'FTr':>6} {'3PAr':>6} {'A/TO':>6}"
    print(header)
    print("  " + "-" * (len(header) - 2))

    for p in players:
        p36_pts = per_36(p["pts"], p["mp"])
        p36_reb = per_36(p["reb"], p["mp"])
        p36_ast = per_36(p["ast"], p["mp"])
        ftr = free_throw_rate(p["fta"], p["fga"])
        tpar = three_point_rate(p["fg3a"], p["fga"])
        ato = ast_to_tov(p["ast"], p["tov"])
        print(
            f"  {p['name']:<22}"
            f" {_fmt(p36_pts):>7}"
            f" {_fmt(p36_reb):>7}"
            f" {_fmt(p36_ast):>7}"
            f" {_fmt(ftr):>6}"
            f" {_fmt(tpar):>6}"
            f" {_fmt(ato):>6}"
        )

    print()
    print("  Notes:")
    print(
        "    per_36  — normalises to 36 min so bench and starter minutes are comparable"
    )
    print(
        "    FTr     — FTA/FGA; anything above 0.40 and the defense is fouling to stop him"
    )
    print(
        "    3PAr    — share of FGA that are threes; above 0.50 = lives behind the arc"
    )
    print(
        "    A/TO    — assists per turnover; good playmakers stay above 2.0, elite above 3.0"
    )
    print()


# ---------------------------------------------------------------------------
# Part 3: on-floor impact metrics with team context — no API call required
# ---------------------------------------------------------------------------


def demo_on_floor_metrics() -> None:
    """Show usage%, AST%, rebound%, steal%, and block% with fabricated team context."""
    print("=" * 60)
    print("On-floor impact — primary ball-handler vs rim-protector")
    print("=" * 60)

    # Shared team context for a single game (per-game counting stats).
    # Both players are on the same team; totals are for the full game.
    team_fga = 88
    team_fta = 20
    team_fgm = 42
    team_tov = 13
    team_oreb = 9
    team_dreb = 31
    team_mp = 240  # sum of all player-minutes for one team (5 * 48)

    # Opponent context (needed for dreb%, stl%, blk%)
    opp_oreb = 12
    opp_dreb = 28
    opp_fg2a = 52  # opponent 2-point attempts (opp_fga - opp_fg3a)
    opp_poss = 94  # estimated: opp_fga + 0.44*opp_fta + opp_tov - opp_oreb

    print("\n  === Primary ball-handler (36 min) ===")
    bh_mp = 36
    bh_fga, bh_fta, bh_tov = 16, 5, 4
    bh_fgm, bh_ast = 8, 11
    bh_dreb, bh_stl = 4, 2

    u = usage_pct(
        fga=bh_fga,
        fta=bh_fta,
        tov=bh_tov,
        mp=bh_mp,
        team_fga=team_fga,
        team_fta=team_fta,
        team_tov=team_tov,
        team_mp=team_mp,
    )
    a = ast_pct(
        ast=bh_ast,
        fgm=bh_fgm,
        mp=bh_mp,
        team_fgm=team_fgm,
        team_mp=team_mp,
    )
    d = dreb_pct(
        dreb=bh_dreb,
        mp=bh_mp,
        team_dreb=team_dreb,
        opp_oreb=opp_oreb,
        team_mp=team_mp,
    )
    s = stl_pct(stl=bh_stl, mp=bh_mp, team_mp=team_mp, opp_poss=opp_poss)

    print(f"    Usage%:  {u:.3f}  (0.25+ = primary option; 0.30+ = star territory)")
    print(f"    AST%:    {a:.3f}  (teammate baskets he assisted while on floor)")
    print(f"    DREB%:   {d:.3f}  (his cut of available defensive rebounds)")
    print(f"    STL%:    {s:.3f}  (opponent possessions he ended with a steal)")

    print("\n  === Rim-protecting center (30 min) ===")
    c_mp = 30
    c_fga, c_fta, c_tov = 11, 6, 2
    c_oreb, c_dreb, c_blk = 4, 8, 3

    u_c = usage_pct(
        fga=c_fga,
        fta=c_fta,
        tov=c_tov,
        mp=c_mp,
        team_fga=team_fga,
        team_fta=team_fta,
        team_tov=team_tov,
        team_mp=team_mp,
    )
    o_c = oreb_pct(
        oreb=c_oreb,
        mp=c_mp,
        team_oreb=team_oreb,
        opp_dreb=opp_dreb,
        team_mp=team_mp,
    )
    d_c = dreb_pct(
        dreb=c_dreb,
        mp=c_mp,
        team_dreb=team_dreb,
        opp_oreb=opp_oreb,
        team_mp=team_mp,
    )
    b_c = blk_pct(blk=c_blk, mp=c_mp, team_mp=team_mp, opp_fg2a=opp_fg2a)

    print(f"    Usage%:  {u_c:.3f}")
    print(f"    OREB%:   {o_c:.3f}  (his cut of available offensive rebounds)")
    print(f"    DREB%:   {d_c:.3f}")
    print(f"    BLK%:    {b_c:.3f}  (opponent 2-pt attempts he blocked)")
    print()


# ---------------------------------------------------------------------------
# Part 4: full PER calculation (aPER → normalised PER) — no API call required
# ---------------------------------------------------------------------------


def demo_per_calculation() -> None:
    """Demonstrate the two-step PER pipeline with a five-player lineup."""
    print("=" * 60)
    print("Full PER calculation — aPER → normalized PER")
    print("=" * 60)
    print("  Step 1: compute pace-adjusted PER (aPER) per player")
    print("  Step 2: weight-average across all player-minutes → lg_aPER")
    print("  Step 3: PER = aPER * (15 / lg_aPER)  →  15.0 is league-average")
    print()

    # Five illustrative players on the same team for a single game.
    # Tuple layout: name, fgm, fga, fg3m, ftm, fta, oreb, treb, ast, stl, blk, pf, tov, mp
    team_ast = 28
    team_fgm = 42
    team_pace = 98.5  # slightly below league-average pace

    roster: list[
        tuple[str, int, int, int, int, int, int, int, int, int, int, int, int, int]
    ] = [
        ("Star wing", 11, 20, 3, 7, 8, 1, 8, 5, 2, 1, 3, 3, 36),
        ("Point guard", 7, 15, 2, 4, 5, 0, 4, 9, 2, 0, 2, 4, 34),
        ("Big man", 8, 12, 0, 5, 8, 4, 10, 2, 1, 3, 2, 2, 30),
        ("3&D wing", 5, 10, 3, 2, 2, 1, 5, 2, 2, 1, 3, 1, 28),
        ("Backup guard", 3, 8, 1, 2, 2, 0, 2, 4, 1, 0, 1, 2, 18),
    ]

    apers: list[tuple[str, float, int]] = []
    for (
        name,
        fgm,
        fga,
        fg3m,
        ftm,
        fta,
        oreb,
        treb,
        ast,
        stl,
        blk,
        pf,
        tov,
        mp,
    ) in roster:
        aper = pace_adjusted_per(
            fgm=fgm,
            fga=fga,
            fg3m=fg3m,
            ftm=ftm,
            fta=fta,
            oreb=oreb,
            treb=treb,
            ast=ast,
            stl=stl,
            blk=blk,
            pf=pf,
            tov=tov,
            mp=mp,
            team_ast=team_ast,
            team_fgm=team_fgm,
            team_pace=team_pace,
            lg=NBA_2024_25,
        )
        if aper is not None:
            apers.append((name, aper, mp))
            print(f"    {name:<18}  aPER = {aper:.4f}  ({mp} min)")

    total_min = sum(mp for _, _, mp in apers)
    lg_aper = sum(aper * mp for _, aper, mp in apers) / total_min if total_min else 0.0

    print(f"\n  Weighted lg_aPER (by minutes): {lg_aper:.4f}")
    print(f"  Scale factor (15 / lg_aPER):   {15 / lg_aper:.3f}\n")

    print(f"  {'Player':<18}  {'aPER':>7}  {'PER':>7}  {'vs avg':>8}")
    print("  " + "-" * 45)
    for name, aper, _ in apers:
        player_per = per(aper=aper, lg_aper=lg_aper)
        if player_per is not None:
            diff = player_per - 15.0
            print(f"  {name:<18}  {aper:>7.4f}  {player_per:>7.2f}  {diff:>+8.2f}")
    print()


# ---------------------------------------------------------------------------
# Part 5: live API — game score leaderboard for a given date
# ---------------------------------------------------------------------------


def _parse_minutes(minutes_str: str) -> int:
    """Return integer minutes from a 'MM:SS' string, or 0 on empty/bad input."""
    if not minutes_str or ":" not in minutes_str:
        return 0
    return int(minutes_str.split(":", maxsplit=1)[0])


async def game_score_leaderboard(date_str: str) -> None:
    """Fetch all box scores for a date and rank players by Game Score."""
    print("=" * 60)
    print(f"Game Score leaderboard — {date_str}")
    print("=" * 60)

    async with NBAClient() as client:
        games = await get_games_on_date(client, date_str)
        if not games:
            print("  No games found.")
            return

        game_ids = [g.game_id for g in games if g.game_id]
        print(f"  {len(game_ids)} game(s). Fetching box scores...")
        box_scores = await get_box_scores(client, game_ids)

    rows = []
    for bxs in box_scores.values():
        for team in (bxs.homeTeam, bxs.awayTeam):
            for player in team.players:
                s = player.statistics
                mp = _parse_minutes(s.minutes)
                if mp < 10:  # noqa: PLR2004 — skip DNPs and garbage-time cameos
                    continue
                gs = game_score(
                    pts=s.points,
                    fgm=s.fieldGoalsMade,
                    fga=s.fieldGoalsAttempted,
                    ftm=s.freeThrowsMade,
                    fta=s.freeThrowsAttempted,
                    oreb=s.reboundsOffensive,
                    dreb=s.reboundsDefensive,
                    stl=s.steals,
                    ast=s.assists,
                    blk=s.blocks,
                    pf=s.foulsPersonal,
                    tov=s.turnovers,
                )
                ts = true_shooting(
                    pts=s.points, fga=s.fieldGoalsAttempted, fta=s.freeThrowsAttempted
                )
                rows.append(
                    (
                        f"{player.firstName} {player.familyName}",
                        team.teamTricode,
                        mp,
                        gs,
                        ts,
                    )
                )

    rows.sort(key=lambda r: r[3], reverse=True)
    print(f"\n  {'Player':<25} {'Team':<5} {'MIN':>4}  {'GmSc':>6}  {'TS%':>6}")
    print("  " + "-" * 50)
    for name, tricode, mp, gs, ts in rows[:15]:
        ts_str = f"{ts:.3f}" if ts is not None else "  n/a"
        print(f"  {name:<25} {tricode:<5} {mp:>4}  {gs:>6.1f}  {ts_str:>6}")
    print()


# ---------------------------------------------------------------------------
# Part 6: live API — usage & on-floor impact leaderboard
# ---------------------------------------------------------------------------


async def usage_leaderboard(date_str: str) -> None:
    """Fetch box scores and compute usage%, AST%, pts/36, and A/TO for each player."""
    print("=" * 60)
    print(f"Usage & impact leaderboard — {date_str}")
    print("=" * 60)

    async with NBAClient() as client:
        games = await get_games_on_date(client, date_str)
        if not games:
            print("  No games found.")
            return

        game_ids = [g.game_id for g in games if g.game_id]
        print(f"  {len(game_ids)} game(s). Fetching box scores...")
        box_scores = await get_box_scores(client, game_ids)

    rows = []
    for bxs in box_scores.values():
        for team in (bxs.homeTeam, bxs.awayTeam):
            ts = team.statistics
            # Sum all player-minutes rather than parsing team.statistics.minutes,
            # since the per-team total is the scale used by usage_pct / ast_pct.
            team_mp = sum(_parse_minutes(p.statistics.minutes) for p in team.players)

            for player in team.players:
                s = player.statistics
                mp = _parse_minutes(s.minutes)
                if mp < 10:  # noqa: PLR2004
                    continue

                u = usage_pct(
                    fga=s.fieldGoalsAttempted,
                    fta=s.freeThrowsAttempted,
                    tov=s.turnovers,
                    mp=mp,
                    team_fga=ts.fieldGoalsAttempted,
                    team_fta=ts.freeThrowsAttempted,
                    team_tov=ts.turnovers,
                    team_mp=team_mp,
                )
                a = ast_pct(
                    ast=s.assists,
                    fgm=s.fieldGoalsMade,
                    mp=mp,
                    team_fgm=ts.fieldGoalsMade,
                    team_mp=team_mp,
                )
                p36 = per_36(s.points, mp)
                ato = ast_to_tov(s.assists, s.turnovers)

                rows.append(
                    (
                        f"{player.firstName} {player.familyName}",
                        team.teamTricode,
                        mp,
                        u if u is not None else 0.0,
                        a if a is not None else 0.0,
                        p36 if p36 is not None else 0.0,
                        ato,
                    )
                )

    rows.sort(key=lambda r: r[3], reverse=True)
    print(
        f"\n  {'Player':<25} {'Tm':<4} {'MIN':>4}"
        f"  {'Usage%':>7}  {'AST%':>6}  {'Pts/36':>7}  {'A/TO':>5}"
    )
    print("  " + "-" * 60)
    for name, tricode, mp, u, a, p36, ato in rows[:15]:
        ato_str = f"{ato:.2f}" if ato is not None else " n/a"
        print(
            f"  {name:<25} {tricode:<4} {mp:>4}"
            f"  {u:>7.3f}  {a:>6.3f}  {p36:>7.1f}  {ato_str:>5}"
        )
    print()


# Part 7: team ratings — ortg, drtg, net_rtg — no API call required
# ─────────────────────────────────────────────────────────────────────


def demo_team_ratings() -> None:
    """Demonstrate ortg, drtg, and net_rtg with fabricated game stats."""
    print("=" * 60)
    print("Part 7 — Team Offensive / Defensive / Net Rating")
    print("=" * 60)

    # Fabricated game totals for two contrasting performances.
    # Each row: label, team pts/fga/oreb/tov/fta, opp pts/fga/oreb/tov/fta
    games: list[tuple[str, float, float, float, float, float, float, float, float, float, float, float]] = [
        # label,        pts, fga, oreb, tov, fta,  opp_pts, opp_fga, opp_oreb, opp_tov, opp_fta
        ("Blowout win", 130,  90,   12,  14,  22,     108,      85,        8,      17,      16),
        ("Close loss",  107,  88,    9,  16,  18,     111,      89,       11,      13,      22),
    ]

    for label, pts, fga, oreb, tov, fta, opp_pts, opp_fga, opp_oreb, opp_tov, opp_fta in games:
        o = ortg(pts=pts, fga=fga, oreb=oreb, tov=tov, fta=fta)
        d = drtg(opp_pts=opp_pts, opp_fga=opp_fga, opp_oreb=opp_oreb, opp_tov=opp_tov, opp_fta=opp_fta)
        n = net_rtg(ortg_val=o, drtg_val=d)
        print(f"\n  {label}:")
        print(f"    ORTG:    {o:.1f}" if o is not None else "    ORTG:    N/A")
        print(f"    DRTG:    {d:.1f}" if d is not None else "    DRTG:    N/A")
        print(f"    Net RTG: {n:+.1f}" if n is not None else "    Net RTG: N/A")
    print()


# ---------------------------------------------------------------------------
# Part 8: rolling average — no API call required
# ---------------------------------------------------------------------------


def demo_rolling_avg() -> None:
    """Show rolling_avg over a fabricated 10-game scoring sequence."""
    print("=" * 60)
    print("Part 8 — Rolling average over a scoring sequence")
    print("=" * 60)

    # Fabricated 10-game scoring streak with one missed game (None)
    pts: list[float | None] = [
        18.0,
        22.0,
        15.0,
        None,
        30.0,
        28.0,
        12.0,
        25.0,
        19.0,
        24.0,
    ]

    for window in (3, 5):
        avgs = rolling_avg(pts, window=window)
        print(f"\n  {window}-game rolling average:")
        print(f"  {'Game':>5}  {'Pts':>5}  {'Avg':>7}")
        print("  " + "-" * 22)
        for i, (raw, avg) in enumerate(zip(pts, avgs, strict=True), start=1):
            raw_str = f"{raw:.1f}" if raw is not None else " DNP"
            if avg is not None:
                avg_str = f"{avg:.2f}"
            elif i < window:
                avg_str = "  warm"  # still in warm-up period
            else:
                avg_str = "   n/a"  # None propagated from a DNP within the window
            print(f"  {i:>5}  {raw_str:>5}  {avg_str:>7}")

    print()
    print("  Notes:")
    print("    'warm' = fewer than window games played yet (warm-up period).")
    print("    'n/a'  = a DNP/missing value within the window propagates None.")
    print()


async def main() -> None:
    demo_single_line()
    demo_rate_stats()
    demo_on_floor_metrics()
    demo_per_calculation()
    demo_team_ratings()
    demo_rolling_avg()

    yesterday = (
        datetime.now(tz=UTC).astimezone().date() - timedelta(days=1)
    ).isoformat()
    await game_score_leaderboard(yesterday)
    await usage_leaderboard(yesterday)


if __name__ == "__main__":
    asyncio.run(main())
