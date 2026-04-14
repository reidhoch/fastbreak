"""League configuration — constants and rules for NBA, WNBA, and other leagues."""

from __future__ import annotations

from enum import Enum


class League(Enum):
    """League identifier with associated timing, season, and game constants."""

    NBA = "00"
    WNBA = "10"

    @property
    def league_id(self) -> str:
        """Return the NBA Stats API league ID string."""
        return self.value

    @property
    def quarter_seconds(self) -> int:
        """Return the duration of a regulation quarter in seconds."""
        return _QUARTER_SECONDS[self]

    @property
    def ot_seconds(self) -> int:
        """Return the duration of an overtime period in seconds."""
        return 300  # 5 minutes for both leagues

    @property
    def game_minutes(self) -> int:
        """Return the total regulation game length in minutes."""
        return _GAME_MINUTES[self]

    @property
    def season_games(self) -> int:
        """Return the number of regular-season games."""
        return _SEASON_GAMES[self]

    @property
    def season_start_month(self) -> int:
        """Return the month (1-12) when the season typically begins."""
        return _SEASON_START_MONTH[self]


# Lookup tables keyed by League — avoids repeating if/else chains.
_QUARTER_SECONDS: dict[League, int] = {
    League.NBA: 720,  # 12 minutes
    League.WNBA: 600,  # 10 minutes
}

_GAME_MINUTES: dict[League, int] = {
    League.NBA: 48,
    League.WNBA: 40,
}

_SEASON_GAMES: dict[League, int] = {
    League.NBA: 82,
    League.WNBA: 40,
}

_SEASON_START_MONTH: dict[League, int] = {
    League.NBA: 10,  # October
    League.WNBA: 5,  # May
}
