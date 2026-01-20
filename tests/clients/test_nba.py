from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiohttp import ClientSession, ClientTimeout

from fastbreak.clients.nba import NBAClient
from fastbreak.endpoints import PlayByPlay
from fastbreak.models import PlayByPlayResponse


@pytest.fixture
def mock_play_by_play_response():
    """Sample play-by-play API response."""
    return {
        "meta": {
            "version": 1,
            "request": "http://nba.cloud/games/0022500571/playbyplay",
            "time": "2026-01-15T12:10:24.1024Z",
        },
        "game": {
            "gameId": "0022500571",
            "videoAvailable": 1,
            "actions": [
                {
                    "actionNumber": 1,
                    "clock": "PT12M00.00S",
                    "period": 1,
                    "teamId": 1610612754,
                    "teamTricode": "IND",
                    "personId": 1630643,
                    "playerName": "Huff",
                    "playerNameI": "J. Huff",
                    "xLegacy": 0,
                    "yLegacy": 0,
                    "shotDistance": 0,
                    "shotResult": "",
                    "isFieldGoal": 0,
                    "scoreHome": "0",
                    "scoreAway": "0",
                    "pointsTotal": 0,
                    "location": "h",
                    "description": "Jump Ball",
                    "actionType": "Jump Ball",
                    "subType": "",
                    "videoAvailable": 1,
                    "shotValue": 0,
                    "actionId": 1,
                }
            ],
        },
    }


class TestNBAClientInit:
    """Tests for NBAClient initialization."""

    def test_default_initialization(self):
        """Client initializes with default values."""
        client = NBAClient()
        assert client._session is None
        assert client._owns_session is True
        assert client._timeout.total == 30

    def test_custom_timeout(self):
        """Client accepts custom timeout."""
        timeout = ClientTimeout(total=60)
        client = NBAClient(timeout=timeout)
        assert client._timeout.total == 60

    def test_provided_session(self):
        """Client uses provided session and doesn't own it."""
        session = MagicMock(spec=ClientSession)
        client = NBAClient(session=session)
        assert client._session is session
        assert client._owns_session is False


class TestNBAClientContextManager:
    """Tests for async context manager protocol."""

    @pytest.mark.asyncio
    async def test_context_manager_enter_returns_self(self):
        """__aenter__ returns the client instance."""
        client = NBAClient()
        result = await client.__aenter__()
        assert result is client
        await client.close()

    @pytest.mark.asyncio
    async def test_context_manager_closes_owned_session(self):
        """__aexit__ closes session when client owns it."""
        client = NBAClient()
        # Create a session first
        with patch.object(client, "_session") as mock_session:
            mock_session.close = AsyncMock()
            client._owns_session = True
            await client.__aexit__(None, None, None)
            mock_session.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_context_manager_preserves_external_session(self):
        """__aexit__ doesn't close externally provided session."""
        external_session = MagicMock(spec=ClientSession)
        external_session.close = AsyncMock()
        client = NBAClient(session=external_session)
        await client.__aexit__(None, None, None)
        external_session.close.assert_not_called()


class TestNBAClientGet:
    """Tests for the get method."""

    @pytest.mark.asyncio
    async def test_get_returns_parsed_response(self, mock_play_by_play_response):
        """get() fetches data and returns parsed model."""
        mock_response = AsyncMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json = AsyncMock(return_value=mock_play_by_play_response)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        mock_session = MagicMock(spec=ClientSession)
        mock_session.get = MagicMock(return_value=mock_response)

        client = NBAClient(session=mock_session)
        endpoint = PlayByPlay("0022500571")

        result = await client.get(endpoint)

        assert isinstance(result, PlayByPlayResponse)
        assert result.game.gameId == "0022500571"
        assert len(result.game.actions) == 1
        mock_session.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_constructs_correct_url(self, mock_play_by_play_response):
        """get() builds URL from BASE_URL and endpoint path."""
        mock_response = AsyncMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json = AsyncMock(return_value=mock_play_by_play_response)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        mock_session = MagicMock(spec=ClientSession)
        mock_session.get = MagicMock(return_value=mock_response)

        client = NBAClient(session=mock_session)
        endpoint = PlayByPlay("0022500571")

        await client.get(endpoint)

        call_args = mock_session.get.call_args
        assert call_args[0][0] == "https://stats.nba.com/stats/playbyplayv3"
        assert call_args[1]["params"] == {"GameID": "0022500571"}


class TestNBAClientSession:
    """Tests for session management."""

    @pytest.mark.asyncio
    async def test_get_session_creates_session_when_none(self):
        """_get_session creates a new session if none exists."""
        client = NBAClient()
        assert client._session is None

        with patch("fastbreak.clients.nba.ClientSession") as mock_session_class:
            mock_session = MagicMock(spec=ClientSession)
            mock_session_class.return_value = mock_session

            session = await client._get_session()

            assert session is mock_session
            mock_session_class.assert_called_once()

        await client.close()

    @pytest.mark.asyncio
    async def test_get_session_reuses_existing_session(self):
        """_get_session returns existing session if present."""
        mock_session = MagicMock(spec=ClientSession)
        client = NBAClient(session=mock_session)

        session = await client._get_session()

        assert session is mock_session

    @pytest.mark.asyncio
    async def test_close_clears_owned_session(self):
        """close() sets session to None when owned."""
        client = NBAClient()
        mock_session = MagicMock(spec=ClientSession)
        mock_session.close = AsyncMock()
        client._session = mock_session

        await client.close()

        assert client._session is None
        mock_session.close.assert_called_once()
