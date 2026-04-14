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

import bisect
from collections.abc import Sequence
from dataclasses import dataclass, field, fields
from math import erf, pow as fpow, sqrt as fsqrt


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
        lg_pace:  Derived read-only property: lg_fga - lg_oreb + lg_tov + 0.44*lg_fta.
                  Used as the pace denominator in PER and identical to the vop denominator,
                  guaranteeing internal consistency.
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
    _pace_denom: float = field(init=False, repr=False)

    def __post_init__(self) -> None:
        # Non-negativity: skip init=False fields (not yet assigned when this runs)
        negative = [
            f.name for f in fields(self) if f.init and getattr(self, f.name) < 0
        ]
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
        )
        for name in denominator_fields:
            if getattr(self, name) == 0:
                msg = f"LeagueAverages.{name} must be positive (used as a denominator), got 0"
                raise ValueError(msg)
        # Cross-field: offensive rebounds cannot exceed total rebounds
        if self.lg_oreb > self.lg_treb:
            msg = f"lg_oreb ({self.lg_oreb}) cannot exceed lg_treb ({self.lg_treb})"
            raise ValueError(msg)
        # Compound vop denominator must be positive; store for reuse in vop and lg_pace
        vop_denom = self.lg_fga - self.lg_oreb + self.lg_tov + 0.44 * self.lg_fta
        if vop_denom <= 0:
            msg = (
                f"LeagueAverages vop denominator (lg_fga - lg_oreb + lg_tov + 0.44*lg_fta)"
                f" must be positive, got {vop_denom}"
            )
            raise ValueError(msg)
        object.__setattr__(self, "_pace_denom", vop_denom)

    @property
    def vop(self) -> float:
        """Value of a Possession = lg_pts / (lg_fga - lg_oreb + lg_tov + 0.44*lg_fta)."""
        return self.lg_pts / self._pace_denom

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

    @property
    def lg_pace(self) -> float:
        """Possession estimate used as the league pace proxy in PER.

        lg_pace = lg_fga - lg_oreb + lg_tov + 0.44*lg_fta

        This is the Dean Oliver possession-count formula applied to per-team-per-game
        league averages.  It is identical to the ``vop`` denominator, guaranteeing
        internal consistency across PER calculations.

        Note on units: when passing ``team_pace`` to ``pace_adjusted_per``, use
        the same formula (``fga - oreb + tov + 0.44*fta``) applied to team totals
        for the same time window.  For a full NBA game this gives approximately the
        same numeric value as "possessions per 48 minutes" (~95-105 for modern teams).
        """
        return self._pace_denom


def true_shooting(pts: float, fga: float, fta: float) -> float | None:
    """True Shooting percentage — shooting efficiency accounting for all shot types.

    TS% = pts / (2 * (FGA + 0.44 * FTA))

    The 0.44 multiplier on FTA reflects that not all free throw attempts represent
    a full possession (e.g., and-one trips to the line cost fewer possessions).

    Values above 1.0 are valid in rare edge cases where a player scores many points
    on very few possession-equivalent attempts (e.g., drawing many and-one free
    throws on a small FGA sample).

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

    Values above 1.0 are valid when a player makes more 3-pointers than 2-pointers
    on a small sample (e.g., fgm=4, fg3m=4, fga=5 → eFG% = 1.2).

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


def tov_pct(fga: float, fta: float, tov: float) -> float | None:
    """Turnover percentage — share of possessions ending in a turnover.

    TOV% = TOV / (FGA + 0.44 * FTA + TOV)

    The denominator uses Dean Oliver's possession estimate, keeping the
    0.44 FTA multiplier consistent with true_shooting and usage_pct.

    Returns a **0-1 fraction** (e.g. 0.126 for 12.6%). This matches the
    scale used by ``FourFactorsStatistics.teamTurnoverPercentage`` (box
    score four-factors endpoint). It does *not* match
    ``AdvancedTeamStatistics.estimatedTeamTurnoverPercentage``, which the
    NBA advanced box-score endpoint returns on a **0-100 scale** (e.g.
    12.6). Multiply by 100 before comparing against that field.

    Returns None when there was no offensive activity (all three inputs zero).
    """
    denominator = fga + 0.44 * fta + tov
    if denominator == 0:
        return None
    return tov / denominator


@dataclass(frozen=True, slots=True)
class FourFactors:
    """Dean Oliver's Four Factors — the four team efficiency components.

    All four fields can be ``None`` when the underlying denominator is zero
    (e.g., a team that took no field goal attempts).

    Attributes:
        efg_pct:  Effective Field Goal% = (FGM + 0.5*FG3M) / FGA.
        tov_pct:  Turnover% = TOV / (FGA + 0.44*FTA + TOV).
        oreb_pct: Team Offensive Rebound% = OREB / (OREB + opp_DREB).
        ftr:      Free Throw Rate = FTA / FGA.
    """

    efg_pct: float | None
    tov_pct: float | None
    oreb_pct: float | None
    ftr: float | None


@dataclass(frozen=True, slots=True)
class BPMResult:
    """Box Plus/Minus 2.0 results (Myers, Basketball Reference).

    All values are in points per 100 team possessions relative to
    league average (0.0 = league average, positive = above average).

    The *raw* BPM returned by :func:`bpm` does not include the team
    adjustment.  To fully reproduce Basketball Reference's published
    numbers, add the team adjustment constant to ``total`` and
    ``offensive`` (and recompute ``defensive``) so that the
    minutes-weighted sum of all players on a roster equals the team's
    observed adjusted efficiency differential.

    Attributes:
        total:     Total BPM (offensive + defensive combined).
        offensive: Offensive BPM (OBPM).
        defensive: Defensive BPM (DBPM = total - offensive).
    """

    total: float
    offensive: float
    defensive: float


def four_factors(  # noqa: PLR0913
    fgm: float,
    fg3m: float,
    fga: float,
    tov: float,
    fta: float,
    oreb: float,
    opp_dreb: float,
) -> FourFactors:
    """Compute Dean Oliver's Four Factors for a single team performance.

    Args:
        fgm:      Field goals made.
        fg3m:     Three-pointers made.
        fga:      Field goals attempted.
        tov:      Turnovers.
        fta:      Free throw attempts.
        oreb:     Offensive rebounds.
        opp_dreb: Opponent defensive rebounds.

    Returns:
        FourFactors with all four components.  Individual components are None
        when their denominator is zero (see per-field docs on FourFactors).
    """
    total_reb = oreb + opp_dreb
    oreb_rate: float | None = oreb / total_reb if total_reb > 0 else None

    return FourFactors(
        efg_pct=effective_fg_pct(fgm=fgm, fg3m=fg3m, fga=fga),
        tov_pct=tov_pct(fga=fga, fta=fta, tov=tov),
        oreb_pct=oreb_rate,
        ftr=free_throw_rate(fta=fta, fga=fga),
    )


def ast_to_tov(ast: float, tov: float) -> float | None:
    """Assist-to-Turnover ratio — playmaking efficiency.

    AST/TOV = AST / TOV

    Higher is better; elite playmakers typically exceed 3.0 for a season.

    Returns None when turnovers are zero to avoid division by zero.
    """
    if tov == 0:
        return None
    return ast / tov


def assist_ratio(ast: float, fga: float, fta: float, tov: float) -> float | None:
    """Assist ratio — assists per 100 offensive plays.

    AST Ratio = AST / (FGA + 0.44*FTA + AST + TOV) * 100

    The denominator covers all offensive plays: field goal attempts, approximate
    free-throw trips, assists, and turnovers.  A value of 20 means the player
    recorded an assist on 20 out of every 100 offensive actions.

    Unlike ``ast_pct``, this requires no team or minutes context and is computed
    entirely from the individual's own box line.  This matches the ``assistRatio``
    field in the NBA v3 box score model.

    Returns None when offensive plays are zero.
    """
    denominator = fga + 0.44 * fta + ast + tov
    if denominator == 0:
        return None
    return ast / denominator * 100


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


def nba_efficiency(  # noqa: PLR0913
    pts: float,
    reb: float,
    ast: float,
    stl: float,
    blk: float,
    tov: float,
    fgm: float,
    fga: float,
    ftm: float,
    fta: float,
) -> float:
    """NBA Efficiency — the simple linear weights stat used on NBA.com.

    EFF = PTS + REB + AST + STL + BLK - TOV - (FGA - FGM) - (FTA - FTM)

    Simpler than Game Score or PER — equal weight to every positive and
    negative contribution.  Useful as a quick single-number box score summary
    but criticized for rewarding volume and ignoring defense beyond steals
    and blocks (Kubatko et al. 2007, Eq. 19).

    Typical values: ~15 for an average starter, 30+ for elite performances.
    Can be negative for extremely poor lines.
    """
    return pts + reb + ast + stl + blk - tov - (fga - fgm) - (fta - ftm)


def per_36(stat: float, minutes: float) -> float | None:
    """Normalize a counting stat to a per-36-minute pace.

    per_36 = stat * 36 / minutes

    36 minutes is the conventional baseline (roughly a starter's workload).

    Returns None when minutes are zero.
    """
    if minutes == 0:
        return None
    return stat * 36 / minutes


def per_48(stat: float, minutes: float) -> float | None:
    """Normalize a counting stat to a per-48-minute pace.

    per_48 = stat * 48 / minutes

    48 minutes is one full NBA game. Use this for net rating and lineup
    efficiency stats that are conventionally reported per 48 minutes.

    Returns None when minutes are zero.
    """
    if minutes == 0:
        return None
    return stat * 48 / minutes


def per_40(stat: float, minutes: float) -> float | None:
    """Normalize a counting stat to a per-40-minute pace.

    per_40 = stat * 40 / minutes

    40 minutes is one full WNBA game. The WNBA equivalent of
    :func:`per_48` for intra-league comparisons.

    Returns None when minutes are zero.
    """
    if minutes == 0:
        return None
    return stat * 40 / minutes


def per_100(stat: float, poss: float) -> float | None:
    """Normalize a counting stat to a per-100-possessions rate.

    per_100 = stat * 100 / poss

    Use ``possessions(fga, oreb, tov, fta)`` from this module (or any other
    possession estimate) as the ``poss`` argument for team-level data.

    Returns None when possessions are zero.
    """
    if poss == 0:
        return None
    return stat * 100 / poss


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
        team_pace:  Team pace in the same units as ``lg.lg_pace`` — estimated as
                    ``fga - oreb + tov + 0.44*fta`` for the team over the same
                    time window.  For a full NBA game this is numerically equivalent
                    to possessions per 48 minutes (~95-105).
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


def bpm(  # noqa: PLR0913
    pts: float,
    fg3m: float,
    ast: float,
    tov: float,
    orb: float,
    drb: float,
    stl: float,
    blk: float,
    pf: float,
    fga: float,
    fta: float,
    *,
    pct_team_trb: float,
    pct_team_stl: float,
    pct_team_pf: float,
    pct_team_ast: float,
    pct_team_blk: float,
    pct_team_pts: float,
    listed_position: float = 3.0,
    mp: float = 500.0,
) -> BPMResult | None:
    """Compute Box Plus/Minus 2.0 (raw, without team adjustment).

    Implements Daniel Myers' BPM 2.0 formula (Basketball Reference).
    Position (1=PG -> 5=C) and offensive role (1=Creator -> 5=Receiver)
    are estimated from team-percentage inputs using the BPM regressions,
    then smoothed against a prior: 50 minutes at ``listed_position`` for
    position, and 50 minutes at role 4.0 (off-ball scorer) for role.

    All counting stats must be **per-100 team possessions**.  Team
    percentages are the player's share of team counting stats while on
    court (0-1 scale).

    The returned values do **not** include the team adjustment constant --
    that requires the full roster and is applied externally so the
    minutes-weighted team total equals the team's adjusted efficiency
    differential.

    Args:
        pts:             Points per 100 team possessions.
        fg3m:            Three-pointers made per 100.
        ast:             Assists per 100.
        tov:             Turnovers per 100.
        orb:             Offensive rebounds per 100.
        drb:             Defensive rebounds per 100.
        stl:             Steals per 100.
        blk:             Blocks per 100.
        pf:              Personal fouls per 100.
        fga:             Field goal attempts per 100.
        fta:             Free throw attempts per 100.
        pct_team_trb:    Player's fraction of team total rebounds (0-1).
        pct_team_stl:    Player's fraction of team steals (0-1).
        pct_team_pf:     Player's fraction of team personal fouls (0-1).
        pct_team_ast:    Player's fraction of team assists (0-1).
        pct_team_blk:    Player's fraction of team blocks (0-1).
        pct_team_pts:    Player's fraction of team points (0-1), used as
                         a proxy for % of team threshold points in the
                         role regression.
        listed_position: Positional designation (1=PG, 2=SG, 3=SF,
                         4=PF, 5=C).  Anchors the position estimate
                         against small samples.  Default 3.0 (neutral).
        mp:              Minutes played; governs how heavily the
                         box-score estimates are trusted vs. priors.
                         Higher mp -> estimates weighted more.

    Returns:
        :class:`BPMResult` with raw total, offensive, and defensive BPM,
        or ``None`` when ``mp`` is zero or negative (no playing time).
    """
    if mp <= 0:
        return None

    # ── Step 1: Estimate position (1=PG, 5=C) ─────────────────────────────
    raw_pos = (
        2.130
        + 8.668 * pct_team_trb
        - 2.486 * pct_team_stl
        + 0.992 * pct_team_pf
        - 3.536 * pct_team_ast
        + 1.667 * pct_team_blk
    )
    position = (raw_pos * mp + listed_position * 50.0) / (mp + 50.0)
    position = max(1.0, min(5.0, position))

    # ── Step 2: Estimate offensive role (1=Creator, 5=Receiver) ───────────
    # Creator: high AST%, high share of team scoring (self-created).
    raw_role = 6.00 - 6.642 * pct_team_ast - 8.544 * pct_team_pts
    role = (raw_role * mp + 4.0 * 50.0) / (mp + 50.0)
    role = max(1.0, min(5.0, role))

    # ── Step 3: Position/role coefficient interpolators ────────────────────
    def _pos(c1: float, c5: float) -> float:
        return c1 + (position - 1.0) / 4.0 * (c5 - c1)

    def _role(c1: float, c5: float) -> float:
        return c1 + (role - 1.0) / 4.0 * (c5 - c1)

    # ── Step 4: Additive position/role constants ───────────────────────────
    # Position constant: linear from constant at pos=1 to 0.0 at pos>=3.
    pos_factor = max(0.0, 3.0 - position) / 2.0
    pos_const_bpm = -0.818 * pos_factor
    pos_const_obpm = -1.698 * pos_factor

    # Role constant: linear from -C at role=1 to +C at role=5 (0 at role=3).
    role_const_bpm = -2.774 + (role - 1.0) / 4.0 * 5.548
    role_const_obpm = -0.860 + (role - 1.0) / 4.0 * 1.720

    # ── Step 5: Raw Total BPM ──────────────────────────────────────────────
    raw_total = (
        0.860 * pts
        + 0.389 * fg3m
        + _pos(0.580, 1.034) * ast
        - 0.964 * tov
        + _pos(0.613, 0.181) * orb
        + _pos(0.116, 0.181) * drb
        + _pos(1.369, 1.008) * stl
        + _pos(1.327, 0.703) * blk
        - 0.367 * pf
        + _role(-0.560, -0.780) * fga
        + _role(-0.246, -0.343) * fta
        + pos_const_bpm
        + role_const_bpm
    )

    # ── Step 6: Raw OBPM ───────────────────────────────────────────────────
    raw_obpm = (
        0.605 * pts
        + 0.477 * fg3m
        + 0.476 * ast  # uniform across positions for OBPM
        + _pos(-0.579, -0.882) * tov
        + _pos(0.606, 0.422) * orb
        + _pos(-0.112, 0.103) * drb
        + _pos(0.177, 0.294) * stl
        + _pos(0.725, 0.097) * blk
        - 0.439 * pf
        + _role(-0.330, -0.472) * fga
        + _role(-0.145, -0.208) * fta
        + pos_const_obpm
        + role_const_obpm
    )

    return BPMResult(
        total=raw_total,
        offensive=raw_obpm,
        defensive=raw_total - raw_obpm,
    )


def vorp(
    bpm_total: float,
    poss_pct: float,
    games: int,
    *,
    replacement_level: float = -2.0,
    season_games: int = 82,
) -> float:
    """Compute Value Over Replacement Player (VORP).

    VORP = (BPM - replacement_level) * poss_pct * (games / season_games)

    Measures a player's total contribution relative to a freely-available
    replacement-level player, scaled to a full season.  Multiply by
    2.7 to convert to approximate wins above replacement.

    Args:
        bpm_total:         Total BPM (from :func:`bpm`).
        poss_pct:          Fraction of team possessions the player
                           participated in -- typically
                           ``mp / (team_games * game_minutes)``, where
                           ``game_minutes`` is 48 (NBA) or 40 (WNBA)
                           and the denominator approximates total
                           team minutes divided by 5 (five players
                           on court).
        games:             Team games played.
        replacement_level: BPM of a replacement-level player.
                           Defaults to -2.0 per Myers BPM 2.0.
        season_games:      Number of regular-season games for the league.
                           Defaults to 82 (NBA). Use 40 for WNBA.

    Returns:
        VORP as a float.  Positive means above replacement level.

    Raises:
        ValueError: If ``season_games`` is not positive.
    """
    if season_games <= 0:
        msg = f"season_games must be > 0, got {season_games}"
        raise ValueError(msg)
    return (bpm_total - replacement_level) * poss_pct * (games / season_games)


def stat_delta(a: float | None, b: float | None) -> float | None:
    """Compute the difference between two stat values (a - b).

    Returns ``None`` if either value is ``None``.  Useful for comparing the
    same stat across two contexts (e.g., home FG% vs. road FG%, clutch TS%
    vs. regular-season TS%) without manually handling the None-guard each time.

    Args:
        a: First stat value.
        b: Second stat value.

    Returns:
        ``a - b`` if both are non-``None``, else ``None``.

    Examples::

        stat_delta(0.48, 0.41)   # → 0.07
        stat_delta(None, 0.41)   # → None
    """
    if a is None or b is None:
        return None
    return a - b


def relative_ts(player_ts: float | None, lg: LeagueAverages) -> float | None:
    """Player True Shooting% minus league average TS%.

    Positive means more efficient than league average.

    Returns None when ``player_ts`` is None (player had no shot attempts).
    """
    return stat_delta(player_ts, lg.ts)


def relative_efg(player_efg: float | None, lg: LeagueAverages) -> float | None:
    """Player Effective Field Goal% minus league average eFG%.

    Positive means more efficient than league average.

    Returns None when ``player_efg`` is None (player had no field goal attempts).
    """
    return stat_delta(player_efg, lg.efg)


def possessions(fga: float, oreb: float, tov: float, fta: float) -> float:
    """Estimate possessions using Dean Oliver's formula.

    poss = FGA - OREB + TOV + 0.44 * FTA

    The 0.44 multiplier accounts for free-throw trips that do not consume a full
    possession (and-ones, technical fouls, flagrants).  This is the same formula
    used internally by ``ortg``, ``drtg``, ``tov_pct``, and ``usage_pct``.

    Typical values: 95-105 for a modern NBA team in a full game.

    Returns a float >= 0; never returns None (the result is zero only when all
    inputs are zero, which is a valid degenerate case).
    """
    return fga - oreb + tov + 0.44 * fta


def possessions_general(  # noqa: PLR0913
    fgm: float,
    fga: float,
    ftm: float,
    fta: float,
    oreb: float,
    dreb_opp: float,
    tov: float,
    alpha: float = 1.0,
    lam: float = 0.44,
) -> float:
    """General possession formula from Kubatko et al. (2007), Eq. 1.

    POSS = (FGM + lam*FTM) + alpha*[(FGA-FGM) + lam*(FTA-FTM) - OREB]
           + (1-alpha)*DREB_opp + TO

    The ``alpha`` parameter controls how missed field goals and missed
    possession-ending free throws split credit between the offensive team
    (via offensive rebounds) and the defensive team (via defensive rebounds).
    When alpha=1, missed shots are fully charged to the offense and defensive
    rebounds have zero possession value -- this gives the common "possessions
    lost" formula.  When alpha=0, credit goes entirely to the defense and you
    get the "possessions gained" formula.

    The ``lam`` parameter is the fraction of free throws that end possessions
    (excluding and-ones, technicals, flagrants).  Empirically ~0.44 in the
    NBA (Kubatko et al. found 43.8% over 2002-06).

    The default (alpha=1, lam=0.44) reduces to :func:`possessions`:
    ``FGA + 0.44*FTA - OREB + TO``.

    Args:
        fgm:      Field goals made.
        fga:      Field goals attempted.
        ftm:      Free throws made.
        fta:      Free throw attempts.
        oreb:     Offensive rebounds.
        dreb_opp: Defensive rebounds for the opponent.
        tov:      Turnovers (including team turnovers).
        alpha:    Credit split parameter in [0, 1].  Default 1.0.
        lam:      Fraction of free throws ending possessions.  Default 0.44.
    """
    made = fgm + lam * ftm
    missed = alpha * ((fga - fgm) + lam * (fta - ftm) - oreb)
    opp_dreb = (1 - alpha) * dreb_opp
    return made + missed + opp_dreb + tov


def plays(fga: float, fta: float, tov: float) -> float:
    """Estimate plays (minor possessions) from box score stats.

    PLAYS = FGA + 0.44 * FTA + TO

    Plays differ from possessions because an offensive rebound starts a new
    *play* but not a new *possession*.  A team typically has more plays than
    possessions (~105 plays per ~92 possessions in 2002-06).

    The 0.44 multiplier is the same possession-ending free throw fraction
    used in :func:`possessions` (Kubatko et al. 2007, Eq. 7).
    """
    return fga + 0.44 * fta + tov


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
    poss = possessions(fga, oreb, tov, fta)
    if poss == 0:
        return None
    return pts / poss * 100


def drtg(
    opp_pts: float,
    opp_fga: float,
    opp_oreb: float,
    opp_tov: float,
    opp_fta: float,
) -> float | None:
    """Defensive rating: opponent points allowed per 100 opponent possessions.

    Args:
        opp_pts:  Opponent points allowed.
        opp_fga:  Opponent field goal attempts.
        opp_oreb: Opponent offensive rebounds.
        opp_tov:  Opponent turnovers.
        opp_fta:  Opponent free throw attempts.

    Returns:
        Opponent points per 100 opponent possessions, or None if possessions == 0.
    """
    poss = possessions(opp_fga, opp_oreb, opp_tov, opp_fta)
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
    return stat_delta(ortg_val, drtg_val)


def floor_pct(
    pts: float,
    poss: float,
) -> float | None:
    """Floor percentage — points scored per possession.

    Introduced by Oliver (2004) as a scoring-rate measure.  The name
    "floor percentage" is traditional but the value is pts / poss,
    which can exceed 1.0 (e.g. 112 pts on 100 possessions → 1.12).

    Args:
        pts:  Points scored.
        poss: Total possessions (from :func:`possessions`).

    Returns:
        Points per possession (unbounded above 1.0), or None when
        possessions is zero.

    Note:
        This is an *approximation* from box score data.  The exact count
        of scoring possessions requires play-by-play data (some possessions
        score 2 or 3 points, so pts/poss overstates the fraction).  A
        common proxy is (FGM + 0.44 * FTA) / POSS, which counts made
        field goals and possession-ending free throw attempts.
    """
    if poss == 0:
        return None
    return pts / poss


def play_pct(
    pts: float,
    total_plays: float,
) -> float | None:
    """Play percentage — points scored per play.

    Analogous to :func:`floor_pct` but uses plays (which count offensive
    rebounds as new opportunities) instead of possessions.  Because a team
    has more plays than possessions, points per play is always ≤ points per
    possession (floor percentage) for the same scoring output.

    Args:
        pts:         Points scored.
        total_plays: Total plays (from :func:`plays`).

    Returns:
        Points per play (unbounded above 1.0), or None when total_plays is zero.
    """
    if total_plays == 0:
        return None
    return pts / total_plays


def offensive_win_shares(
    pts: float,
    fga: float,
    fta: float,
    tov: float,
    lg: LeagueAverages,
) -> float | None:
    """Offensive Win Shares — player's estimated contribution to team wins on offense.

    OWS = marginal_offense / marginal_pts_per_win

    Where:
      player_poss          = 0.96 * (FGA + TOV + 0.44 * FTA)
      marginal_offense     = PTS - 0.92 * lg.vop * player_poss
      marginal_pts_per_win = 0.32 * lg.lg_pts

    The 0.96 factor adjusts for possessions lost to offensive fouls.  The 0.92
    threshold sets "replacement level" at 92% of league-average offensive efficiency
    (not zero); players below this threshold produce negative OWS.  The 0.32
    constant converts marginal points to wins, calibrated to the historical
    relationship between point differential and wins (Basketball-Reference method).

    Works with any time scale — per-game, per-season, or per-stint — as long as
    ``lg`` is calibrated to the same scale as the player inputs.

    Returns None only when ``lg.lg_pts`` is zero (degenerate league averages).
    Can return negative values for players scoring below replacement level.

    Examples:
        # Efficient scorer: 25 pts on 16 FGA, 4 FTA, 3 TOV
        offensive_win_shares(pts=25, fga=16, fta=4, tov=3, lg=lg)   # → ~0.18

        # Inefficient: 5 pts on 16 FGA, 2 FTA, 3 TOV
        offensive_win_shares(pts=5, fga=16, fta=2, tov=3, lg=lg)    # → ~ -0.42
    """
    if lg.lg_pts == 0:
        return None
    player_poss = 0.96 * (fga + tov + 0.44 * fta)
    marginal_offense = pts - 0.92 * lg.vop * player_poss
    marginal_pts_per_win = 0.32 * lg.lg_pts
    return marginal_offense / marginal_pts_per_win


def pythagorean_win_pct(
    pts: float,
    opp_pts: float,
    exp: float = 13.91,
) -> float | None:
    """Pythagorean win expectation — expected win% from point differential.

    win% = pts^exp / (pts^exp + opp_pts^exp)

    The default exponent (13.91) is Daryl Morey's basketball-specific
    correction; pass ``exp=2`` for the original Pythagorean formula or
    ``exp=16.5`` for the Kubatko et al. variant.

    Args:
        pts:     Points scored per game (or season total).
        opp_pts: Points allowed per game (or season total — same scale).
        exp:     Pythagorean exponent (default 13.91).

    Returns:
        Expected win probability in [0, 1], or None when inputs are
        zero/negative.
    """
    if pts < 0 or opp_pts < 0:
        return None
    pts_exp = fpow(pts, exp)
    opp_exp = fpow(opp_pts, exp)
    denominator = pts_exp + opp_exp
    if denominator == 0:
        return None
    return pts_exp / denominator


def bell_curve_win_pct(
    ppg: float,
    opp_ppg: float,
    std_net_pts: float,
) -> float | None:
    """Bell Curve method — win% from point differential using the normal CDF.

    Win% = Φ((PPG - OPP_PPG) / StDev(PPG - OPP_PPG))

    Introduced by Oliver (2004) as a more theoretically grounded alternative
    to the Pythagorean method.  Assumes team points scored and allowed are
    normally distributed, so their difference (net points) is also normal.

    Advantages over :func:`pythagorean_win_pct`:
    - No empirically tuned exponent — works across eras and leagues.
    - Incorporates game-to-game variance: a team that wins by exactly 5
      every game has a higher win% than one that alternates +20 and -10.

    Args:
        ppg:          Points per game (or total — same scale as *opp_ppg*).
        opp_ppg:      Opponent points per game (same scale as *ppg*).
        std_net_pts:  Standard deviation of net points (PPG - OPP_PPG) across
                      the team's games.  Requires individual game data.

    Returns:
        Expected win probability in [0, 1], or None when std_net_pts is
        non-positive (zero or negative — degenerate/invalid case).

    Note:
        Offensive and defensive *ratings* (per-100 possessions) can be
        substituted for PPG and OPP_PPG along with their corresponding
        standard deviation for a pace-neutral version.
    """
    if std_net_pts <= 0:
        return None
    z = (ppg - opp_ppg) / std_net_pts
    return 0.5 * (1.0 + erf(z / fsqrt(2.0)))


def defensive_win_shares(  # noqa: PLR0913
    stl: float,
    blk: float,
    dreb: float,
    mp: float,
    pf: float,
    team_mp: float,
    team_blk: float,
    team_stl: float,
    team_dreb: float,
    team_pf: float,
    opp_fga: float,
    opp_fgm: float,
    opp_fta: float,
    opp_ftm: float,
    opp_tov: float,
    opp_oreb: float,
    opp_pts: float,
    lg: LeagueAverages,
) -> float | None:
    """Defensive Win Shares — player's estimated contribution to team wins on defense.

    Implements the Basketball-Reference stops-based formula:

    1. Stops (player's estimated defensive stops) from steals, blocks, defensive
       rebounds, and a share of team-level stops via personal fouls.
    2. Stop% = player stops * team_mp / (opp_poss * mp)
    3. Individual defensive rating (PlayerDRtg) derived from team_drtg and Stop%.
    4. MarginalDefense = (mp / team_mp) * opp_poss * (1.08 * lg.vop - PlayerDRtg/100)
    5. DWS = MarginalDefense / (0.32 * lg_pts)

    team_drtg is computed internally from opponent stats (opp_pts / opp_poss * 100),
    so no pre-computed team rating is required.

    Returns None when:
    - mp == 0 (player did not play)
    - team_mp == 0 (degenerate or missing team minutes)
    - opp_poss == 0 (degenerate game with no opponent possessions)
    - opp_fgm + sc_poss_ft == 0 (cannot compute points per scoring possession)
    - lg.lg_pts == 0 (invalid league-average points; cannot normalise DWS)

    stop_pct is clamped to [0, 1] so that single-game inputs (where team_blk can
    exceed opp missed shots, or a short stint inflates the fraction above 1) do
    not invert the player_drtg formula and produce unrealistic values.

    Can return negative values for players whose individual defensive rating
    exceeds 1.08 * lg.vop * 100 (i.e., significantly below replacement-level
    defensive efficiency).

    Args:
        stl:       Player steals.
        blk:       Player blocks.
        dreb:      Player defensive rebounds.
        mp:        Player minutes played.
        pf:        Player personal fouls.
        team_mp:   Team total player-minutes (5 x 48 x games played).
        team_blk:  Team total blocks.
        team_stl:  Team total steals.
        team_dreb: Team total defensive rebounds.
        team_pf:   Team total personal fouls.
        opp_fga:   Opponent field goal attempts.
        opp_fgm:   Opponent field goals made.
        opp_fta:   Opponent free throw attempts.
        opp_ftm:   Opponent free throws made.
        opp_tov:   Opponent turnovers.
        opp_oreb:  Opponent offensive rebounds.
        opp_pts:   Opponent points scored.
        lg:        League-wide season averages.
    """
    if mp == 0 or team_mp == 0:
        return None

    opp_poss = possessions(opp_fga, opp_oreb, opp_tov, opp_fta)
    if opp_poss == 0:
        return None
    if lg.lg_pts == 0:
        return None

    # --- team-level defensive rates ---
    drb_pct = team_dreb / (team_dreb + opp_oreb) if (team_dreb + opp_oreb) > 0 else 0.0
    dfg_pct = opp_fgm / opp_fga if opp_fga > 0 else 0.0
    lg_fg_pct = lg.lg_fgm / lg.lg_fga  # lg_fga always > 0 (validated in __post_init__)

    # --- FMwt: weight for how much of a missed FG turns into a player stop ---
    fmwt_num = dfg_pct * (1 - drb_pct)
    fmwt_den = fmwt_num + lg_fg_pct * drb_pct
    fmwt = fmwt_num / fmwt_den if fmwt_den > 0 else 0.0

    # --- individual stops ---
    stop_factor = 1 - 1.07 * drb_pct
    stops1 = stl + blk * fmwt * stop_factor + dreb * (1 - fmwt)

    rate_a = ((opp_fga - opp_fgm - team_blk) / team_mp) * fmwt * stop_factor
    rate_b = (opp_tov - team_stl) / team_mp
    ft_pct = opp_ftm / opp_fta if opp_fta > 0 else 0.0
    pf_stops = (
        (pf / team_pf) * 0.4 * opp_fta * (1 - ft_pct) ** 2 if team_pf > 0 else 0.0
    )
    stops2 = (rate_a + rate_b) * mp + pf_stops

    # --- stop% and individual defensive rating ---
    # Clamp to [0, 1]: single-game inputs can push stop_pct out of range
    # (e.g. team_blk > opp_fga - opp_fgm makes rate_a negative; large stops1
    # relative to a short stint makes it > 1). Out-of-range values invert the
    # player_drtg formula and produce unrealistic DWS.
    stop_pct = (stops1 + stops2) * team_mp / (opp_poss * mp)
    stop_pct = max(0.0, min(1.0, stop_pct))

    sc_poss_ft = opp_fta * (1 - (1 - ft_pct) ** 2) * 0.4
    sc_poss_denom = opp_fgm + sc_poss_ft
    if sc_poss_denom == 0:
        return None
    d_pts_per_sc_poss = opp_pts / sc_poss_denom

    team_drtg = opp_pts / opp_poss * 100
    player_drtg = team_drtg + 0.2 * (
        100 * d_pts_per_sc_poss * (1 - stop_pct) - team_drtg
    )

    # --- marginal defense → DWS ---
    marg_def = (mp / team_mp) * opp_poss * (1.08 * lg.vop - player_drtg / 100)
    return marg_def / (0.32 * lg.lg_pts)


def win_shares(ows: float | None, dws: float | None) -> float | None:
    """Total Win Shares — sum of offensive and defensive contributions.

    WS = OWS + DWS

    Returns None when either component is unavailable, consistent with how
    net_rtg handles missing ORTG or DRTG inputs.

    Args:
        ows: Offensive Win Shares (from offensive_win_shares()).
        dws: Defensive Win Shares (from defensive_win_shares()).
    """
    if ows is None or dws is None:
        return None
    return ows + dws


def win_shares_per_48(
    ws: float | None, mp: float, *, game_minutes: float = 48
) -> float | None:
    """Win Shares per ``game_minutes`` minutes (WS/48 for NBA, WS/40 for WNBA).

    WS/game_minutes = WS * game_minutes / MP

    Calibrated so that league-average ≈ 0.100; elite players reach 0.200+.
    Useful for comparing players with different playing-time levels.

    The ``game_minutes`` default of 48 matches the NBA convention (WS/48).
    Use ``game_minutes=40`` for WNBA (WS/40).

    Returns None when ws is None or mp is zero.

    Args:
        ws: Total Win Shares (from win_shares()).
        mp: Minutes played (same time window as ws).
        game_minutes: Regulation game length in minutes
            (default: 48 for NBA, use 40 for WNBA).
    """
    if ws is None or mp == 0:
        return None
    return ws * game_minutes / mp


def rolling_avg(
    values: Sequence[float | None],
    window: int,
) -> list[float | None]:
    """Sliding-window average over a sequence of per-game stat values.

    Positions before the first full window (warm-up period) return ``None``.
    Any ``None`` within a window propagates ``None`` to that output position.

    Args:
        values: Per-game stat values in chronological order.
                Pass ``None`` for games where the stat is unavailable.
        window: Number of consecutive games in each window (>= 1).

    Returns:
        List of the same length as *values*.  Each position holds the mean
        of the corresponding window, or ``None`` if the window is incomplete
        or contains a ``None``.

    Raises:
        ValueError: When *window* is less than 1.

    Examples:
        pts = [22.0, 18.0, 30.0, 25.0, 20.0]
        rolling_avg(pts, window=3)
        # [None, None, 23.33, 24.33, 25.0]
    """
    if window < 1:
        msg = f"window must be >= 1, got {window}"
        raise ValueError(msg)

    result: list[float | None] = []
    window_sum = 0.0
    none_count = 0
    for i, val in enumerate(values):
        if val is None:
            none_count += 1
        else:
            window_sum += val
        if i >= window:
            old = values[i - window]
            if old is None:
                none_count -= 1
            else:
                window_sum -= old
        if i + 1 < window or none_count > 0:
            result.append(None)
        else:
            result.append(window_sum / window)
    return result


def ewma(
    values: Sequence[float | None],
    span: int,
) -> list[float | None]:
    """Exponentially weighted moving average over a sequence of per-game values.

    Uses the pandas-compatible smoothing factor ``alpha = 2 / (span + 1)``.  The
    first valid (non-``None``) observation initialises the running average.
    ``None`` entries (DNP / missing games) produce ``None`` in the output but
    do **not** reset the running state — the EWA resumes from its last value
    when the next valid observation arrives.

    Args:
        values: Per-game stat values in chronological order (oldest first).
                Pass ``None`` for games where the stat is unavailable (DNP).
        span: Effective window size (>= 1).  Larger values produce a
                smoother, slower-reacting average.  Uses the same recursive
                update as ``pandas.Series(values).ewm(span=span, adjust=False,
                ignore_na=True).mean()``, but preserves ``None`` entries in
                the output list.

    Returns:
        List of the same length as *values*.  Each position holds the EWA
        up to and including that game, or ``None`` before the first valid
        observation or when the game was a DNP.

    Raises:
        ValueError: When *span* is less than 1.

    Examples:
        pts = [22.0, 18.0, 30.0, 25.0, 20.0]
        ewma(pts, span=3)
        # [22.0, 20.0, 25.0, 25.0, 22.5]
    """
    if span < 1:
        msg = f"span must be >= 1, got {span}"
        raise ValueError(msg)

    alpha = 2.0 / (span + 1)
    one_minus_alpha = 1.0 - alpha
    result: list[float | None] = []
    s: float | None = None  # running EWA; None until first valid observation

    for val in values:
        if val is None:
            result.append(None)
            continue
        s = val if s is None else alpha * val + one_minus_alpha * s
        result.append(s)

    return result


# ---------------------------------------------------------------------------
# Distribution statistics: floor, ceiling, median, prop hit rate
# ---------------------------------------------------------------------------


def _percentile(sorted_values: list[float], p: float) -> float:
    """Linear-interpolation percentile on a pre-sorted list.

    Args:
        sorted_values: Non-empty list already sorted ascending.
        p: Percentile in [0.0, 100.0].

    Returns:
        Linearly interpolated value at the *p*-th percentile.
    """
    n = len(sorted_values)
    if n == 1:
        return sorted_values[0]
    idx = (p / 100.0) * (n - 1)
    lo = int(idx)
    hi = min(lo + 1, n - 1)
    return sorted_values[lo] + (idx - lo) * (sorted_values[hi] - sorted_values[lo])


def stat_floor(
    values: Sequence[float | None],
    percentile: float = 10.0,
) -> float | None:
    """Nth percentile of a stat sample — downside / floor estimate.

    Uses linear interpolation (same as NumPy's default).  ``None`` values
    (e.g., DNP games) are excluded from the sample so they don't suppress an
    otherwise computable result.

    Args:
        values: Per-game stat values; pass ``None`` for games where the player
                did not participate.
        percentile: Percentile in [0.0, 100.0].  Defaults to 10 — the low-end
                    floor used in player projection systems.

    Returns:
        The Nth percentile as a float, or ``None`` if *values* contains no
        non-``None`` entries.

    Raises:
        ValueError: When *percentile* is outside [0.0, 100.0].

    Examples:
        pts = [22.0, 18.0, None, 30.0, 25.0, 20.0]
        stat_floor(pts)          # 10th pct ≈ 18.4 (DNP game excluded)
        stat_floor(pts, 25.0)    # 25th pct
    """
    if not (0.0 <= percentile <= 100.0):  # noqa: PLR2004
        msg = f"percentile must be in [0.0, 100.0], got {percentile}"
        raise ValueError(msg)
    valid = sorted(v for v in values if v is not None)
    if not valid:
        return None
    return _percentile(valid, percentile)


def stat_ceiling(
    values: Sequence[float | None],
    percentile: float = 90.0,
) -> float | None:
    """Nth percentile of a stat sample — upside / ceiling estimate.

    Uses linear interpolation (same as NumPy's default).  ``None`` values
    are excluded from the sample.

    Args:
        values: Per-game stat values; pass ``None`` for DNP games.
        percentile: Percentile in [0.0, 100.0].  Defaults to 90 — the
                    high-end ceiling used in player projection systems.

    Returns:
        The Nth percentile as a float, or ``None`` if *values* contains no
        non-``None`` entries.

    Raises:
        ValueError: When *percentile* is outside [0.0, 100.0].

    Examples:
        pts = [22.0, 18.0, None, 30.0, 25.0, 20.0]
        stat_ceiling(pts)          # 90th pct ≈ 29.6 (DNP game excluded)
        stat_ceiling(pts, 75.0)    # 75th pct
    """
    if not (0.0 <= percentile <= 100.0):  # noqa: PLR2004
        msg = f"percentile must be in [0.0, 100.0], got {percentile}"
        raise ValueError(msg)
    valid = sorted(v for v in values if v is not None)
    if not valid:
        return None
    return _percentile(valid, percentile)


def stat_median(values: Sequence[float | None]) -> float | None:
    """Median of a stat sample — central tendency estimate.

    Equivalent to ``stat_floor(values, 50.0)`` or ``stat_ceiling(values, 50.0)``.
    ``None`` values (DNP games) are excluded from the sample.

    Args:
        values: Per-game stat values; pass ``None`` for DNP games.

    Returns:
        50th percentile as a float, or ``None`` if *values* contains no
        non-``None`` entries.

    Examples:
        pts = [22.0, 18.0, None, 30.0, 25.0, 20.0]
        stat_median(pts)    # 22.0 (median of [18, 20, 22, 25, 30])
    """
    valid = sorted(v for v in values if v is not None)
    if not valid:
        return None
    return _percentile(valid, 50.0)


def prop_hit_rate(
    values: Sequence[float | None],
    line: float,
) -> float | None:
    """Fraction of games where a stat value meets or exceeds a threshold.

    Uses ``>=`` semantics: a value exactly equal to *line* counts as a hit.
    ``None`` values (DNP games) are excluded from both numerator and denominator
    so that missed games don't dilute the rate.

    Args:
        values: Per-game stat values; pass ``None`` for DNP games.
        line:   The threshold to compare against (e.g., a prop bet line of 24.5).

    Returns:
        Fraction of valid games in [0.0, 1.0] where the stat met *line*,
        or ``None`` if *values* contains no non-``None`` entries.

    Examples:
        pts = [22.0, 25.0, 18.0, 30.0, 25.0]
        prop_hit_rate(pts, 24.5)    # 3/5 = 0.60
        prop_hit_rate(pts, 25.0)    # 3/5 = 0.60  (>= 25 counts)
    """
    valid = [v for v in values if v is not None]
    if not valid:
        return None
    hits = sum(1 for v in valid if v >= line)
    return hits / len(valid)


def percentile_rank(value: float, reference: Sequence[float | None]) -> float | None:
    """Position of *value* within a reference distribution as a percentile.

    Inverse of :func:`stat_floor`: if ``stat_floor(values, p)`` returns *v*, then
    ``percentile_rank(v, values)`` returns approximately *p* (exact for unique-value
    lists; interpolates for duplicates).

    ``None`` values (DNP games) in *reference* are skipped before computing the rank.
    Values outside the reference range are clamped to ``[0.0, 100.0]``.

    Args:
        value:     The query value to rank.
        reference: The distribution to rank against; ``None`` entries are excluded.

    Returns:
        Percentile rank in ``[0.0, 100.0]``, or ``None`` if *reference* contains no
        non-``None`` entries.

    Examples:
        >>> percentile_rank(20.0, [10.0, 20.0, 30.0])   # 50.0
        >>> percentile_rank(35.0, [10.0, 20.0, 30.0])   # 100.0 (above max → clamped)
    """
    valid = sorted(v for v in reference if v is not None)
    if not valid:
        return None
    n = len(valid)
    # Single-element list: below → 0.0, equal or above → 100.0
    if n == 1:
        return 100.0 if value >= valid[0] else 0.0
    if value <= valid[0]:
        return 0.0
    if value >= valid[-1]:
        return 100.0
    # Find the bracketing interval via binary search and interpolate
    lo = bisect.bisect_right(valid, value) - 1
    hi = lo + 1
    span = valid[hi] - valid[lo]
    frac = 0.0 if span == 0.0 else (value - valid[lo]) / span
    idx = lo + frac
    return idx / (n - 1) * 100.0


def stat_consistency(values: Sequence[float | None]) -> float | None:
    """Population standard deviation of a sequence of per-game stats.

    Measures how much a player's output varies from game to game.  A lower value
    indicates a more consistent player.  ``None`` values (DNP games) are excluded
    from the calculation.

    Uses the *population* standard deviation (divided by *n*, not *n - 1*) because
    the game log represents the full sample being analysed, not a statistical sample.

    Args:
        values: Per-game stat values; pass ``None`` for DNP games.

    Returns:
        Population standard deviation (≥ 0.0), or ``None`` if *values* contains no
        non-``None`` entries.  A single valid entry returns ``0.0``.

    Examples:
        pts = [20.0, 25.0, 18.0, 30.0, 22.0]
        stat_consistency(pts)         # ≈ 4.07  (moderate variance)
        stat_consistency([20.0] * 5)  # 0.0     (perfectly consistent)
    """
    valid = [v for v in values if v is not None]
    if not valid:
        return None
    n = len(valid)
    mean = sum(valid) / n
    variance = sum((v - mean) ** 2 for v in valid) / n
    return fsqrt(variance)


def streak_count(values: Sequence[float | None], line: float) -> int:
    """Number of consecutive recent games where a stat met or exceeded *line*.

    Counts backwards from the most recent game, stopping at the first game that
    falls below the line.  ``None`` values (DNP games) are skipped — a DNP does
    not break an active streak.

    Uses ``>=`` semantics: a value exactly equal to *line* counts as a hit.

    Args:
        values: Per-game stat values in chronological order (oldest first);
                pass ``None`` for DNP games.
        line:   The threshold the stat must meet (e.g., a prop bet line of 24.5).

    Returns:
        Length of the current streak (≥ 0).  Returns ``0`` if the most recent
        non-``None`` game missed the line, or if there are no non-``None`` games.

    Examples:
        pts = [10.0, 25.0, 30.0, 28.0]
        streak_count(pts, 20.0)                       # 3  (last three ≥ 20)
        streak_count([20.0, 25.0, None, 30.0], 20.0)  # 3  (DNP skipped)
    """
    count = 0
    for v in reversed(values):
        if v is None:
            continue
        if v >= line:
            count += 1
        else:
            break
    return count


def rolling_consistency(
    values: Sequence[float | None],
    window: int,
) -> list[float | None]:
    """Sliding-window population standard deviation over per-game stat values.

    Measures game-to-game variance across a rolling window. Higher values mean
    wilder swings; lower means tighter, more predictable output.

    Mirrors :func:`rolling_avg` semantics: positions before the first full
    window return ``None``, and any ``None`` within a window propagates ``None``
    to that output position. If a game is missing, the variance for that window
    is unknown — not zero.

    Args:
        values: Per-game stat values in chronological order.
                Pass ``None`` for games where the stat is unavailable.
        window: Number of consecutive games in each window (>= 1).

    Returns:
        List of the same length as *values*.  Each position holds the
        population std dev of the corresponding window, or ``None`` if the
        window is incomplete or contains a ``None``.

    Raises:
        ValueError: When *window* is less than 1.

    Examples:
        pts = [22.0, 18.0, 30.0, 25.0, 20.0]
        rolling_consistency(pts, window=3)
        # [None, None, ≈4.99, ≈4.92, ≈4.08]
    """
    if window < 1:
        msg = f"window must be >= 1, got {window}"
        raise ValueError(msg)

    result: list[float | None] = []
    for i in range(len(values)):
        if i + 1 < window:
            result.append(None)
            continue
        # Two-pass computation: compute the mean first, then sum squared
        # deviations. Avoids the catastrophic cancellation of the single-pass
        # formula (E[X²] - (E[X])²) for large values.
        has_none = False
        floats: list[float] = []
        for j in range(i - window + 1, i + 1):
            v = values[j]
            if v is None:
                has_none = True
                break
            floats.append(v)
        if has_none:
            result.append(None)
            continue
        mean = sum(floats) / len(floats)
        variance = sum((v - mean) ** 2 for v in floats) / len(floats)
        result.append(fsqrt(variance))
    return result


def expected_stat(values: Sequence[float | None]) -> float | None:
    """PERT-weighted projection combining the floor, median, and ceiling.

    Applies the Program Evaluation and Review Technique (PERT) formula to
    produce a single-number projection that down-weights extreme outcomes:

    .. code-block::

        expected = (floor + 4 * median + ceiling) / 6

    where floor is the 10th percentile, median is the 50th, and ceiling is
    the 90th.  The median gets 4x the weight of either extreme, so a one-off
    blowup game won't move the projection as much as a straight average would.

    ``None`` values (DNP games) are excluded before computing the projection.

    Args:
        values: Per-game stat values; pass ``None`` for DNP games.

    Returns:
        PERT-weighted projection in ``[stat_floor(values), stat_ceiling(values)]``,
        or ``None`` if *values* contains no non-``None`` entries.

    Examples:
        pts = [38.0, 14.0, 41.0, 22.0, 35.0, 29.0, 44.0, 18.0]
        expected_stat(pts)  # weighted projection accounting for boom/bust range
    """
    # Filter and sort once; derive P10/P50/P90 via the shared helper to avoid
    # the O(3n log n) cost of calling stat_floor/stat_median/stat_ceiling separately.
    valid = sorted(v for v in values if v is not None)
    if not valid:
        return None
    floor_v = _percentile(valid, 10.0)
    median_v = _percentile(valid, 50.0)
    ceil_v = _percentile(valid, 90.0)
    return (floor_v + 4.0 * median_v + ceil_v) / 6.0


def hit_rate_last_n(
    values: Sequence[float | None],
    line: float,
    n: int,
) -> float | None:
    """Prop hit rate restricted to the last *n* non-DNP games.

    Equivalent to calling :func:`prop_hit_rate` on a slice of only the most
    recent *n* games played (``None`` entries are skipped when counting).
    Use this to gauge a player's *current form* rather than their full-season
    rate. Small *n* tracks recent games closely but is noisy; large *n* is
    more stable. Pick based on how much you trust recency.

    Uses ``>=`` semantics: a value exactly equal to *line* counts as a hit.

    Args:
        values: Per-game stat values in chronological order (oldest first);
                pass ``None`` for DNP games.
        line:   The threshold the stat must meet.
        n:      Number of most-recent non-DNP games to consider (>= 1).

    Returns:
        Fraction of the last *n* valid games in [0.0, 1.0] where the stat met
        *line*, or ``None`` if there are no non-``None`` entries.  If fewer
        than *n* games have been played, all available games are used.

    Raises:
        ValueError: When *n* is less than 1.

    Examples:
        pts = [10.0, 25.0, 30.0, 15.0, 28.0]
        hit_rate_last_n(pts, 20.0, n=3)   # 2/3 ≈ 0.667  (28, 15, 30)
        hit_rate_last_n(pts, 20.0, n=10)  # same as prop_hit_rate(pts, 20.0)
    """
    if n < 1:
        msg = f"n must be >= 1, got {n}"
        raise ValueError(msg)
    # Collect the last n non-None values, walking backwards from most recent
    recent: list[float] = []
    for v in reversed(values):
        if v is None:
            continue
        recent.append(v)
        if len(recent) == n:
            break
    if not recent:
        return None
    return sum(1 for v in recent if v >= line) / len(recent)
