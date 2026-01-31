import pytest
from aiohttp import ClientResponseError, RequestInfo
from multidict import CIMultiDict
from yarl import URL


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
