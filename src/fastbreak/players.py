"""Player lookup utilities for the NBA Stats API."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastbreak.clients.nba import NBAClient
    from fastbreak.models import PlayerIndexEntry


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
    if not query or not query.strip():
        return []

    from fastbreak.endpoints import PlayerIndex  # noqa: PLC0415
    from fastbreak.utils import get_season_from_date  # noqa: PLC0415

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
    from fastbreak.utils import get_season_from_date  # noqa: PLC0415

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
