"""WNBA client — async client configured for the WNBA (league ID ``"10"``)."""

from typing import ClassVar

from fastbreak.clients.base import BaseClient
from fastbreak.league import League


class WNBAClient(BaseClient):
    """Async client for the WNBA Stats API."""

    league: ClassVar[League] = League.WNBA
