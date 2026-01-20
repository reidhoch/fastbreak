from asyncio import Lock
from types import TracebackType
from typing import ClassVar, Self, TypeVar

from aiohttp import ClientSession, ClientTimeout, TCPConnector
from pydantic import BaseModel

from fastbreak.endpoints.base import Endpoint

T = TypeVar("T", bound=BaseModel)


class NBAClient:
    """Async client for the NBA Stats API."""

    BASE_URL = "https://stats.nba.com/stats"

    DEFAULT_HEADERS: ClassVar[dict[str, str]] = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "Referer": "https://stats.nba.com/",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0",
        "Sec-Ch-Ua": '"Not.A/Brand";v="8", "Chromium";v="114", "Firefox";v="114"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Fetch-Dest": "empty",
    }

    def __init__(
        self,
        session: ClientSession | None = None,
        timeout: ClientTimeout | None = None,
    ) -> None:
        self._session = session
        self._owns_session = session is None
        self._timeout = timeout or ClientTimeout(total=30)
        self._session_lock = Lock()

    async def _get_session(self) -> ClientSession:
        async with self._session_lock:
            if self._session is None:
                connector = TCPConnector(
                    limit_per_host=10,
                    ttl_dns_cache=300,
                )
                self._session = ClientSession(
                    connector=connector,
                    headers=self.DEFAULT_HEADERS,
                    timeout=self._timeout,
                )
        return self._session

    async def close(self) -> None:
        """Close the client session if we own it."""
        async with self._session_lock:
            if self._owns_session and self._session is not None:
                await self._session.close()
                self._session = None

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.close()

    async def get(self, endpoint: Endpoint[T]) -> T:
        """Fetch data from an endpoint and return the parsed response.

        Args:
            endpoint: An Endpoint instance defining the request

        Returns:
            The parsed response model

        """
        session = await self._get_session()
        url = f"{self.BASE_URL}/{endpoint.path}"
        async with session.get(url, params=endpoint.params()) as resp:
            resp.raise_for_status()
            data = await resp.json()
            return endpoint.parse_response(data)
