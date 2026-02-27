"""Derived basketball metrics computed from traditional box score statistics.

Most functions accept raw counting stats and return a computed rate, ratio, or
index.  Functions with a division guard return ``None`` when the denominator is
zero rather than raising.  ``game_score``, ``is_double_double``, and
``is_triple_double`` never return ``None``.

All functions assume finite, non-negative inputs.  Passing ``nan`` or ``inf``
produces unspecified results and is the caller's responsibility to prevent.

Examples::

    from fastbreak.metrics import true_shooting, game_score, per_36

    ts = true_shooting(pts=28, fga=18, fta=6)   # → 0.678
    gs = game_score(pts=28, fgm=11, fga=19, ftm=7, fta=9,
                    oreb=1, dreb=8, stl=2, ast=8, blk=1, pf=3, tov=4)  # → 24.5
    pts_per_36 = per_36(stat=20, minutes=30)     # → 24.0

    lg = LeagueAverages(lg_pts=114.0, lg_fga=88.0, ...)
    aper = pace_adjusted_per(fgm=11, ..., team_pace=101.2, lg=lg)
    player_per = per(aper=aper, lg_aper=0.516)   # → ~18
"""

from dataclasses import dataclass, fields


@dataclass(frozen=True, slots=True)
class LeagueAverages:
    """League-wide season totals used to normalise per-player metrics.

    Pass per-team-per-game averages (or whole-league totals — as long as the
    scale is consistent across all fields).  Derived constants (``vop``,
    ``drb_pct``, etc.) are recomputed on each property access.

    Raises ``ValueError`` on construction if any field is negative, if
    ``lg_fga``, ``lg_treb``, ``lg_fgm``, ``lg_ftm``, ``lg_pf``, or
    ``lg_pace`` is zero, if ``lg_oreb > lg_treb``, or if the ``vop`` compound
    denominator (``lg_fga - lg_oreb + lg_tov + 0.44*lg_fta``) is not
    positive.

    Attributes:
        lg_pts:   League average points per team per game.
        lg_fga:   League average field goal attempts.
        lg_fta:   League average free throw attempts.
        lg_ftm:   League average free throws made.
        lg_oreb:  League average offensive rebounds.
        lg_treb:  League average total rebounds.
        lg_ast:   League average assists.
        lg_fgm:   League average field goals made.
        lg_fg3m:  League average 3-pointers made.
        lg_tov:   League average turnovers.
        lg_pf:    League average personal fouls.
        lg_pace:  Estimated league average possessions per game
                  (fga - oreb + tov + 0.44*fta), used as the pace denominator in PER.
    """

    lg_pts: float
    lg_fga: float
    lg_fta: float
    lg_ftm: float
    lg_oreb: float
    lg_treb: float
    lg_ast: float
    lg_fgm: float
    lg_fg3m: float
    lg_tov: float
    lg_pf: float
    lg_pace: float

    def __post_init__(self) -> None:
        # Non-negativity: auto-discovers all fields so new ones are validated without changes here
        negative = [f.name for f in fields(self) if getattr(self, f.name) < 0]
        if negative:
            vals = ", ".join(f"{n}={getattr(self, n)}" for n in negative)
            msg = f"LeagueAverages fields must be non-negative: {vals}"
            raise ValueError(msg)
        # Individual denominators that must be strictly positive
        denominator_fields = (
            "lg_fga",
            "lg_treb",
            "lg_fgm",
            "lg_ftm",
            "lg_pf",
            "lg_pace",
        )
        for name in denominator_fields:
            if getattr(self, name) == 0:
                msg = f"LeagueAverages.{name} must be positive (used as a denominator), got 0"
                raise ValueError(msg)
        # Cross-field: offensive rebounds cannot exceed total rebounds
        if self.lg_oreb > self.lg_treb:
            msg = f"lg_oreb ({self.lg_oreb}) cannot exceed lg_treb ({self.lg_treb})"
            raise ValueError(msg)
        # Compound vop denominator must be positive
        vop_denom = self.lg_fga - self.lg_oreb + self.lg_tov + 0.44 * self.lg_fta
        if vop_denom <= 0:
            msg = (
                f"LeagueAverages vop denominator (lg_fga - lg_oreb + lg_tov + 0.44*lg_fta)"
                f" must be positive, got {vop_denom}"
            )
            raise ValueError(msg)

    @property
    def vop(self) -> float:
        """Value of a Possession = lg_pts / (lg_fga - lg_oreb + lg_tov + 0.44*lg_fta)."""
        return self.lg_pts / (
            self.lg_fga - self.lg_oreb + self.lg_tov + 0.44 * self.lg_fta
        )

    @property
    def drb_pct(self) -> float:
        """League defensive rebound rate = (lg_treb - lg_oreb) / lg_treb."""
        return (self.lg_treb - self.lg_oreb) / self.lg_treb

    @property
    def factor(self) -> float:
        """Assist factor used in PER = 2/3 - (0.5*(lg_ast/lg_fgm)) / (2*(lg_fgm/lg_ftm))."""
        return 2 / 3 - (0.5 * (self.lg_ast / self.lg_fgm)) / (
            2 * (self.lg_fgm / self.lg_ftm)
        )

    @property
    def ts(self) -> float:
        """League average True Shooting% = lg_pts / (2*(lg_fga + 0.44*lg_fta))."""
        return self.lg_pts / (2 * (self.lg_fga + 0.44 * self.lg_fta))

    @property
    def efg(self) -> float:
        """League average eFG% = (lg_fgm + 0.5*lg_fg3m) / lg_fga."""
        return (self.lg_fgm + 0.5 * self.lg_fg3m) / self.lg_fga


def true_shooting(pts: float, fga: float, fta: float) -> float | None:
    """True Shooting percentage — shooting efficiency accounting for all shot types.

    TS% = pts / (2 * (FGA + 0.44 * FTA))

    The 0.44 multiplier on FTA reflects that not all free throw attempts represent
    a full possession (e.g., and-one trips to the line cost fewer possessions).

    Returns None when both FGA and FTA are zero.
    """
    denominator = 2 * (fga + 0.44 * fta)
    if denominator == 0:
        return None
    return pts / denominator


def effective_fg_pct(fgm: float, fg3m: float, fga: float) -> float | None:
    """Effective Field Goal percentage — adjusts FG% to credit 3-pointers.

    eFG% = (FGM + 0.5 * FG3M) / FGA

    A made 3-pointer is worth 1.5x a made 2-pointer, so eFG% gives 3-pointers
    their fair weight in a single shooting number.

    Returns None when FGA is zero.
    """
    if fga == 0:
        return None
    return (fgm + 0.5 * fg3m) / fga


def free_throw_rate(fta: float, fga: float) -> float | None:
    """Free Throw Rate — how often a player gets to the line relative to FGA.

    FTr = FTA / FGA

    Values above 1.0 are valid for aggressive attackers who draw more foul
    trips than field goal attempts.

    Returns None when FGA is zero.
    """
    if fga == 0:
        return None
    return fta / fga


def three_point_rate(fg3a: float, fga: float) -> float | None:
    """Three-Point Attempt Rate — share of field goal attempts from beyond the arc.

    3PAr = FG3A / FGA

    Returns None when FGA is zero.
    """
    if fga == 0:
        return None
    return fg3a / fga


def ast_to_tov(ast: float, tov: float) -> float | None:
    """Assist-to-Turnover ratio — playmaking efficiency.

    AST/TOV = AST / TOV

    Higher is better; elite playmakers typically exceed 3.0 for a season.

    Returns None when turnovers are zero to avoid division by zero.
    """
    if tov == 0:
        return None
    return ast / tov


def game_score(  # noqa: PLR0913
    pts: float,
    fgm: float,
    fga: float,
    ftm: float,
    fta: float,
    oreb: float,
    dreb: float,
    stl: float,
    ast: float,
    blk: float,
    pf: float,
    tov: float,
) -> float:
    """Hollinger's Game Score — single-number summary of a box score line.

    GmSc = PTS + 0.4*FGM - 0.7*FGA - 0.4*(FTA - FTM)
           + 0.7*OREB + 0.3*DREB + STL + 0.7*AST + 0.7*BLK - 0.4*PF - TOV

    Roughly calibrated so that 10 is an average game and 40+ is exceptional.
    Can be negative for very poor shooting lines.
    """
    return (
        pts
        + 0.4 * fgm
        - 0.7 * fga
        - 0.4 * (fta - ftm)
        + 0.7 * oreb
        + 0.3 * dreb
        + stl
        + 0.7 * ast
        + 0.7 * blk
        - 0.4 * pf
        - tov
    )


def per_36(stat: float, minutes: float) -> float | None:
    """Normalize a counting stat to a per-36-minute pace.

    per_36 = stat * 36 / minutes

    36 minutes is the conventional baseline (roughly a starter's workload).

    Returns None when minutes are zero.
    """
    if minutes == 0:
        return None
    return stat * 36 / minutes


_DOUBLE_DIGIT_THRESHOLD: int = 10


def _count_double_digit_categories(
    pts: float, reb: float, ast: float, stl: float, blk: float
) -> int:
    """Return how many of the five counting categories are at 10 or above."""
    return sum(1 for c in (pts, reb, ast, stl, blk) if c >= _DOUBLE_DIGIT_THRESHOLD)


def is_double_double(
    pts: float,
    reb: float,
    ast: float,
    stl: float,
    blk: float,
) -> bool:
    """Return True if at least two of the five counting categories reach 10+."""
    return _count_double_digit_categories(pts, reb, ast, stl, blk) >= 2  # noqa: PLR2004


def is_triple_double(
    pts: float,
    reb: float,
    ast: float,
    stl: float,
    blk: float,
) -> bool:
    """Return True if at least three of the five counting categories reach 10+."""
    return _count_double_digit_categories(pts, reb, ast, stl, blk) >= 3  # noqa: PLR2004


def usage_pct(  # noqa: PLR0913
    fga: float,
    fta: float,
    tov: float,
    mp: float,
    team_fga: float,
    team_fta: float,
    team_tov: float,
    team_mp: float,
) -> float | None:
    """Usage percentage — share of team possessions used by the player while on floor.

    Usage% = (FGA + 0.44*FTA + TOV) * (team_MP/5) / (MP * (team_FGA + 0.44*team_FTA + team_TOV))

    The 0.44 FTA multiplier estimates possession cost (same as TS%).
    Dividing team_MP by 5 puts team and player minutes on the same per-person scale.
    A usage rate of ~0.20 is average; ~0.30+ is a primary scoring option.

    Returns None when player minutes or team possessions are zero.
    """
    team_poss = team_fga + 0.44 * team_fta + team_tov
    denominator = mp * team_poss
    if denominator == 0:
        return None
    player_poss = fga + 0.44 * fta + tov
    return player_poss * (team_mp / 5) / denominator


def ast_pct(
    ast: float,
    fgm: float,
    mp: float,
    team_fgm: float,
    team_mp: float,
) -> float | None:
    """Assist percentage — share of teammate field goals assisted while on floor.

    AST% = AST / ((MP / (team_MP / 5)) * team_FGM - FGM)

    The denominator estimates how many teammate baskets the player could
    have assisted: team FGM scaled to the player's time on floor, minus the
    player's own makes.

    Returns None when player or team minutes are zero, or when the denominator
    is non-positive (degenerate data).
    """
    if team_mp == 0 or mp == 0:
        return None
    denominator = (mp / (team_mp / 5)) * team_fgm - fgm
    if denominator <= 0:
        return None
    return ast / denominator


def _possession_pct(
    stat: float, mp: float, team_mp: float, opportunity: float
) -> float | None:
    """Compute a per-possession rate stat: stat * (team_MP/5) / (MP * opportunity).

    Returns None when player minutes or the opportunity count are zero.
    """
    denominator = mp * opportunity
    if denominator == 0:
        return None
    return stat * (team_mp / 5) / denominator


def oreb_pct(
    oreb: float,
    mp: float,
    team_oreb: float,
    opp_dreb: float,
    team_mp: float,
) -> float | None:
    """Offensive Rebound percentage — share of available offensive boards grabbed.

    OREB% = OREB * (team_MP/5) / (MP * (team_OREB + opp_DREB))

    The denominator is total offensive rebounds available: every missed shot
    by the player's team that was either grabbed offensively or conceded.

    Returns None when player minutes or available rebounds are zero.
    """
    return _possession_pct(oreb, mp, team_mp, team_oreb + opp_dreb)


def dreb_pct(
    dreb: float,
    mp: float,
    team_dreb: float,
    opp_oreb: float,
    team_mp: float,
) -> float | None:
    """Defensive Rebound percentage — share of available defensive boards grabbed.

    DREB% = DREB * (team_MP/5) / (MP * (team_DREB + opp_OREB))

    The denominator is total defensive rebounds available: every opponent
    miss that was either secured defensively or retrieved by the opponent.

    Returns None when player minutes or available rebounds are zero.
    """
    return _possession_pct(dreb, mp, team_mp, team_dreb + opp_oreb)


def stl_pct(
    stl: float,
    mp: float,
    team_mp: float,
    opp_poss: float,
) -> float | None:
    """Steal percentage — share of opponent possessions ending in a steal.

    STL% = STL * (team_MP/5) / (MP * opp_poss)

    ``opp_poss`` is typically estimated as: opp_FGA + 0.44*opp_FTA + opp_TOV - opp_OREB.

    Returns None when player minutes or opponent possessions are zero.
    """
    return _possession_pct(stl, mp, team_mp, opp_poss)


def blk_pct(
    blk: float,
    mp: float,
    team_mp: float,
    opp_fg2a: float,
) -> float | None:
    """Block percentage — share of opponent 2-point attempts blocked.

    BLK% = BLK * (team_MP/5) / (MP * opp_FG2A)

    Only 2-point attempts are used because 3-pointers are almost never blocked,
    so including them would dilute the signal.
    ``opp_fg2a`` = opp_FGA - opp_FG3A.

    Returns None when player minutes or opponent 2-point attempts are zero.
    """
    return _possession_pct(blk, mp, team_mp, opp_fg2a)


def pace_adjusted_per(  # noqa: PLR0913
    fgm: float,
    fga: float,
    fg3m: float,
    ftm: float,
    fta: float,
    oreb: float,
    treb: float,
    ast: float,
    stl: float,
    blk: float,
    pf: float,
    tov: float,
    mp: float,
    team_ast: float,
    team_fgm: float,
    team_pace: float,
    lg: LeagueAverages,
) -> float | None:
    """Pace-adjusted PER (aPER) — the first of two steps toward a full PER.

    Implements Hollinger's unadjusted PER formula then scales by the ratio of
    league pace to team pace.  The caller must then collect aPER values for all
    players, compute a weighted league average (``lg_aper``), and call :func:`per`
    to normalise to the conventional 15.0 baseline.

    Args:
        fgm:        Field goals made.
        fga:        Field goals attempted.
        fg3m:       Three-pointers made.
        ftm:        Free throws made.
        fta:        Free throws attempted.
        oreb:       Offensive rebounds.
        treb:       Total rebounds.
        ast:        Assists.
        stl:        Steals.
        blk:        Blocks.
        pf:         Personal fouls.
        tov:        Turnovers.
        mp:         Minutes played.
        team_ast:   Team assists (same game / period as player stats).
        team_fgm:   Team field goals made.
        team_pace:  Team pace (possessions per 48 minutes).
        lg:         League-wide season averages.

    Returns:
        Pace-adjusted PER, or ``None`` when ``mp``, ``team_fgm``, or
        ``team_pace`` is zero.
    """
    if mp == 0 or team_fgm == 0 or team_pace == 0:
        return None

    team_ast_ratio = team_ast / team_fgm

    uper = (1 / mp) * (
        fg3m
        + (2 / 3) * ast
        + (2 - lg.factor * team_ast_ratio) * fgm
        + ftm * 0.5 * (1 + (1 - team_ast_ratio) + (2 / 3) * team_ast_ratio)
        - lg.vop * tov
        - lg.vop * lg.drb_pct * (fga - fgm)
        - lg.vop * 0.44 * (0.44 + 0.56 * lg.drb_pct) * (fta - ftm)
        + lg.vop * (1 - lg.drb_pct) * (treb - oreb)
        + lg.vop * lg.drb_pct * oreb
        + lg.vop * stl
        + lg.vop * lg.drb_pct * blk
        - pf * (lg.lg_ftm / lg.lg_pf - 0.44 * (lg.lg_fta / lg.lg_pf) * lg.vop)
    )
    return (lg.lg_pace / team_pace) * uper


def per(aper: float, lg_aper: float) -> float | None:
    """Normalise pace-adjusted PER to the conventional 15.0 league-average baseline.

    PER = aPER * (15 / lg_aPER)

    Calibrated so 15.0 is league-average; a 25 PER is a borderline All-Star, 30+ is rare.

    Args:
        aper:    Pace-adjusted PER for the player (from :func:`pace_adjusted_per`).
        lg_aper: League average aPER (weighted mean across all player-minutes).

    Returns:
        Normalised PER, or ``None`` when ``lg_aper`` is zero.
    """
    if lg_aper == 0:
        return None
    return aper * (15 / lg_aper)


def relative_ts(player_ts: float | None, lg: LeagueAverages) -> float | None:
    """Player True Shooting% minus league average TS%.

    Positive means more efficient than league average.

    Returns None when ``player_ts`` is None (player had no shot attempts).
    """
    if player_ts is None:
        return None
    return player_ts - lg.ts


def relative_efg(player_efg: float | None, lg: LeagueAverages) -> float | None:
    """Player Effective Field Goal% minus league average eFG%.

    Positive means more efficient than league average.

    Returns None when ``player_efg`` is None (player had no field goal attempts).
    """
    if player_efg is None:
        return None
    return player_efg - lg.efg


def _possessions(fga: float, oreb: float, tov: float, fta: float) -> float:
    """Estimate team possessions using Dean Oliver's formula."""
    return fga - oreb + tov + 0.44 * fta


def ortg(
    pts: float,
    fga: float,
    oreb: float,
    tov: float,
    fta: float,
) -> float | None:
    """Offensive rating: points scored per 100 possessions.

    Args:
        pts: Points scored
        fga: Field goal attempts
        oreb: Offensive rebounds
        tov: Turnovers
        fta: Free throw attempts

    Returns:
        Points per 100 possessions, or None if possessions == 0.
    """
    poss = _possessions(fga, oreb, tov, fta)
    if poss == 0:
        return None
    return pts / poss * 100


def drtg(
    opp_pts: float,
    fga: float,
    oreb: float,
    tov: float,
    fta: float,
) -> float | None:
    """Defensive rating: opponent points allowed per 100 possessions.

    Args:
        opp_pts: Opponent points allowed
        fga: Team field goal attempts (used to estimate possessions)
        oreb: Team offensive rebounds
        tov: Team turnovers
        fta: Team free throw attempts

    Returns:
        Opponent points per 100 team possessions, or None if possessions == 0.
    """
    poss = _possessions(fga, oreb, tov, fta)
    if poss == 0:
        return None
    return opp_pts / poss * 100


def net_rtg(ortg_val: float | None, drtg_val: float | None) -> float | None:
    """Net rating: ORTG minus DRTG.

    Args:
        ortg_val: Offensive rating (from ortg())
        drtg_val: Defensive rating (from drtg())

    Returns:
        Net rating, or None if either input is None.
    """
    if ortg_val is None or drtg_val is None:
        return None
    return ortg_val - drtg_val
