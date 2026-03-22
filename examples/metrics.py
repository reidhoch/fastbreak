"""Example: Computing derived metrics with fastbreak.metrics.

Part 1  — pure computation: basic efficiency metrics (no network needed).
Part 2  — pure computation: rate stats & playmaking ratios.
Part 3  — pure computation: on-floor impact metrics with team context.
Part 4  — pure computation: full PER calculation (pace-adjusted + normalized).
Part 5  — live API: game score leaderboard for yesterday's games.
Part 6  — live API: usage & on-floor impact from real box score data.
Part 7  — pure computation: team offensive / defensive / net ratings.
Part 8  — pure computation: rolling averages with DNP and warm-up handling.
Part 9  — pure computation: Win Shares (OWS + DWS → WS → WS/48) for three archetypes.
Part 10 — live API: per-game Win Shares leaderboard for yesterday's games.
Part 11 — pure computation: distribution stats (floor / median / ceiling / prop hit rate).
Part 12 — live API: player prop profile from a season game log.
Part 13 — pure computation: advanced distribution analytics (consistency, streaks, percentile rank).
Part 14 — pure computation: rolling consistency, expected stat, and recent-form hit rate.
Part 15 — pure computation: Box Plus/Minus 2.0 (BPM / OBPM / DBPM) + VORP — LeBron James 2009-10.
Part 16 — pure computation: EWMA scoring trend — span comparison and DNP gap handling.
Part 17 — pure computation: Kubatko et al. (2007) additions — possessions, plays,
          efficiency, floor/play %, and Bell Curve win expectation.
"""

import asyncio
from datetime import UTC, datetime, timedelta

from fastbreak.clients import NBAClient
from fastbreak.games import get_box_scores, get_games_on_date
from fastbreak.metrics import (
    LeagueAverages,
    ast_pct,
    ast_to_tov,
    bell_curve_win_pct,
    blk_pct,
    bpm,
    defensive_win_shares,
    dreb_pct,
    drtg,
    effective_fg_pct,
    ewma,
    expected_stat,
    floor_pct,
    free_throw_rate,
    game_score,
    hit_rate_last_n,
    is_double_double,
    is_triple_double,
    nba_efficiency,
    net_rtg,
    offensive_win_shares,
    oreb_pct,
    ortg,
    pace_adjusted_per,
    per,
    per_36,
    percentile_rank,
    play_pct,
    plays,
    possessions,
    possessions_general,
    prop_hit_rate,
    pythagorean_win_pct,
    relative_efg,
    relative_ts,
    rolling_avg,
    rolling_consistency,
    stat_ceiling,
    stat_consistency,
    stat_floor,
    stat_median,
    stl_pct,
    streak_count,
    three_point_rate,
    true_shooting,
    usage_pct,
    vorp,
    win_shares,
    win_shares_per_48,
)
from fastbreak.players import get_player_game_log
from fastbreak.teams import get_league_averages

# ---------------------------------------------------------------------------
# Approximate 2025-26 NBA league averages.
# Swap in real values from LeagueDashTeamStats / LeagueDashPlayerStats for
# production use.
# ---------------------------------------------------------------------------
NBA_2025_26 = LeagueAverages(
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
    rel_ts = relative_ts(ts, NBA_2025_26)
    rel_efg = relative_efg(efg, NBA_2025_26)

    print(f"  Line:  {pts} pts  {oreb + dreb} reb  {ast} ast  {stl} stl  {blk} blk")
    print(f"  FG:    {fgm}/{fga}  3P: {fg3m}/{fg3a}  FT: {ftm}/{fta}")
    print()
    print(f"  Game Score:       {gs:+.1f}   (avg ≈ 10, elite ≈ 30+)")
    print(
        f"  True Shooting%:   {ts:.3f}   (league avg {NBA_2025_26.ts:.3f},"
        f" rel {rel_ts:+.3f})"
        if ts is not None and rel_ts is not None
        else "  True Shooting%:   n/a"
    )
    print(
        f"  Eff. FG%:         {efg:.3f}   (league avg {NBA_2025_26.efg:.3f},"
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
            lg=NBA_2025_26,
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


def demo_bpm_vorp() -> None:
    """BPM 2.0 + VORP -- LeBron James, Cleveland Cavaliers 2009-10.

    Shows the full pipeline:
      1. Per-100-possession stats (from Basketball Reference).
      2. Compute raw BPM (Total / OBPM / DBPM) -- no team adjustment applied.
      3. Apply the approximate team adjustment to match published numbers.
      4. Compute VORP.

    2009-10 Cleveland pace: ~93.8 possessions per game.
    Per-100 stats below are sourced from Basketball Reference's
    2009-10 per-100-possession page for LeBron James.

    Basketball Reference published values (team-adjusted):
      BPM +10.8, OBPM +6.5, DBPM +4.3, VORP 9.3.
    This was the highest Total BPM of LeBron's career to that point.
    """
    print("=" * 62)
    print("BPM 2.0 -- LeBron James, Cleveland Cavaliers 2009-10")
    print("=" * 62)

    # ── Per-100 team possession stats (BR 2009-10 per-100 page) ───────────
    #   Stat         per-game   per-100
    #   PTS          29.7       34.3
    #   FGA          20.9       26.5   (FG% 50.3%)
    #   FG3M          1.4        1.6   (3P% 33.3%, 3PA 4.7)
    #   FTA           8.8       10.2
    #   AST           8.6        9.8
    #   TOV           3.4        3.9
    #   ORB           1.2        1.4
    #   DRB           6.3        7.3
    #   STL           1.6        1.9
    #   BLK           1.0        1.1
    #   PF            2.2        2.5
    result = bpm(
        pts=34.3,
        fg3m=1.6,
        ast=9.8,
        tov=3.9,
        orb=1.4,
        drb=7.3,
        stl=1.9,
        blk=1.1,
        pf=2.5,
        fga=26.5,
        fta=10.2,
        # Cleveland 2009-10 team per-game averages (used as proxy for
        # on-court team share; BR uses true on-court totals which differ
        # slightly, accounting for the residual gap in the adj values below):
        #   PPG 102.1, RPG 43.5, APG 21.2, SPG 7.9, BPG 5.2, PF 20.4
        pct_team_trb=0.168,  # 7.3  / 43.5
        pct_team_stl=0.203,  # 1.6  / 7.9
        pct_team_pf=0.108,  # 2.2  / 20.4
        pct_team_ast=0.406,  # 8.6  / 21.2
        pct_team_blk=0.192,  # 1.0  / 5.2
        pct_team_pts=0.291,  # 29.7 / 102.1
        listed_position=3.0,  # SF
        mp=2966.0,  # 38.5 mpg x 77 games (approx.)
    )
    assert result is not None

    print("\n  Raw BPM (before team adjustment)")
    print(f"  {'Total BPM:':<14} {result.total:+.2f}")
    print(f"  {'OBPM:':<14} {result.offensive:+.2f}")
    print(f"  {'DBPM:':<14} {result.defensive:+.2f}")
    print()
    print("  Note: raw values are elevated because the team adjustment has")
    print("  not yet been applied.  DBPM is unaffected by the team constant")
    print("  (it equals Total BPM minus OBPM, so the constant cancels).")

    # ── Team adjustment ────────────────────────────────────────────────────
    # The team adjustment is a constant added to every player's Total and
    # OBPM so the minutes-weighted team average equals the Cavaliers'
    # actual adjusted efficiency differential (~+7).  The raw team-average
    # BPM across the roster came out roughly +14, so the adjustment is
    # approximately 7 - 14 = -7.  Using -7.0 here reproduces the published
    # BR values within ~0.5 points:
    #   adj total = raw - 7.0 ≈ 10.8  (BR: +10.8)
    #   adj OBPM  = raw - 7.0 ≈  6.5  (BR: +6.5)
    #   DBPM is unchanged           ≈  4.3  (BR: +4.3)
    team_adj = -7.0
    adj_total = result.total + team_adj
    adj_obpm = result.offensive + team_adj
    adj_dbpm = result.defensive  # unchanged

    print(f"\n  Team adjustment: {team_adj:+.1f}  (Cavaliers adj. eff. diff. ~+7)")
    print(f"  {'Adj Total:':<14} {adj_total:+.2f}   (BR published: +10.8)")
    print(f"  {'Adj OBPM:':<14} {adj_obpm:+.2f}   (BR published: +6.5)")
    print(f"  {'Adj DBPM:':<14} {adj_dbpm:+.2f}   (BR published: +4.3)")

    # ── VORP ───────────────────────────────────────────────────────────────
    # poss_pct = player minutes / (team games x 48 min/game)
    # Captures the fraction of team possessions the player participated in.
    poss_pct = 2966.0 / (82 * 48)  # ≈ 0.754
    player_vorp = vorp(bpm_total=adj_total, poss_pct=poss_pct, games=82)
    wins_above_replacement = player_vorp * 2.7  # BR conversion factor

    print("\n  VORP calculation")
    print(f"  Possession share:  {poss_pct:.1%}  (2966 min / 82x48)")
    print(f"  VORP:              {player_vorp:.2f}   (BR published: 9.3)")
    print(f"  ~{wins_above_replacement:.1f} wins above replacement")
    print()
    print("  Context: +10.8 BPM is one of the highest single-season marks")
    print("  in the Basketball Reference era.  LeBron averaged 29.7 / 7.3")
    print("  / 8.6 on a 61-win Cleveland team in his first MVP campaign.")
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

        # Exclude All-Star games (game_id prefix "003") — non-standard tricodes
        game_ids = [g.game_id for g in games if g.game_id and g.game_id[:3] == "002"]
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

        # Exclude All-Star games (game_id prefix "003") — non-standard tricodes
        game_ids = [g.game_id for g in games if g.game_id and g.game_id[:3] == "002"]
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
    games: list[
        tuple[
            str,
            float,
            float,
            float,
            float,
            float,
            float,
            float,
            float,
            float,
            float,
            float,
        ]
    ] = [
        # label,        pts, fga, oreb, tov, fta,  opp_pts, opp_fga, opp_oreb, opp_tov, opp_fta
        ("Blowout win", 130, 90, 12, 14, 22, 108, 85, 8, 17, 16),
        ("Close loss", 107, 88, 9, 16, 18, 111, 89, 11, 13, 22),
    ]

    for (
        label,
        pts,
        fga,
        oreb,
        tov,
        fta,
        opp_pts,
        opp_fga,
        opp_oreb,
        opp_tov,
        opp_fta,
    ) in games:
        o = ortg(pts=pts, fga=fga, oreb=oreb, tov=tov, fta=fta)
        d = drtg(
            opp_pts=opp_pts,
            opp_fga=opp_fga,
            opp_oreb=opp_oreb,
            opp_tov=opp_tov,
            opp_fta=opp_fta,
        )
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


# ---------------------------------------------------------------------------
# Part 9: Win Shares — OWS + DWS → WS → WS/48 — no API call required
# ---------------------------------------------------------------------------


def demo_win_shares() -> None:
    """Compare OWS, DWS, WS, and WS/48 for three season-level archetypes."""
    print("=" * 60)
    print("Part 9 — Win Shares (OWS + DWS → WS → WS/48)")
    print("=" * 60)
    print(
        "  Win Shares estimate how many team wins each player contributed.\n"
        "  WS/48 normalises to a per-48-minute pace for fair comparisons.\n"
    )

    # Shared team/opponent context — generic 82-game NBA team.
    # team_mp = 5 players x 48 min x 82 games.
    _team = {
        "team_mp": 19_680,
        "team_blk": 410,
        "team_stl": 656,
        "team_dreb": 2_624,
        "team_pf": 1_640,
    }
    _opp = {
        "opp_fga": 7_380,
        "opp_fgm": 3_444,
        "opp_fta": 1_804,
        "opp_ftm": 1_394,
        "opp_tov": 1_148,
        "opp_oreb": 820,
        "opp_pts": 9_430,
    }

    # Three contrasting archetypes — season totals from per-game rates x 82 games.
    archetypes = [
        {
            "name": "Two-way wing  (35 min)",
            "pts": 2_050,  # 25.0 ppg
            "fga": 984,  # 12.0 fga/g
            "fta": 328,  # 4.0  fta/g
            "tov": 164,  # 2.0  tov/g
            "stl": 164,  # 2.0  stl/g
            "blk": 82,  # 1.0  blk/g
            "dreb": 410,  # 5.0  dreb/g
            "mp": 2_870,  # 35.0 min/g
            "pf": 164,  # 2.0  pf/g
        },
        {
            "name": "Volume scorer (36 min)",
            "pts": 2_296,  # 28.0 ppg
            "fga": 1_476,  # 18.0 fga/g
            "fta": 656,  # 8.0  fta/g
            "tov": 287,  # 3.5  tov/g
            "stl": 82,  # 1.0  stl/g
            "blk": 41,  # 0.5  blk/g
            "dreb": 328,  # 4.0  dreb/g
            "mp": 2_952,  # 36.0 min/g
            "pf": 205,  # 2.5  pf/g
        },
        {
            "name": "Def. anchor  (30 min)",
            "pts": 1_148,  # 14.0 ppg
            "fga": 738,  # 9.0  fga/g
            "fta": 410,  # 5.0  fta/g
            "tov": 82,  # 1.0  tov/g
            "stl": 66,  # 0.8  stl/g
            "blk": 246,  # 3.0  blk/g
            "dreb": 820,  # 10.0 dreb/g
            "mp": 2_460,  # 30.0 min/g
            "pf": 164,  # 2.0  pf/g
        },
    ]

    def _ws48_tier(v: float | None) -> str:
        if v is None:
            return "—"
        if v >= 0.250:  # noqa: PLR2004
            return "MVP-caliber"
        if v >= 0.200:  # noqa: PLR2004
            return "All-Star"
        if v >= 0.150:  # noqa: PLR2004
            return "solid starter"
        if v >= 0.100:  # noqa: PLR2004
            return "lg average"
        return "rotation" if v >= 0.050 else "below avg"  # noqa: PLR2004

    def _f2(v: float | None) -> str:
        return f"{v:.2f}" if v is not None else " n/a"

    def _f3(v: float | None) -> str:
        return f"{v:.3f}" if v is not None else "   n/a"

    print(f"  {'Archetype':<26} {'OWS':>5}  {'DWS':>5}  {'WS':>5}  {'WS/48':>6}  Tier")
    print("  " + "-" * 66)

    for a in archetypes:
        ows = offensive_win_shares(
            pts=a["pts"],
            fga=a["fga"],
            fta=a["fta"],
            tov=a["tov"],
            lg=NBA_2025_26,
        )
        dws = defensive_win_shares(
            stl=a["stl"],
            blk=a["blk"],
            dreb=a["dreb"],
            mp=a["mp"],
            pf=a["pf"],
            **_team,
            **_opp,
            lg=NBA_2025_26,
        )
        ws = win_shares(ows, dws)
        ws48 = win_shares_per_48(ws, a["mp"])
        print(
            f"  {a['name']:<26} {_f2(ows):>5}  {_f2(dws):>5}  {_f2(ws):>5}"
            f"  {_f3(ws48):>6}  {_ws48_tier(ws48)}"
        )

    print()
    print("  WS/48 benchmarks:  0.100+ lg average    · 0.150+ solid starter")
    print("                     0.200+ All-Star      · 0.250+ MVP-caliber")
    print()


# ---------------------------------------------------------------------------
# Part 10: live API — per-game Win Shares leaderboard for a given date
# ---------------------------------------------------------------------------


async def win_shares_leaderboard(date_str: str) -> None:
    """Fetch box scores and rank players by single-game Win Shares."""
    print("=" * 60)
    print(f"Win Shares leaderboard — {date_str}")
    print("=" * 60)

    async with NBAClient() as client:
        games = await get_games_on_date(client, date_str)
        if not games:
            print("  No games found.")
            return

        # Exclude All-Star games (game_id prefix "003") — non-standard tricodes
        game_ids = [g.game_id for g in games if g.game_id and g.game_id[:3] == "002"]
        print(f"  {len(game_ids)} game(s). Fetching box scores and league averages...")
        box_scores_data, lg = await asyncio.gather(
            get_box_scores(client, game_ids),
            get_league_averages(client),
        )

    def _f3(v: float | None) -> str:
        return f"{v:.3f}" if v is not None else "  n/a"

    rows = []
    for bxs in box_scores_data.values():
        for team, opp_team in (
            (bxs.homeTeam, bxs.awayTeam),
            (bxs.awayTeam, bxs.homeTeam),
        ):
            ts = team.statistics
            opp_ts = opp_team.statistics
            team_mp = sum(_parse_minutes(p.statistics.minutes) for p in team.players)

            for player in team.players:
                s = player.statistics
                mp = _parse_minutes(s.minutes)
                if mp < 10:  # noqa: PLR2004
                    continue

                ows = offensive_win_shares(
                    pts=s.points,
                    fga=s.fieldGoalsAttempted,
                    fta=s.freeThrowsAttempted,
                    tov=s.turnovers,
                    lg=lg,
                )
                dws = defensive_win_shares(
                    stl=s.steals,
                    blk=s.blocks,
                    dreb=s.reboundsDefensive,
                    mp=mp,
                    pf=s.foulsPersonal,
                    team_mp=team_mp,
                    team_blk=ts.blocks,
                    team_stl=ts.steals,
                    team_dreb=ts.reboundsDefensive,
                    team_pf=ts.foulsPersonal,
                    opp_fga=opp_ts.fieldGoalsAttempted,
                    opp_fgm=opp_ts.fieldGoalsMade,
                    opp_fta=opp_ts.freeThrowsAttempted,
                    opp_ftm=opp_ts.freeThrowsMade,
                    opp_tov=opp_ts.turnovers,
                    opp_oreb=opp_ts.reboundsOffensive,
                    opp_pts=opp_ts.points,
                    lg=lg,
                )
                ws = win_shares(ows, dws)
                ws48 = win_shares_per_48(ws, mp)
                rows.append(
                    (
                        f"{player.firstName} {player.familyName}",
                        team.teamTricode,
                        mp,
                        ows,
                        dws,
                        ws,
                        ws48,
                    )
                )

    rows.sort(key=lambda r: r[6] if r[6] is not None else float("-inf"), reverse=True)
    print(
        f"\n  {'Player':<25} {'Tm':<4} {'MIN':>3}"
        f"  {'OWS':>6}  {'DWS':>6}  {'WS':>6}  {'WS/48':>6}"
    )
    print("  " + "-" * 63)
    for name, tricode, mp, ows, dws, ws, ws48 in rows[:15]:
        print(
            f"  {name:<25} {tricode:<4} {mp:>3}"
            f"  {_f3(ows):>6}  {_f3(dws):>6}  {_f3(ws):>6}  {_f3(ws48):>6}"
        )
    print()
    print(
        "  Note: single-game WS is a fraction of a full season's contribution.\n"
        "  A player with 0.050+ WS in one game made a genuinely significant impact."
    )
    print()


# ---------------------------------------------------------------------------
# Part 11: distribution stats — no API call required
# ---------------------------------------------------------------------------


def demo_distribution_stats() -> None:
    """Compare floor/median/ceiling and prop hit rates for three scoring profiles."""
    print("=" * 60)
    print("Part 11 — Distribution stats: floor / median / ceiling / prop hit rate")
    print("=" * 60)
    print(
        "  Distribution stats describe the shape of a player's output\n"
        "  over a sample of games — going beyond the average to capture\n"
        "  upside, downside, and reliability. DNP games (None) are skipped.\n"
    )

    # Fabricated 15-game scoring logs for three contrasting archetypes.
    # None = DNP (did not play) — excluded from the distribution, not counted as 0.
    profiles: list[dict] = [
        {
            "name": "Streaky star  (35 min)",
            "pts": [
                38.0,
                14.0,
                41.0,
                22.0,
                None,
                35.0,
                12.0,
                29.0,
                44.0,
                18.0,
                9.0,
                31.0,
                26.0,
                40.0,
                20.0,
            ],
            "lines": [20.5, 25.5, 30.5],
        },
        {
            "name": "Consistent scorer (32 min)",
            "pts": [
                24.0,
                22.0,
                26.0,
                20.0,
                27.0,
                23.0,
                25.0,
                None,
                21.0,
                28.0,
                22.0,
                24.0,
                19.0,
                26.0,
                23.0,
            ],
            "lines": [20.5, 22.5, 24.5],
        },
        {
            "name": "Bench contributor (22 min)",
            "pts": [
                12.0,
                8.0,
                15.0,
                None,
                11.0,
                6.0,
                14.0,
                9.0,
                13.0,
                None,
                7.0,
                16.0,
                10.0,
                8.0,
                12.0,
            ],
            "lines": [8.5, 10.5, 12.5],
        },
    ]

    def _f1(v: float | None) -> str:
        return f"{v:.1f}" if v is not None else " n/a"

    for profile in profiles:
        name: str = profile["name"]
        pts: list[float | None] = profile["pts"]
        lines: list[float] = profile["lines"]

        valid = [p for p in pts if p is not None]
        avg = sum(valid) / len(valid) if valid else 0.0
        dnps = sum(1 for p in pts if p is None)

        floor_v = stat_floor(pts)  # 10th percentile: downside floor
        median_v = stat_median(pts)  # 50th percentile: central tendency
        ceil_v = stat_ceiling(pts)  # 90th percentile: upside ceiling

        print(f"  {name}")
        print(
            f"    {len(valid)} games played  ({dnps} DNP)  "
            f"avg={avg:.1f}  range={min(valid):.0f}-{max(valid):.0f}"
        )
        print(f"    Floor   (10th pct):  {_f1(floor_v):>5}")
        print(f"    Median  (50th pct):  {_f1(median_v):>5}")
        print(f"    Ceiling (90th pct):  {_f1(ceil_v):>5}")
        print()

        print("    Prop hit rates (>= line):")
        for line in lines:
            rate = prop_hit_rate(pts, line)
            rate_str = f"{rate:.1%}" if rate is not None else " n/a"
            bar_width = int((rate or 0.0) * 20)
            bar = "█" * bar_width + "░" * (20 - bar_width)
            print(f"      >= {line:>4.1f}:  {rate_str:>6}  {bar}")
        print()

    print(
        "  Key insight: a consistent scorer and a streaky star can have the\n"
        "  same average but very different floor/ceiling profiles. The\n"
        "  consistent scorer is a safer prop-bet play; the streaky star\n"
        "  is better for tournament formats that reward big games.\n"
    )


# ---------------------------------------------------------------------------
# Part 12: live API — player prop profile from a season game log
# ---------------------------------------------------------------------------


async def player_prop_profile(player_id: int, player_name: str) -> None:
    """Fetch a player's game log and compute their scoring distribution profile."""
    print("=" * 60)
    print(f"Player prop profile — {player_name}")
    print("=" * 60)

    async with NBAClient() as client:
        log = await get_player_game_log(client, player_id=player_id)

    # Filter to regular-season games (game_id prefix "002") — All-Star games
    # (prefix "003") produce non-standard stats and inflate or deflate distributions.
    regular = [g for g in log if g.game_id[:3] == "002"]

    if not regular:
        print("  No regular-season games found.")
        return

    pts: list[float | None] = [
        float(g.pts) if g.pts is not None else None for g in regular
    ]
    reb: list[float | None] = [
        float(g.reb) if g.reb is not None else None for g in regular
    ]
    ast: list[float | None] = [
        float(g.ast) if g.ast is not None else None for g in regular
    ]

    def _dist(
        values: list[float | None],
    ) -> tuple[float | None, float | None, float | None]:
        return stat_floor(values), stat_median(values), stat_ceiling(values)

    def _f1(v: float | None) -> str:
        return f"{v:.1f}" if v is not None else " n/a"

    games_played = sum(1 for v in pts if v is not None)
    print(f"  Season sample: {games_played} games played of {len(regular)} scheduled\n")

    print(f"  {'Stat':<6}  {'Floor(10)':>9}  {'Median':>8}  {'Ceiling(90)':>11}")
    print("  " + "-" * 40)
    for label, values in [("PTS", pts), ("REB", reb), ("AST", ast)]:
        f, m, c = _dist(values)
        print(f"  {label:<6}  {_f1(f):>9}  {_f1(m):>8}  {_f1(c):>11}")

    # Prop hit rates — common market lines for each stat category
    print()
    print("  Prop hit rates against typical market lines:")
    prop_lines: list[tuple[str, list[float | None], list[float]]] = [
        ("PTS", pts, [19.5, 24.5, 29.5]),
        ("REB", reb, [5.5, 8.5, 10.5]),
        ("AST", ast, [4.5, 7.5, 10.5]),
    ]
    for label, values, lines in prop_lines:
        rates = [prop_hit_rate(values, line) for line in lines]
        rate_strs = "  ".join(
            f"{line:.1f}→{r:.0%}" if r is not None else f"{line:.1f}→ n/a"
            for line, r in zip(lines, rates, strict=True)
        )
        print(f"    {label:<5} {rate_strs}")

    print()
    print(
        "  Note: distributions are built from this season's game log only.\n"
        "  Use a multi-season window for more stable floor/ceiling estimates."
    )
    print()


# ---------------------------------------------------------------------------
# Part 13: pure computation — consistency, streaks, and percentile rank
# ---------------------------------------------------------------------------


def demo_advanced_distribution() -> None:
    """Showcase stat_consistency, streak_count, and percentile_rank."""
    print("=" * 60)
    print("Part 13 — Advanced distribution: consistency / streaks / rank")
    print("=" * 60)

    # Same three archetypes as Part 11 — reused so the outputs are comparable.
    profiles: list[dict] = [
        {
            "name": "Streaky star  (35 min)",
            "pts": [
                38.0,
                14.0,
                41.0,
                22.0,
                None,
                35.0,
                12.0,
                29.0,
                44.0,
                18.0,
                9.0,
                31.0,
                26.0,
                40.0,
                20.0,
            ],
        },
        {
            "name": "Consistent scorer (32 min)",
            "pts": [
                24.0,
                22.0,
                26.0,
                20.0,
                27.0,
                23.0,
                25.0,
                None,
                21.0,
                28.0,
                22.0,
                24.0,
                19.0,
                26.0,
                23.0,
            ],
        },
        {
            "name": "Bench contributor (22 min)",
            "pts": [
                12.0,
                8.0,
                15.0,
                None,
                11.0,
                6.0,
                14.0,
                9.0,
                13.0,
                None,
                7.0,
                16.0,
                10.0,
                8.0,
                12.0,
            ],
        },
    ]

    # ------------------------------------------------------------------ #
    # Section A: stat_consistency — population std dev of each archetype  #
    # ------------------------------------------------------------------ #
    print(
        "\n  stat_consistency = population std dev of per-game output.\n"
        "  Lower is more reliable; higher means boom-or-bust variance.\n"
    )
    print(f"  {'Player':<28}  {'Avg':>6}  {'Consistency':>11}  {'CV (%)':>7}")
    print("  " + "-" * 58)
    for p in profiles:
        pts: list[float | None] = p["pts"]
        valid = [v for v in pts if v is not None]
        avg = sum(valid) / len(valid)
        cons = stat_consistency(pts)
        cv = (cons / avg * 100.0) if cons is not None and avg > 0 else None
        cv_str = f"{cv:.1f}%" if cv is not None else "n/a"
        cons_str = f"{cons:.2f}" if cons is not None else "n/a"
        print(f"  {p['name']:<28}  {avg:>6.1f}  {cons_str:>11}  {cv_str:>7}")

    # ------------------------------------------------------------------ #
    # Section B: streak_count — current active scoring streak             #
    # ------------------------------------------------------------------ #
    streak_lines = [15.0, 20.0, 25.0]
    print("\n  streak_count = consecutive recent games >= line (DNPs skipped).\n")
    print(f"  {'Player':<28}  " + "  ".join(f">=  {line:.0f}" for line in streak_lines))
    print("  " + "-" * 58)
    for p in profiles:
        pts_vals: list[float | None] = p["pts"]
        streaks = [str(streak_count(pts_vals, line)) for line in streak_lines]
        print(f"  {p['name']:<28}  " + "         ".join(f"{s:>4}" for s in streaks))

    # ------------------------------------------------------------------ #
    # Section C: percentile_rank — where does 25 pts rank in each log?   #
    # ------------------------------------------------------------------ #
    query_value = 25.0
    print(
        f"\n  percentile_rank(value={query_value:.0f}, reference=season_log)\n"
        f"  Answers: 'a {query_value:.0f}-pt game would rank in the Nth percentile\n"
        "  of this player's historical output.'\n"
    )
    print(f"  {'Player':<28}  {'Rank':>8}  Interpretation")
    print("  " + "-" * 58)
    for p in profiles:
        pts_vals = p["pts"]
        rank = percentile_rank(query_value, pts_vals)
        if rank is None:
            interp = "no data"
        elif rank >= 90.0:  # noqa: PLR2004
            interp = "exceptional game (top 10%)"
        elif rank >= 75.0:  # noqa: PLR2004
            interp = "strong game (top quartile)"
        elif rank >= 50.0:  # noqa: PLR2004
            interp = "above-average game"
        elif rank >= 25.0:  # noqa: PLR2004
            interp = "below-average game"
        else:
            interp = "poor game (bottom quartile)"
        rank_str = f"{rank:.1f}th" if rank is not None else "n/a"
        print(f"  {p['name']:<28}  {rank_str:>8}  {interp}")

    print()
    print(
        "  Combined insight: use stat_consistency to filter for reliable\n"
        "  targets, streak_count to gauge current form, and percentile_rank\n"
        "  to contextualise any single game within the season sample.\n"
    )


# ---------------------------------------------------------------------------
# Part 14: pure computation — rolling consistency, expected stat, recent form
# ---------------------------------------------------------------------------


def demo_recent_form() -> None:
    """Showcase rolling_consistency, expected_stat, and hit_rate_last_n."""
    print("=" * 60)
    print(
        "Part 14 — Recent form: rolling consistency / PERT projection / last-N hit rate"
    )
    print("=" * 60)

    # A 20-game scoring log — starts cold, heats up, then levels off.
    # None = DNP (did not play).
    pts: list[float | None] = [
        12.0,
        8.0,
        15.0,
        None,
        10.0,  # cold stretch
        18.0,
        22.0,
        None,
        25.0,
        20.0,  # improving
        28.0,
        31.0,
        25.0,
        None,
        27.0,  # hot stretch
        24.0,
        26.0,
        22.0,
        28.0,
        25.0,  # recent games
    ]
    games_played = sum(1 for v in pts if v is not None)
    print(
        f"\n  20-game log: {games_played} games played  "
        f"(avg={sum(v for v in pts if v is not None) / games_played:.1f})\n"
    )

    # ------------------------------------------------------------------ #
    # Section A: rolling_consistency — is the player more or less erratic? #
    # ------------------------------------------------------------------ #
    window = 5
    rc = rolling_consistency(pts, window)

    print(f"  Rolling consistency (window={window}) — lower = more predictable:")
    print(f"  {'Game':<6}  {'PTS':>4}  {'RC(5)':>8}")
    print("  " + "-" * 22)
    for i, (p, r) in enumerate(zip(pts, rc, strict=True), start=1):
        pts_str = f"{p:.0f}" if p is not None else "DNP"
        rc_str = f"{r:.2f}" if r is not None else " n/a"
        print(f"  {i:<6}  {pts_str:>4}  {rc_str:>8}")

    print()
    print(
        "  Key: games 1-5 have higher RC (cold + erratic), games 14-20\n"
        "  show lower RC as output steadies in the 24-28 range.\n"
    )

    # ------------------------------------------------------------------ #
    # Section B: expected_stat — PERT projection for the full season      #
    # ------------------------------------------------------------------ #
    exp = expected_stat(pts)
    floor_v = stat_floor(pts)
    median_v = stat_median(pts)
    ceil_v = stat_ceiling(pts)

    print("  expected_stat (PERT projection):")
    print(f"    Floor  (10th pct):  {floor_v:.1f}")
    print(f"    Median (50th pct):  {median_v:.1f}")
    print(f"    Ceiling(90th pct):  {ceil_v:.1f}")
    print(f"    PERT projection:    {exp:.1f}  ← (floor + 4*median + ceiling) / 6")
    print(
        "\n  The PERT value sits between the median and average, pulled\n"
        "  toward the median to down-weight the cold early games.\n"
    )

    # ------------------------------------------------------------------ #
    # Section C: hit_rate_last_n — recent form vs full-season rate         #
    # ------------------------------------------------------------------ #
    line = 22.5
    print(f"  hit_rate_last_n (line >= {line}) — recent form versus season rate:")
    print(f"  {'Window':<12}  {'Hit rate':>8}  {'Bar':>22}")
    print("  " + "-" * 46)
    for n, label in [
        (3, "Last 3"),
        (5, "Last 5"),
        (10, "Last 10"),
        (games_played, "Full season"),
    ]:
        rate = hit_rate_last_n(pts, line, n)
        rate_str = f"{rate:.0%}" if rate is not None else "n/a"
        bar_w = int((rate or 0.0) * 20)
        bar = "█" * bar_w + "░" * (20 - bar_w)
        print(f"  {label:<12}  {rate_str:>8}  {bar}")

    print()
    print(
        "  Compare last-3 (hot recent stretch) vs full-season to spot\n"
        "  players entering form. A rising last-N rate vs the season\n"
        "  rate is a strong signal for upcoming games.\n"
    )


# ---------------------------------------------------------------------------
# Part 16: EWMA — exponentially weighted moving average — no API call required
# ---------------------------------------------------------------------------


def demo_ewma() -> None:
    """Compare EWMA at three spans over a 20-game log, and show DNP-gap behaviour."""
    print("=" * 60)
    print("Part 16 — EWMA: exponentially weighted scoring trend")
    print("=" * 60)
    print(
        "  alpha = 2 / (span + 1).  Larger span = smoother / slower reaction.\n"
        "  None (DNP) produces None output but does not reset the running state.\n"
    )

    # 20-game scoring log: cold start → improvement → hot stretch → steady.
    # Three None entries scattered to represent DNPs.
    pts: list[float | None] = [
        12.0,
        8.0,
        15.0,
        None,
        10.0,  # cold (None = DNP)
        18.0,
        22.0,
        None,
        25.0,
        20.0,  # improving
        28.0,
        31.0,
        25.0,
        None,
        27.0,  # hot stretch
        24.0,
        26.0,
        22.0,
        28.0,
        25.0,  # recent games
    ]

    # ------------------------------------------------------------------ #
    # Section A: side-by-side comparison of three spans                   #
    # ------------------------------------------------------------------ #
    spans = [3, 7, 10]
    smoothed = {s: ewma(pts, span=s) for s in spans}

    header = f"  {'Gm':>3}  {'PTS':>4}" + "".join(
        f"  {'EWMA(' + str(s) + ')':>9}" for s in spans
    )
    print(header)
    print("  " + "-" * (len(header) - 2))
    for i, raw in enumerate(pts):
        raw_str = f"{raw:.0f}" if raw is not None else "DNP"
        row = f"  {i + 1:>3}  {raw_str:>4}"
        for s in spans:
            v = smoothed[s][i]
            row += f"  {v:>9.2f}" if v is not None else f"  {'—':>9}"
        print(row)

    print()
    for s in spans:
        last = smoothed[s][-1]  # pts ends with 25.0 (non-None), so always set
        alpha = 2.0 / (s + 1)
        last_str = f"{last:.2f}" if last is not None else "n/a"
        print(f"  span={s:>2}  alpha={alpha:.3f}  final EWMA = {last_str}")
    print(
        "\n  Larger span trails further behind the recent hot stretch —\n"
        "  useful for trend detection (span=3) vs noise suppression (span=10).\n"
    )

    # ------------------------------------------------------------------ #
    # Section B: DNP gap — running state persists across missed games     #
    # ------------------------------------------------------------------ #
    print("  DNP gap demo (span=5): state persists, then resumes")
    gap_pts: list[float | None] = [20.0, 22.0, 24.0, None, None, None, 30.0]
    gap_ewma = ewma(gap_pts, span=5)
    print(f"  {'Gm':>3}  {'PTS':>4}  {'EWMA(5)':>9}")
    print("  " + "-" * 20)
    for i, (raw, avg) in enumerate(zip(gap_pts, gap_ewma, strict=True), start=1):
        raw_str = f"{raw:.0f}" if raw is not None else "DNP"
        avg_str = f"{avg:.2f}" if avg is not None else "     —"
        print(f"  {i:>3}  {raw_str:>4}  {avg_str:>9}")
    print(
        "\n  After three DNPs the EWMA resumes from its last value (~22)\n"
        "  and reacts to the 30-point game — no cold-start penalty.\n"
    )


def demo_kubatko() -> None:
    """Part 17 — Kubatko et al. (2007) additions."""
    print("=" * 60)
    print("Part 17: Kubatko et al. (2007) — possession framework")
    print("=" * 60)

    # --- Possessions and plays ---
    fga, oreb, tov, fta = 88, 10, 13, 22
    poss = possessions(fga=fga, oreb=oreb, tov=tov, fta=fta)
    play_count = plays(fga=fga, fta=fta, tov=tov)
    print(f"\nTeam box: FGA={fga}, OREB={oreb}, TOV={tov}, FTA={fta}")
    print(f"  Possessions (standard):  {poss:.1f}")
    print(f"  Plays (minor poss):      {play_count:.1f}")
    print(f"  Difference (OREB plays): {play_count - poss:.1f}")

    # --- General formula with different alpha values ---
    fgm, ftm, dreb_opp = 40, 17, 30
    poss_lost = possessions_general(
        fgm=fgm,
        fga=fga,
        ftm=ftm,
        fta=fta,
        oreb=oreb,
        dreb_opp=dreb_opp,
        tov=tov,
        alpha=1.0,
    )
    poss_gained = possessions_general(
        fgm=fgm,
        fga=fga,
        ftm=ftm,
        fta=fta,
        oreb=oreb,
        dreb_opp=dreb_opp,
        tov=tov,
        alpha=0.0,
    )
    print(f"\n  General formula (alpha=1.0, 'poss lost'):   {poss_lost:.1f}")
    print(f"  General formula (alpha=0.0, 'poss gained'): {poss_gained:.1f}")

    # --- Floor and play percentages ---
    pts = 112
    fp = floor_pct(pts=pts, poss=poss)
    pp = play_pct(pts=pts, total_plays=play_count)
    print(f"\n  Scoring: {pts} pts on {poss:.0f} poss / {play_count:.0f} plays")
    print(f"  Floor%:  {fp:.3f}" if fp is not None else "  Floor%:  —")
    print(f"  Play%:   {pp:.3f}" if pp is not None else "  Play%:   —")

    # --- NBA Efficiency ---
    eff = nba_efficiency(
        pts=25,
        reb=10,
        ast=5,
        stl=2,
        blk=1,
        tov=3,
        fgm=10,
        fga=18,
        ftm=5,
        fta=6,
    )
    print(f"\n  NBA Efficiency (25/10/5/2/1 with 10-18 FG, 5-6 FT, 3 TO): {eff:.0f}")

    # --- Win expectation: Pythagorean vs Bell Curve ---
    ppg, opp_ppg, std_net = 110.0, 105.0, 12.0
    pyth = pythagorean_win_pct(pts=ppg, opp_pts=opp_ppg)
    pyth_kubatko = pythagorean_win_pct(pts=ppg, opp_pts=opp_ppg, exp=16.5)
    bell = bell_curve_win_pct(ppg=ppg, opp_ppg=opp_ppg, std_net_pts=std_net)
    print(f"\n  Win% estimates for {ppg:.0f} PPG vs {opp_ppg:.0f} OPP_PPG:")
    print(f"    Pythagorean (e=13.91): {pyth:.3f}" if pyth is not None else "    Pythagorean: —")
    print(
        f"    Pythagorean (e=16.5):  {pyth_kubatko:.3f}"
        if pyth_kubatko is not None
        else "    Pythagorean: —"
    )
    print(
        f"    Bell Curve (std={std_net}): {bell:.3f}" if bell is not None else "    Bell Curve: —"
    )

    # Show Bell Curve sensitivity to variance
    for std in [8.0, 12.0, 20.0]:
        bc = bell_curve_win_pct(ppg=ppg, opp_ppg=opp_ppg, std_net_pts=std)
        print(
            f"    Bell Curve (std={std:4.1f}):  {bc:.3f}"
            if bc is not None
            else f"    Bell Curve (std={std}): —"
        )
    print()


async def main() -> None:
    demo_single_line()
    demo_rate_stats()
    demo_on_floor_metrics()
    demo_per_calculation()
    demo_bpm_vorp()
    demo_team_ratings()
    demo_rolling_avg()
    demo_win_shares()
    demo_distribution_stats()
    demo_advanced_distribution()
    demo_recent_form()
    demo_ewma()
    demo_kubatko()

    yesterday = (
        datetime.now(tz=UTC).astimezone().date() - timedelta(days=1)
    ).isoformat()
    await game_score_leaderboard(yesterday)
    await usage_leaderboard(yesterday)
    await win_shares_leaderboard(yesterday)
    await player_prop_profile(player_id=1630162, player_name="Anthony Edwards")


if __name__ == "__main__":
    asyncio.run(main())
