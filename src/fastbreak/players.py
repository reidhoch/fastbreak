"""Player lookup utilities for the NBA Stats API."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastbreak.logging import logger
from fastbreak.seasons import get_season_from_date

if TYPE_CHECKING:
    from fastbreak.clients.nba import NBAClient
    from fastbreak.models import PlayerIndexEntry
    from fastbreak.models.league_hustle_stats_player import LeagueHustlePlayer
    from fastbreak.models.league_leaders import LeagueLeader
    from fastbreak.models.league_player_on_details import PlayerOnCourtDetail
    from fastbreak.models.player_career_stats import PlayerCareerStatsResponse
    from fastbreak.models.player_game_log import PlayerGameLogEntry
    from fastbreak.models.synergy_playtypes import PlayerSynergyPlaytype
    from fastbreak.types import PerMode, Season, SeasonType, StatCategoryAbbreviation


async def search_players(
    client: NBAClient,
    query: str,
    *,
    season: Season | None = None,
    limit: int = 10,
) -> list[PlayerIndexEntry]:
    """Search for players by partial name match.

    Args:
        client: NBA API client
        query: Search string (matches first name, last name, or full name)
        season: Season to search in (defaults to current)
        limit: Maximum results to return

    Returns:
        List of matching PlayerIndexEntry objects, sorted by relevance tier,
        then alphabetically by last name within each tier

    Raises:
        ValueError: If limit is less than 1.

    Examples:
        await search_players(client, "Curry")  # finds Stephen Curry, etc.
        await search_players(client, "Ant")    # finds Anthony Edwards, etc.

    """
    if limit < 1:
        msg = f"limit must be a positive integer, got {limit}"
        raise ValueError(msg)
    if not query or not query.strip():
        return []

    from fastbreak.endpoints import PlayerIndex  # noqa: PLC0415

    season = season or get_season_from_date()
    response = await client.get(PlayerIndex(season=season))

    q = query.lower().strip()
    matches: list[tuple[int, PlayerIndexEntry]] = []

    for player in response.players:
        first = player.player_first_name.lower()
        last = player.player_last_name.lower()
        full = f"{first} {last}"

        if full == q:
            priority = 0
        elif last.startswith(q):
            priority = 1
        elif first.startswith(q):
            priority = 2
        elif q in first or q in last or q in full:
            priority = 3
        else:
            continue

        matches.append((priority, player))

    matches.sort(key=lambda x: (x[0], x[1].player_last_name.lower()))
    return [player for _, player in matches[:limit]]


async def get_player(
    client: NBAClient,
    identifier: int | str,
    *,
    season: Season | None = None,
) -> PlayerIndexEntry | None:
    """Get a player by ID or exact name.

    Args:
        client: NBA API client
        identifier: Player ID (int) or exact full name (str)
        season: Season to search in (defaults to current)

    Returns:
        PlayerIndexEntry if found, None otherwise

    Examples:
        await get_player(client, 201939)           # by ID
        await get_player(client, "Stephen Curry")  # exact name match

    """
    if isinstance(identifier, int):
        from fastbreak.endpoints import PlayerIndex  # noqa: PLC0415

        season = season or get_season_from_date()
        response = await client.get(PlayerIndex(season=season))
        for player in response.players:
            if player.person_id == identifier:
                return player
        # Integer ID miss is unexpected in normal usage (stale ID?) — log at WARNING
        logger.warning("player_not_found", identifier=identifier, season=season)
        return None

    results = await search_players(client, identifier, season=season, limit=1)
    if results:
        full = f"{results[0].player_first_name} {results[0].player_last_name}"
        if full.lower() == identifier.lower().strip():
            return results[0]
    # String name miss is expected (typo, partial name) — log at DEBUG to avoid noise
    logger.debug("player_not_found", identifier=identifier, season=season)
    return None


async def get_player_id(
    client: NBAClient,
    name: str,
    *,
    season: Season | None = None,
) -> int | None:
    """Get a player's ID by exact name.

    Args:
        client: NBA API client
        name: Exact full name of the player
        season: Season to search in (defaults to current)

    Returns:
        Player ID if found, None otherwise

    Examples:
        player_id = await get_player_id(client, "LeBron James")

    """
    player = await get_player(client, name, season=season)
    return player.person_id if player else None


async def get_player_game_log(
    client: NBAClient,
    *,
    player_id: int,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
) -> list[PlayerGameLogEntry]:
    """Return a player's game-by-game stats for a season.

    Args:
        client: NBA API client
        player_id: NBA player ID
        season: Season in YYYY-YY format (defaults to current)
        season_type: "Regular Season", "Playoffs", etc.

    Returns:
        List of PlayerGameLogEntry objects, one per game played

    Examples:
        log = await get_player_game_log(client, player_id=201939)

    """
    from fastbreak.endpoints import PlayerGameLog  # noqa: PLC0415

    season = season or get_season_from_date()
    response = await client.get(
        PlayerGameLog(player_id=player_id, season=season, season_type=season_type)
    )
    return response.games


async def get_player_stats(
    client: NBAClient,
    player_id: int,
    *,
    per_mode: PerMode = "PerGame",
) -> PlayerCareerStatsResponse:
    """Return career statistics for a player.

    Args:
        client: NBA API client
        player_id: NBA player ID
        per_mode: Stat aggregation mode ("PerGame", "Totals", "Per36", etc.)

    Returns:
        PlayerCareerStatsResponse with season-by-season and career totals

    Examples:
        stats = await get_player_stats(client, player_id=201939)
        current = stats.season_totals_regular_season[-1]

    """
    from fastbreak.endpoints import PlayerCareerStats  # noqa: PLC0415

    return await client.get(PlayerCareerStats(player_id=player_id, per_mode=per_mode))


async def get_league_leaders(
    client: NBAClient,
    *,
    season: Season | None = None,
    stat_category: StatCategoryAbbreviation = "PTS",
    season_type: SeasonType = "Regular Season",
    limit: int | None = None,
) -> list[LeagueLeader]:
    """Return ranked league leaders for a statistical category.

    Args:
        client: NBA API client
        season: Season in YYYY-YY format (defaults to current)
        stat_category: Stat to rank by ("PTS", "REB", "AST", "STL", "BLK", etc.)
        season_type: "Regular Season", "Playoffs", etc.
        limit: Maximum results to return (None = all)

    Returns:
        List of LeagueLeader objects ranked by stat_category

    Raises:
        ValueError: If limit is less than 1.

    Examples:
        scorers = await get_league_leaders(client, stat_category="PTS", limit=10)
        assisters = await get_league_leaders(client, stat_category="AST", limit=5)

    """
    if limit is not None and limit < 1:
        msg = f"limit must be a positive integer, got {limit}"
        raise ValueError(msg)

    from fastbreak.endpoints import LeagueLeaders  # noqa: PLC0415

    season = season or get_season_from_date()
    response = await client.get(
        LeagueLeaders(
            season=season,
            stat_category=stat_category,
            season_type=season_type,
        )
    )
    leaders = response.leaders
    return leaders if limit is None else leaders[:limit]


async def get_hustle_stats(
    client: NBAClient,
    player_id: int,
    *,
    season: Season | None = None,
    season_type: SeasonType = "Regular Season",
) -> LeagueHustlePlayer | None:
    """Return season hustle statistics for a player.

    Fetches league-wide hustle stats and returns the entry for the given player.
    Hustle stats include contested shots, deflections, screen assists,
    charges drawn, loose balls recovered, and box outs.

    Args:
        client: NBA API client
        player_id: NBA player ID
        season: Season in YYYY-YY format (defaults to current)
        season_type: "Regular Season", "Playoffs", etc.

    Returns:
        LeagueHustlePlayer if found, None otherwise

    Examples:
        hustle = await get_hustle_stats(client, player_id=201939)
        if hustle:
            print(hustle.deflections, hustle.screen_assists)

    """
    from fastbreak.endpoints import LeagueHustleStatsPlayer  # noqa: PLC0415

    season = season or get_season_from_date()
    response = await client.get(
        LeagueHustleStatsPlayer(season=season, season_type=season_type)
    )
    for player in response.players:
        if player.player_id == player_id:
            return player
    logger.warning(
        "hustle_stats_not_found",
        player_id=player_id,
        season=season,
        total_players_in_response=len(response.players),
    )
    return None


def _season_id_to_season(season_id: str) -> str:
    """Convert NBA season_id string to YYYY-YY format.

    Handles two API formats:
    - "22024" (type digit + 4-digit year) -> "2024-25"
    - "2020-21" (already YYYY-YY)         -> "2020-21"
    """
    if "-" in season_id:
        return season_id
    if len(season_id) < 2:  # noqa: PLR2004
        msg = f"Cannot parse season_id {season_id!r}: expected 'T+YYYY' format (e.g., '22024')"
        raise ValueError(msg)
    raw = season_id[1:]
    try:
        year = int(raw)
    except ValueError as exc:
        msg = (
            f"Cannot parse season_id {season_id!r}: year portion {raw!r} is not numeric"
        )
        raise ValueError(msg) from exc
    return f"{year}-{str(year + 1)[2:]}"


async def get_career_game_logs(
    client: NBAClient,
    player_id: int,
    *,
    season_type: SeasonType = "Regular Season",
) -> list[PlayerGameLogEntry]:
    """Return game log entries for every season of a player's career.

    Fetches PlayerCareerStats to discover all seasons played, then calls
    get_player_game_log for each season concurrently.

    Args:
        client: NBA API client
        player_id: NBA player ID
        season_type: "Regular Season" or "Playoffs"

    Returns:
        Flat list of PlayerGameLogEntry objects across all seasons, in the order
        returned by get_player_game_log (typically reverse chronological
        within each season), seasons in the order returned by career stats.

    Examples:
        entries = await get_career_game_logs(client, player_id=2544)
        print(f"{len(entries)} games in career")
    """
    from fastbreak.endpoints import PlayerCareerStats, PlayerGameLog  # noqa: PLC0415

    career = await client.get(PlayerCareerStats(player_id=player_id))
    seasons = (
        career.season_totals_regular_season
        if season_type == "Regular Season"
        else career.season_totals_post_season
    )
    if not seasons:
        return []

    season_strings = [_season_id_to_season(s.season_id) for s in seasons]

    endpoints = [
        PlayerGameLog(player_id=player_id, season=s, season_type=season_type)
        for s in season_strings
    ]
    responses = await client.get_many(endpoints)
    return [game for resp in responses for game in resp.games]


async def get_on_off_splits(  # noqa: PLR0913
    client: NBAClient,
    player_id: int,
    team_id: int,
    season: Season | None = None,
    *,
    per_mode: PerMode = "PerGame",
    season_type: SeasonType = "Regular Season",
) -> dict[str, list[PlayerOnCourtDetail]]:
    """Return on-court and off-court splits for a player.

    Fetches the LeaguePlayerOnDetails endpoint for the player's team, then
    partitions rows by court_status == "On" vs "Off".

    Args:
        client: NBA API client
        player_id: NBA player ID
        team_id: NBA team ID the player belongs to
        season: Season in YYYY-YY format (defaults to current season)
        per_mode: "PerGame", "Per36", "Totals", etc.
        season_type: "Regular Season", "Playoffs", etc.

    Returns:
        Dict with keys "on" and "off", each a list of PlayerOnCourtDetail rows
        for the given player_id.

    Examples:
        splits = await get_on_off_splits(client, player_id=2544, team_id=1610612747)
        on_rows  = splits["on"]
        off_rows = splits["off"]

    """
    from fastbreak.endpoints import LeaguePlayerOnDetails  # noqa: PLC0415
    from fastbreak.seasons import get_season_from_date  # noqa: PLC0415

    season = season or get_season_from_date()
    endpoint = LeaguePlayerOnDetails(
        team_id=team_id,
        season=season,
        per_mode=per_mode,
        season_type=season_type,
    )
    response = await client.get(endpoint)
    rows = [r for r in response.details if r.vs_player_id == player_id]
    return {
        "on": [r for r in rows if r.court_status == "On"],
        "off": [r for r in rows if r.court_status == "Off"],
    }


async def get_player_playtypes(
    client: NBAClient,
    player_id: int,
    season: Season | None = None,
    *,
    season_type: SeasonType = "Regular Season",
    type_grouping: str = "offensive",
) -> list[PlayerSynergyPlaytype]:
    """Return play-type breakdown stats for a player.

    Uses the Synergy play-type endpoint, filtered to a single player.

    Args:
        client: NBA API client
        player_id: NBA player ID
        season: Season in YYYY-YY format (defaults to current season)
        season_type: "Regular Season", "Playoffs", etc.
        type_grouping: "offensive" or "defensive"

    Returns:
        List of PlayerSynergyPlaytype rows for this player, one per play type.

    Examples:
        plays = await get_player_playtypes(client, player_id=2544)
        for p in sorted(plays, key=lambda x: x.poss, reverse=True):
            print(p.play_type, p.ppp)
    """
    from fastbreak.endpoints import SynergyPlaytypes  # noqa: PLC0415
    from fastbreak.seasons import get_season_from_date  # noqa: PLC0415

    season = season or get_season_from_date()
    response = await client.get(
        SynergyPlaytypes(
            player_or_team="P",
            season_year=season,
            season_type=season_type,
            type_grouping=type_grouping,
        )
    )
    return [r for r in response.player_stats if r.player_id == player_id]
