from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from aiohttp import ClientResponseError, ClientSession, RequestInfo
from multidict import CIMultiDict, CIMultiDictProxy
from yarl import URL

from fastbreak.clients.nba import NBAClient


@pytest.fixture
def make_client_response_error():
    """Factory fixture for creating ClientResponseError with specified status code.

    Usage:
        def test_something(make_client_response_error):
            error = make_client_response_error(429)
            assert error.status == 429
    """

    def _make(status: int, url: str = "https://test.com") -> ClientResponseError:
        request_info = RequestInfo(
            url=URL(url),
            method="GET",
            headers=CIMultiDict(),
            real_url=URL(url),
        )
        return ClientResponseError(request_info=request_info, history=(), status=status)

    return _make


@pytest.fixture
def sample_action_data():
    """A minimal valid action for unit tests."""
    return {
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


@pytest.fixture
def sample_shot_action_data():
    """A made shot action for testing shot-specific fields."""
    return {
        "actionNumber": 10,
        "clock": "PT10M30.00S",
        "period": 1,
        "teamId": 1610612754,
        "teamTricode": "IND",
        "personId": 1627783,
        "playerName": "Siakam",
        "playerNameI": "P. Siakam",
        "xLegacy": 15,
        "yLegacy": 80,
        "shotDistance": 8,
        "shotResult": "Made",
        "isFieldGoal": 1,
        "scoreHome": "2",
        "scoreAway": "0",
        "pointsTotal": 2,
        "location": "h",
        "description": "Siakam 8' Driving Layup (2 PTS)",
        "actionType": "2pt",
        "subType": "Driving Layup",
        "videoAvailable": 1,
        "shotValue": 2,
        "actionId": 10,
    }


@pytest.fixture
def sample_meta_data():
    """Sample meta data for responses."""
    return {
        "version": 1,
        "request": "http://nba.cloud/games/0022500571/playbyplay?Format=json",
        "time": "2026-01-15T12:10:24.1024Z",
    }


@pytest.fixture
def sample_game_data(sample_action_data, sample_shot_action_data):
    """Sample game data with multiple actions."""
    return {
        "gameId": "0022500571",
        "videoAvailable": 1,
        "actions": [sample_action_data, sample_shot_action_data],
    }


@pytest.fixture
def sample_response_data(sample_meta_data, sample_game_data):
    """Complete sample response matching API structure."""
    return {
        "meta": sample_meta_data,
        "game": sample_game_data,
    }


@pytest.fixture
def make_mock_client():
    """Factory fixture for creating NBAClient with mocked session.

    Returns a tuple of (client, mock_session) for tests that need to inspect calls.

    Usage:
        def test_something(make_mock_client):
            client, mock_session = make_mock_client(json_data={"resultSets": []})
            result = await client.get(endpoint)
            mock_session.get.assert_called_once()

        # With error simulation:
        def test_error(make_mock_client, make_client_response_error):
            error = make_client_response_error(429)
            client, _ = make_mock_client(raise_error=error)
    """

    def _make(
        json_data: dict[str, Any] | None = None,
        status: int = 200,
        raise_error: Exception | None = None,
        headers: dict[str, str] | None = None,
        **client_kwargs: Any,
    ) -> tuple[NBAClient, MagicMock]:
        # Create mock response
        response = AsyncMock()
        response.status = status
        response.headers = CIMultiDictProxy(CIMultiDict(headers or {}))

        if raise_error:
            response.raise_for_status = MagicMock(side_effect=raise_error)
        else:
            response.raise_for_status = MagicMock()

        response.json = AsyncMock(return_value=json_data)
        response.__aenter__ = AsyncMock(return_value=response)
        response.__aexit__ = AsyncMock(return_value=None)

        # Create mock session
        mock_session = MagicMock(spec=ClientSession)
        mock_session.get = MagicMock(return_value=response)

        # Create client with mock session
        client = NBAClient(session=mock_session, **client_kwargs)

        return client, mock_session

    return _make
