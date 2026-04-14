"""Game finder utilities for the NBA Stats API.

Search for games by team or player with rich filtering (opponent, date range,
outcome, location, stat thresholds) and analyze results with pure helpers.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import groupby
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastbreak.clients.base import BaseClient
    from fastbreak.models.league_game_finder import GameFinderResult
    from fastbreak.types import Date, Location, Outcome, Season, SeasonType


# ---------------------------------------------------------------------------
# Return types
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class GameAverages:
    """Averaged stats across a set of games."""

    pts: float
    reb: float
    ast: float
    stl: float
    blk: float
    tov: float
    fg_pct: float | None
    fg3_pct: float | None
    ft_pct: float | None
    plus_minus: float | None

    def __post_init__(self) -> None:
        for field in ("pts", "reb", "ast", "stl", "blk", "tov"):
            if getattr(self, field) < 0:
                msg = f"{field} must be non-negative, got {getattr(self, field)}"
                raise ValueError(msg)
        for field in ("fg_pct", "fg3_pct", "ft_pct"):
            val = getattr(self, field)
            if val is not None and not 0.0 <= val <= 1.0:
                msg = f"{field} must be in [0, 1], got {val}"
                raise ValueError(msg)


@dataclass(frozen=True, slots=True)
class Record:
    """Win-loss record summary."""

    wins: int
    losses: int
    win_pct: float

    def __post_init__(self) -> None:
        if self.wins < 0:
            msg = f"wins must be non-negative, got {self.wins}"
            raise ValueError(msg)
        if self.losses < 0:
            msg = f"losses must be non-negative, got {self.losses}"
            raise ValueError(msg)
        if not 0.0 <= self.win_pct <= 1.0:
            msg = f"win_pct must be in [0, 1], got {self.win_pct}"
            raise ValueError(msg)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _str_or_none(value: int | None) -> str | None:
    return str(value) if value is not None else None


_LOCATION_MATCHUP: dict[Location, str] = {"Home": "vs.", "Road": "@"}


def _filter_location(
    games: list[GameFinderResult],
    location: Location | None,
) -> list[GameFinderResult]:
    """Filter games by location using the matchup string.

    The ``Location`` API parameter is non-functional on the
    ``leaguegamefinder`` endpoint, so we filter client-side instead.
    ``"Home"`` games contain ``"vs."`` in the matchup; ``"Road"`` games
    contain ``"@"``.  Games with a ``None`` matchup are excluded.
    """
    if location is None:
        return games
    token = _LOCATION_MATCHUP[location]
    return [g for g in games if g.matchup and token in g.matchup]


def _avg_optional(values: list[float | None]) -> float | None:
    """Average non-None values; return None if all are None."""
    valid = [v for v in values if v is not None]
    if not valid:
        return None
    return sum(valid) / len(valid)


# ---------------------------------------------------------------------------
# Async search functions
# ---------------------------------------------------------------------------


async def find_team_games(  # noqa: PLR0913
    client: BaseClient,
    team_id: int,
    *,
    vs_team_id: int | None = None,
    season: Season | None = None,
    season_type: SeasonType | None = None,
    date_from: Date | None = None,
    date_to: Date | None = None,
    outcome: Outcome | None = None,
    location: Location | None = None,
    gt_pts: int | None = None,
    gt_reb: int | None = None,
    gt_ast: int | None = None,
    gt_stl: int | None = None,
    gt_blk: int | None = None,
) -> list[GameFinderResult]:
    """Find games for a team matching the given filters.

    Args:
        client: NBA API client.
        team_id: Team ID to search for.
        vs_team_id: Filter by opponent team ID.
        season: Season in YYYY-YY format (e.g., "2025-26").
        season_type: "Regular Season", "Playoffs", etc.
        date_from: Start date in MM/DD/YYYY format.
        date_to: End date in MM/DD/YYYY format.
        outcome: Filter by game outcome ("W" or "L").
        location: Filter by game location ("Home" or "Road").
            Applied client-side via the ``matchup`` field because the
            ``Location`` API parameter is non-functional on ``leaguegamefinder``.
        gt_pts: Minimum points threshold.
        gt_reb: Minimum rebounds threshold.
        gt_ast: Minimum assists threshold.
        gt_stl: Minimum steals threshold.
        gt_blk: Minimum blocks threshold.

    Returns:
        List of ``GameFinderResult`` matching the criteria.

    Examples:
        games = await find_team_games(client, team_id=1610612738, season="2025-26", outcome="W")

    """
    from fastbreak.endpoints import LeagueGameFinder  # noqa: PLC0415

    endpoint = LeagueGameFinder(
        league_id=client.league_id,
        player_or_team="T",
        team_id=str(team_id),
        vs_team_id=_str_or_none(vs_team_id),
        season=season,
        season_type=season_type,
        date_from=date_from,
        date_to=date_to,
        outcome=outcome,
        gt_pts=_str_or_none(gt_pts),
        gt_reb=_str_or_none(gt_reb),
        gt_ast=_str_or_none(gt_ast),
        gt_stl=_str_or_none(gt_stl),
        gt_blk=_str_or_none(gt_blk),
    )
    response = await client.get(endpoint)
    return _filter_location(response.games, location)


async def find_player_games(  # noqa: PLR0913
    client: BaseClient,
    player_id: int,
    *,
    team_id: int | None = None,
    vs_team_id: int | None = None,
    season: Season | None = None,
    season_type: SeasonType | None = None,
    date_from: Date | None = None,
    date_to: Date | None = None,
    outcome: Outcome | None = None,
    location: Location | None = None,
    gt_pts: int | None = None,
    gt_reb: int | None = None,
    gt_ast: int | None = None,
    gt_stl: int | None = None,
    gt_blk: int | None = None,
) -> list[GameFinderResult]:
    """Find games for a player matching the given filters.

    Args:
        client: NBA API client.
        player_id: Player ID to search for.
        team_id: Filter by team ID.
        vs_team_id: Filter by opponent team ID.
        season: Season in YYYY-YY format (e.g., "2025-26").
        season_type: "Regular Season", "Playoffs", etc.
        date_from: Start date in MM/DD/YYYY format.
        date_to: End date in MM/DD/YYYY format.
        outcome: Filter by game outcome ("W" or "L").
        location: Filter by game location ("Home" or "Road").
            Applied client-side via the ``matchup`` field because the
            ``Location`` API parameter is non-functional on ``leaguegamefinder``.
        gt_pts: Minimum points threshold.
        gt_reb: Minimum rebounds threshold.
        gt_ast: Minimum assists threshold.
        gt_stl: Minimum steals threshold.
        gt_blk: Minimum blocks threshold.

    Returns:
        List of ``GameFinderResult`` matching the criteria.

    Examples:
        games = await find_player_games(client, player_id=201939, gt_pts=30)

    """
    from fastbreak.endpoints import LeagueGameFinder  # noqa: PLC0415

    endpoint = LeagueGameFinder(
        league_id=client.league_id,
        player_or_team="P",
        player_id=str(player_id),
        team_id=_str_or_none(team_id),
        vs_team_id=_str_or_none(vs_team_id),
        season=season,
        season_type=season_type,
        date_from=date_from,
        date_to=date_to,
        outcome=outcome,
        gt_pts=_str_or_none(gt_pts),
        gt_reb=_str_or_none(gt_reb),
        gt_ast=_str_or_none(gt_ast),
        gt_stl=_str_or_none(gt_stl),
        gt_blk=_str_or_none(gt_blk),
    )
    response = await client.get(endpoint)
    return _filter_location(response.games, location)


# ---------------------------------------------------------------------------
# Pure computation helpers
# ---------------------------------------------------------------------------


def aggregate_games(games: list[GameFinderResult]) -> GameAverages:
    """Compute average stats across a list of games.

    Counting stats (pts, reb, ast, stl, blk, tov) are always averaged.
    Percentage fields and plus_minus are averaged from non-None values only;
    if all values are None the result is None.

    Args:
        games: List of ``GameFinderResult`` to aggregate.

    Returns:
        ``GameAverages`` frozen dataclass with averaged stats.

    """
    if not games:
        return GameAverages(
            pts=0.0,
            reb=0.0,
            ast=0.0,
            stl=0.0,
            blk=0.0,
            tov=0.0,
            fg_pct=None,
            fg3_pct=None,
            ft_pct=None,
            plus_minus=None,
        )

    n = len(games)
    return GameAverages(
        pts=sum(g.pts for g in games) / n,
        reb=sum(g.reb for g in games) / n,
        ast=sum(g.ast for g in games) / n,
        stl=sum(g.stl for g in games) / n,
        blk=sum(g.blk for g in games) / n,
        tov=sum(g.tov for g in games) / n,
        fg_pct=_avg_optional([g.fg_pct for g in games]),
        fg3_pct=_avg_optional([g.fg3_pct for g in games]),
        ft_pct=_avg_optional([g.ft_pct for g in games]),
        plus_minus=_avg_optional([g.plus_minus for g in games]),
    )


def streak_games(
    games: list[GameFinderResult],
) -> list[list[GameFinderResult]]:
    """Group consecutive games into win/loss streaks.

    Games with ``wl=None`` are excluded and break the current streak.

    Args:
        games: List of ``GameFinderResult`` in chronological order.

    Returns:
        List of streaks, where each streak is a list of consecutive games
        with the same ``wl`` value. Adjacent streaks have different ``wl``
        values when the input contains no ``None`` ``wl`` games; ``None``
        values break the current streak and may produce adjacent streaks
        with the same ``wl``.

    """
    streaks: list[list[GameFinderResult]] = []
    for key, group in groupby(games, key=lambda g: g.wl):
        if key is not None:
            streaks.append(list(group))
    return streaks


def summarize_record(games: list[GameFinderResult]) -> Record:
    """Compute win-loss record from a list of games.

    Games with ``wl=None`` are excluded from the count.

    Args:
        games: List of ``GameFinderResult``.

    Returns:
        ``Record`` frozen dataclass with wins, losses, and win_pct.

    """
    wins = sum(1 for g in games if g.wl == "W")
    losses = sum(1 for g in games if g.wl == "L")
    total = wins + losses
    return Record(
        wins=wins,
        losses=losses,
        win_pct=wins / total if total > 0 else 0.0,
    )
