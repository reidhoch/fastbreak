"""Player lookup utilities for the NBA Stats API."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastbreak.clients.nba import NBAClient
    from fastbreak.models import PlayerIndexEntry
    from fastbreak.models.league_hustle_stats_player import LeagueHustlePlayer
    from fastbreak.models.league_leaders import LeagueLeader
    from fastbreak.models.player_career_stats import PlayerCareerStatsResponse
    from fastbreak.models.player_game_log import PlayerGameLogEntry
    from fastbreak.types import PerMode, SeasonType, StatCategoryAbbreviation


async def search_players(
    client: NBAClient,
    query: str,
    *,
    season: str | None = None,
    limit: int = 10,
) -> list[PlayerIndexEntry]:
    """Search for players by partial name match.

    Args:
        client: NBA API client
        query: Search string (matches first name, last name, or full name)
        season: Season to search in (defaults to current)
        limit: Maximum results to return

    Returns:
        List of matching PlayerIndexEntry objects, sorted by relevance

    Examples:
        await search_players(client, "Curry")  # finds Stephen, Seth, etc.
        await search_players(client, "Ant")    # finds Anthony Edwards, etc.

    """
    if limit < 1:
        msg = f"limit must be a positive integer, got {limit}"
        raise ValueError(msg)
    if not query or not query.strip():
        return []

    from fastbreak.endpoints import PlayerIndex  # noqa: PLC0415
    from fastbreak.seasons import get_season_from_date  # noqa: PLC0415

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
    season: str | None = None,
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
    from fastbreak.endpoints import PlayerIndex  # noqa: PLC0415
    from fastbreak.seasons import get_season_from_date  # noqa: PLC0415

    season = season or get_season_from_date()
    response = await client.get(PlayerIndex(season=season))

    if isinstance(identifier, int):
        for player in response.players:
            if player.person_id == identifier:
                return player
        return None

    name: str = identifier.lower().strip()
    for player in response.players:
        full_name = f"{player.player_first_name} {player.player_last_name}".lower()
        if full_name == name:
            return player
    return None


async def get_player_id(
    client: NBAClient,
    name: str,
    *,
    season: str | None = None,
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
    season: str | None = None,
    season_type: SeasonType = "Regular Season",
) -> list[PlayerGameLogEntry]:
    """Return a player's game-by-game stats for a season.

    Args:
        client: NBA API client
        player_id: NBA player ID
        season: Season in YYYY-YY format (defaults to current)
        season_type: \"Regular Season\", \"Playoffs\", etc.

    Returns:
        List of PlayerGameLogEntry objects, one per game played

    Examples:
        log = await get_player_game_log(client, player_id=201939)

    """
    from fastbreak.endpoints import PlayerGameLog  # noqa: PLC0415
    from fastbreak.seasons import get_season_from_date  # noqa: PLC0415

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
    season: str | None = None,
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

    Examples:
        scorers = await get_league_leaders(client, stat_category="PTS", limit=10)
        assisters = await get_league_leaders(client, stat_category="AST", limit=5)

    """
    from fastbreak.endpoints import LeagueLeaders  # noqa: PLC0415
    from fastbreak.seasons import get_season_from_date  # noqa: PLC0415

    season = season or get_season_from_date()
    response = await client.get(
        LeagueLeaders(
            season=season,
            stat_category=stat_category,
            season_type=season_type,
        )
    )
    if limit is not None and limit < 1:
        msg = f"limit must be a positive integer, got {limit}"
        raise ValueError(msg)
    leaders = response.leaders
    return leaders if limit is None else leaders[:limit]


async def get_hustle_stats(
    client: NBAClient,
    player_id: int,
    *,
    season: str | None = None,
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
    from fastbreak.seasons import get_season_from_date  # noqa: PLC0415

    season = season or get_season_from_date()
    response = await client.get(
        LeagueHustleStatsPlayer(season=season, season_type=season_type)
    )
    for player in response.players:
        if player.player_id == player_id:
            return player
    return None
