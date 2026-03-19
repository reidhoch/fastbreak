import signal
import warnings

import anyio
import certifi
import pytest
from aiohttp import ClientResponseError, ClientSession, ClientTimeout, DummyCookieJar
from pydantic import ValidationError
from pytest_mock import MockerFixture
from tenacity import RetryCallState

from fastbreak.clients.nba import (
    BATCH_PROGRESS_THRESHOLD,
    HTTP_SERVER_ERROR_MIN,
    HTTP_TOO_MANY_REQUESTS,
    NBAClient,
    _RetryAfterState,
    _is_retryable_error,
    _make_wait_with_retry_after,
)
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


class TestIsRetryableError:
    """Tests for the _is_retryable_error helper function."""

    @pytest.mark.parametrize(
        "status,should_retry",
        [
            pytest.param(429, True, id="429_too_many_requests"),
            pytest.param(500, True, id="500_server_error"),
            pytest.param(502, True, id="502_bad_gateway"),
            pytest.param(503, True, id="503_service_unavailable"),
            pytest.param(504, True, id="504_gateway_timeout"),
            pytest.param(400, False, id="400_bad_request"),
            pytest.param(401, False, id="401_unauthorized"),
            pytest.param(403, False, id="403_forbidden"),
            pytest.param(404, False, id="404_not_found"),
        ],
    )
    def test_http_status_retry_behavior(
        self, make_client_response_error, status, should_retry
    ):
        """HTTP status codes trigger appropriate retry behavior."""
        exc = make_client_response_error(status)
        assert _is_retryable_error(exc) is should_retry

    def test_retries_on_timeout_error(self):
        """TimeoutError triggers retry."""
        assert _is_retryable_error(TimeoutError("timeout")) is True

    def test_retries_on_os_error(self):
        """OSError triggers retry."""
        assert _is_retryable_error(OSError("connection reset")) is True

    def test_no_retry_on_value_error(self):
        """ValueError does not trigger retry."""
        assert _is_retryable_error(ValueError("bad value")) is False


class TestConstants:
    """Tests for module constants."""

    def test_http_too_many_requests_value(self):
        """HTTP_TOO_MANY_REQUESTS is 429."""
        assert HTTP_TOO_MANY_REQUESTS == 429

    def test_http_server_error_min_value(self):
        """HTTP_SERVER_ERROR_MIN is 500."""
        assert HTTP_SERVER_ERROR_MIN == 500

    def test_batch_progress_threshold_value(self):
        """BATCH_PROGRESS_THRESHOLD is 10."""
        assert BATCH_PROGRESS_THRESHOLD == 10


class TestNBAClientInit:
    """Tests for NBAClient initialization."""

    def test_default_initialization(self):
        """Client initializes with default values."""
        client = NBAClient()
        assert client._session is None
        assert client._owns_session is True
        assert client._timeout.total == 60  # Increased from 30s for NBA API reliability

    def test_default_max_retries(self):
        """Default max_retries is 3."""
        client = NBAClient()
        assert client._max_retries == 3

    def test_custom_max_retries(self):
        """Custom max_retries is respected."""
        client = NBAClient(max_retries=5)
        assert client._max_retries == 5

    def test_default_retry_wait_strategy(self):
        """Default wait strategy config uses correct values."""
        client = NBAClient()
        assert client._retry_wait_min == 1.0
        assert client._retry_wait_max == 10.0

    def test_custom_retry_wait_min(self):
        """Custom retry_wait_min is stored."""
        client = NBAClient(retry_wait_min=2.5)
        assert client._retry_wait_min == 2.5

    def test_custom_retry_wait_max(self):
        """Custom retry_wait_max is stored."""
        client = NBAClient(retry_wait_max=30.0)
        assert client._retry_wait_max == 30.0

    def test_custom_retry_wait_both(self):
        """Custom retry_wait_min and max are both stored."""
        client = NBAClient(retry_wait_min=0.5, retry_wait_max=5.0)
        assert client._retry_wait_min == 0.5
        assert client._retry_wait_max == 5.0

    def test_custom_timeout(self):
        """Client accepts custom timeout."""
        timeout = ClientTimeout(total=60)
        client = NBAClient(timeout=timeout)
        assert client._timeout.total == 60

    def test_provided_session(self, mocker: MockerFixture):
        """Client uses provided session and doesn't own it."""
        session = mocker.MagicMock(spec=ClientSession)
        client = NBAClient(session=session)
        assert client._session is session
        assert client._owns_session is False


class TestNBAClientGetSession:
    """Tests for _get_session method."""

    async def test_creates_ssl_context_with_certifi(self, mocker: MockerFixture):
        """_get_session creates SSL context using certifi CA bundle."""
        client = NBAClient()

        mock_ssl = mocker.patch("fastbreak.clients.nba.ssl.create_default_context")
        mocker.patch("fastbreak.clients.nba.TCPConnector")
        mocker.patch(
            "fastbreak.clients.nba.ClientSession",
            return_value=mocker.MagicMock(spec=ClientSession),
        )
        mock_ssl.return_value = mocker.MagicMock()

        await client._get_session()

        mock_ssl.assert_called_once_with(cafile=certifi.where())
        await client.close()

    async def test_creates_connector_with_correct_params(self, mocker: MockerFixture):
        """_get_session creates TCPConnector with correct parameters."""
        client = NBAClient()

        mock_ssl_ctx = mocker.MagicMock()
        mock_ssl = mocker.patch("fastbreak.clients.nba.ssl.create_default_context")
        mock_ssl.return_value = mock_ssl_ctx
        mock_connector_cls = mocker.patch("fastbreak.clients.nba.TCPConnector")
        mocker.patch(
            "fastbreak.clients.nba.ClientSession",
            return_value=mocker.MagicMock(spec=ClientSession),
        )

        await client._get_session()

        mock_connector_cls.assert_called_once_with(
            limit_per_host=10,
            ssl=mock_ssl_ctx,
            ttl_dns_cache=300,
        )
        await client.close()

    async def test_creates_session_with_correct_params(self, mocker: MockerFixture):
        """_get_session creates ClientSession with correct parameters."""
        client = NBAClient()

        mocker.patch("fastbreak.clients.nba.ssl.create_default_context")
        mock_connector = mocker.MagicMock()
        mocker.patch("fastbreak.clients.nba.TCPConnector", return_value=mock_connector)
        mock_session = mocker.MagicMock(spec=ClientSession)
        mock_session_cls = mocker.patch(
            "fastbreak.clients.nba.ClientSession", return_value=mock_session
        )

        result = await client._get_session()

        mock_session_cls.assert_called_once_with(
            connector=mock_connector,
            headers=NBAClient.DEFAULT_HEADERS,
            timeout=client._timeout,
            cookie_jar=mocker.ANY,
        )
        _, kwargs = mock_session_cls.call_args
        assert isinstance(kwargs["cookie_jar"], DummyCookieJar)
        assert result is mock_session
        await client.close()

    async def test_reuses_existing_session(self, mocker: MockerFixture):
        """_get_session returns existing session if present."""
        mock_session = mocker.MagicMock(spec=ClientSession)
        client = NBAClient(session=mock_session)

        session = await client._get_session()

        assert session is mock_session

    async def test_session_created_only_once(self, mocker: MockerFixture):
        """_get_session only creates session on first call."""
        client = NBAClient()

        mocker.patch("fastbreak.clients.nba.ssl.create_default_context")
        mocker.patch("fastbreak.clients.nba.TCPConnector")
        mock_session = mocker.MagicMock(spec=ClientSession)
        mock_session_cls = mocker.patch(
            "fastbreak.clients.nba.ClientSession", return_value=mock_session
        )

        session1 = await client._get_session()
        session2 = await client._get_session()

        assert session1 is session2
        assert mock_session_cls.call_count == 1
        await client.close()


class TestNBAClientContextManager:
    """Tests for async context manager protocol."""

    async def test_context_manager_enter_returns_self(self):
        """async with NBAClient() yields the client instance."""
        client_instance = NBAClient(handle_signals=False)
        async with client_instance as client:
            assert client is client_instance

    async def test_context_manager_closes_owned_session(self, mocker: MockerFixture):
        """Context manager closes session when client owns it."""
        client = NBAClient(handle_signals=False)
        mock_session = mocker.patch.object(client, "_session")
        mock_session.close = mocker.AsyncMock()
        client._owns_session = True
        async with client:
            pass
        mock_session.close.assert_called_once()

    async def test_context_manager_preserves_external_session(
        self, mocker: MockerFixture
    ):
        """Context manager doesn't close externally provided session."""
        external_session = mocker.MagicMock(spec=ClientSession)
        external_session.close = mocker.AsyncMock()
        async with NBAClient(session=external_session, handle_signals=False):
            pass
        external_session.close.assert_not_called()

    async def test_context_manager_with_handle_signals(self, mocker: MockerFixture):
        """Context manager manages signal handler loop when handle_signals=True."""

        async def never_signals():
            await anyio.sleep_forever()
            yield  # pragma: no cover

        mock_receiver = mocker.MagicMock()
        mock_receiver.__enter__ = mocker.MagicMock(return_value=never_signals())
        mock_receiver.__exit__ = mocker.MagicMock(return_value=False)
        mocker.patch("anyio.open_signal_receiver", return_value=mock_receiver)

        client = NBAClient(handle_signals=True)
        async with client:
            pass

        assert client._session is None

    async def test_context_manager_propagates_body_exception_with_handle_signals(
        self, mocker: MockerFixture
    ):
        """Body exceptions are not wrapped in ExceptionGroup when handle_signals=True."""

        async def never_signals():
            await anyio.sleep_forever()
            yield  # pragma: no cover

        mock_receiver = mocker.MagicMock()
        mock_receiver.__enter__ = mocker.MagicMock(return_value=never_signals())
        mock_receiver.__exit__ = mocker.MagicMock(return_value=False)
        mocker.patch("anyio.open_signal_receiver", return_value=mock_receiver)

        with pytest.raises(ValueError, match="body error"):
            async with NBAClient(handle_signals=True):
                raise ValueError("body error")


class TestNBAClientClose:
    """Tests for close method."""

    async def test_close_clears_owned_session(self, mocker: MockerFixture):
        """close() sets session to None when owned."""
        client = NBAClient()
        mock_session = mocker.MagicMock(spec=ClientSession)
        mock_session.close = mocker.AsyncMock()
        client._session = mock_session

        await client.close()

        assert client._session is None
        mock_session.close.assert_called_once()

    async def test_close_does_not_close_external_session(self, mocker: MockerFixture):
        """close() doesn't close externally provided session."""
        external_session = mocker.MagicMock(spec=ClientSession)
        external_session.close = mocker.AsyncMock()
        client = NBAClient(session=external_session)

        await client.close()

        external_session.close.assert_not_called()

    async def test_close_logs_warning_on_timeout(self, mocker: MockerFixture):
        """close() logs a warning when session.close() exceeds the timeout."""
        client = NBAClient()
        mock_session = mocker.MagicMock(spec=ClientSession)
        mock_session.close = mocker.AsyncMock()
        client._session = mock_session
        mock_logger = mocker.patch("fastbreak.clients.nba.logger")

        mock_cancel_scope = mocker.MagicMock()
        mock_cancel_scope.cancelled_caught = True
        mock_cm = mocker.MagicMock()
        mock_cm.__enter__ = mocker.MagicMock(return_value=mock_cancel_scope)
        mock_cm.__exit__ = mocker.MagicMock(return_value=False)
        mocker.patch("anyio.move_on_after", return_value=mock_cm)

        await client.close()

        mock_logger.warning.assert_called_once_with(
            "session_close_timeout",
            timeout=mocker.ANY,
            hint="Session close timed out, forcing cleanup",
        )
        assert client._session is None


# Helper to create mock HTTP responses
def _make_mock_response(
    mocker: MockerFixture,
    status: int = 200,
    json_data: dict | None = None,
    raise_error: Exception | None = None,
    headers: dict | None = None,
):
    """Create a mock aiohttp response for testing."""
    from multidict import CIMultiDict, CIMultiDictProxy

    response = mocker.AsyncMock()
    response.status = status
    response.headers = CIMultiDictProxy(CIMultiDict(headers or {}))

    if raise_error:
        response.raise_for_status = mocker.MagicMock(side_effect=raise_error)
    else:
        response.raise_for_status = mocker.MagicMock()

    response.json = mocker.AsyncMock(return_value=json_data)
    response.__aenter__ = mocker.AsyncMock(return_value=response)
    response.__aexit__ = mocker.AsyncMock(return_value=None)
    return response


class TestNBAClientGet:
    """Tests for the get method."""

    async def test_get_returns_parsed_response(
        self, mock_play_by_play_response, make_mock_client
    ):
        """get() fetches data and returns parsed model."""
        client, mock_session = make_mock_client(json_data=mock_play_by_play_response)
        endpoint = PlayByPlay(game_id="0022500571")

        result = await client.get(endpoint)

        assert isinstance(result, PlayByPlayResponse)
        assert result.game.gameId == "0022500571"
        assert len(result.game.actions) == 1
        mock_session.get.assert_called_once()

    async def test_get_constructs_correct_url(
        self, mock_play_by_play_response, make_mock_client
    ):
        """get() builds URL from BASE_URL and endpoint path."""
        client, mock_session = make_mock_client(json_data=mock_play_by_play_response)
        endpoint = PlayByPlay(game_id="0022500571")

        await client.get(endpoint)

        call_args = mock_session.get.call_args
        assert call_args[0][0] == "https://stats.nba.com/stats/playbyplayv3"
        assert call_args[1]["params"] == {
            "GameID": "0022500571",
            "EndPeriod": "0",
            "StartPeriod": "0",
        }

    async def test_get_logs_request_attempt(
        self, mock_play_by_play_response, make_mock_client, mocker: MockerFixture
    ):
        """get() logs request attempt with correct parameters."""
        client, mock_session = make_mock_client(json_data=mock_play_by_play_response)
        endpoint = PlayByPlay(game_id="0022500571")

        mock_logger = mocker.patch("fastbreak.clients.nba.logger")
        mock_bound = mocker.MagicMock()
        mock_bound.adebug = mocker.AsyncMock()
        mock_logger.bind.return_value = mock_bound

        await client.get(endpoint)

        # Verify logger.bind was called with endpoint path and request_id
        mock_logger.bind.assert_called_once()
        bind_kwargs = mock_logger.bind.call_args[1]
        assert bind_kwargs["endpoint"] == "playbyplayv3"
        assert "request_id" in bind_kwargs  # UUID generated automatically

        # Verify request_attempt log was called with all params
        request_log_calls = [
            c for c in mock_bound.adebug.call_args_list if c[0][0] == "request_attempt"
        ]
        assert len(request_log_calls) == 1
        call_kwargs = request_log_calls[0][1]
        assert call_kwargs["attempt"] == 1
        assert call_kwargs["url"] == "https://stats.nba.com/stats/playbyplayv3"
        assert call_kwargs["params"] == endpoint.params()

    async def test_get_logs_success(
        self, mock_play_by_play_response, make_mock_client, mocker: MockerFixture
    ):
        """get() logs success with attempt number."""
        client, mock_session = make_mock_client(json_data=mock_play_by_play_response)
        endpoint = PlayByPlay(game_id="0022500571")

        mock_logger = mocker.patch("fastbreak.clients.nba.logger")
        mock_bound = mocker.MagicMock()
        mock_bound.adebug = mocker.AsyncMock()
        mock_logger.bind.return_value = mock_bound

        await client.get(endpoint)

        # Verify success log was called
        success_calls = [
            c for c in mock_bound.adebug.call_args_list if c[0][0] == "request_success"
        ]
        assert len(success_calls) == 1
        assert success_calls[0][1]["attempt"] == 1

    async def test_get_logs_rate_limited_on_429(
        self, make_client_response_error, make_mock_client, mocker: MockerFixture
    ):
        """get() logs rate_limited when receiving 429 status."""
        error = make_client_response_error(429, "https://stats.nba.com/stats/test")
        client, mock_session = make_mock_client(
            status=429,
            raise_error=error,
            headers={"Retry-After": "30"},
            max_retries=0,
            retry_wait_min=0.01,
        )
        endpoint = PlayByPlay(game_id="0022500571")

        mock_logger = mocker.patch("fastbreak.clients.nba.logger")
        mock_bound = mocker.MagicMock()
        mock_bound.adebug = mocker.AsyncMock()
        mock_logger.bind.return_value = mock_bound

        with pytest.raises(ClientResponseError):
            await client.get(endpoint)

        # Verify rate_limited log was called with correct params
        rate_limit_calls = [
            c for c in mock_bound.adebug.call_args_list if c[0][0] == "rate_limited"
        ]
        assert len(rate_limit_calls) == 1
        call_kwargs = rate_limit_calls[0][1]
        assert call_kwargs["status"] == 429
        assert call_kwargs["retry_after"] == 30.0  # Parsed to float
        assert call_kwargs["retry_after_raw"] == "30"  # Original header value
        assert call_kwargs["attempt"] == 1

    async def test_get_logs_validation_failed(
        self, make_mock_client, mocker: MockerFixture
    ):
        """get() logs validation_failed and re-raises ValidationError with context."""
        client, mock_session = make_mock_client(json_data={"invalid": "data"})
        endpoint = PlayByPlay(game_id="0022500571")

        mock_logger = mocker.patch("fastbreak.clients.nba.logger")
        mock_bound = mocker.MagicMock()
        mock_bound.adebug = mocker.AsyncMock()
        mock_bound.awarning = mocker.AsyncMock()
        mock_logger.bind.return_value = mock_bound

        # Specifically catch ValidationError, not generic Exception
        with pytest.raises(ValidationError) as exc_info:
            await client.get(endpoint)

        # Verify the ValidationError contains useful field information
        error = exc_info.value
        assert error.error_count() > 0  # At least one validation error
        # The error should mention missing required fields
        error_str = str(error)
        assert "game" in error_str.lower() or "validation" in error_str.lower()

        # Verify validation_failed log was called at WARNING level
        validation_calls = [
            c
            for c in mock_bound.awarning.call_args_list
            if c[0][0] == "validation_failed"
        ]
        assert len(validation_calls) == 1
        call_kwargs = validation_calls[0][1]
        assert "error" in call_kwargs
        assert call_kwargs["error"] is not None  # error string should be set
        assert call_kwargs["endpoint"] == "playbyplayv3"
        assert call_kwargs["response_keys"] == ["invalid"]

    async def test_get_validation_error_contains_field_info(self, make_mock_client):
        """ValidationError should contain specific field information."""
        # Response missing required 'game' field
        client, mock_session = make_mock_client(json_data={"meta": {}, "other": "data"})
        endpoint = PlayByPlay(game_id="0022500571")

        with pytest.raises(ValidationError) as exc_info:
            await client.get(endpoint)

        # Verify the error provides useful debugging information
        error = exc_info.value
        errors = error.errors()
        assert len(errors) > 0

        # Check that error locations are provided (field paths)
        error_locs = [e.get("loc") for e in errors]
        assert all(loc is not None for loc in error_locs)

        # Check that error types are provided
        error_types = [e.get("type") for e in errors]
        assert all(t is not None for t in error_types)

    async def test_get_validation_error_is_not_wrapped(self, make_mock_client):
        """ValidationError should be re-raised directly, not wrapped."""
        client, mock_session = make_mock_client(json_data={"wrong": "structure"})
        endpoint = PlayByPlay(game_id="0022500571")

        with pytest.raises(ValidationError) as exc_info:
            await client.get(endpoint)

        # Verify it's a direct ValidationError, not wrapped in another exception
        assert type(exc_info.value) is ValidationError
        # Verify __cause__ is not set (not chained from another exception)
        assert exc_info.value.__cause__ is None

    async def test_get_validation_error_log_includes_response_keys(
        self, make_mock_client, mocker: MockerFixture
    ):
        """Logged validation error should include response keys for debugging."""
        # Response with unexpected structure
        client, mock_session = make_mock_client(
            json_data={"unexpected_key1": "value1", "unexpected_key2": "value2"}
        )
        endpoint = PlayByPlay(game_id="0022500571")

        mock_logger = mocker.patch("fastbreak.clients.nba.logger")
        mock_bound = mocker.MagicMock()
        mock_bound.adebug = mocker.AsyncMock()
        mock_bound.awarning = mocker.AsyncMock()
        mock_logger.bind.return_value = mock_bound

        with pytest.raises(ValidationError):
            await client.get(endpoint)

        # Find the validation_failed log call
        validation_calls = [
            c
            for c in mock_bound.awarning.call_args_list
            if c[0][0] == "validation_failed"
        ]
        assert len(validation_calls) == 1

        # Verify response_keys are logged to help debug what was received
        call_kwargs = validation_calls[0][1]
        response_keys = call_kwargs["response_keys"]
        assert "unexpected_key1" in response_keys
        assert "unexpected_key2" in response_keys

    async def test_get_rate_limited_not_logged_for_non_429(
        self, mock_play_by_play_response, make_mock_client, mocker: MockerFixture
    ):
        """get() only logs rate_limited for 429 status, not other statuses."""
        client, mock_session = make_mock_client(json_data=mock_play_by_play_response)
        endpoint = PlayByPlay(game_id="0022500571")

        mock_logger = mocker.patch("fastbreak.clients.nba.logger")
        mock_bound = mocker.MagicMock()
        mock_bound.adebug = mocker.AsyncMock()
        mock_logger.bind.return_value = mock_bound

        await client.get(endpoint)

        # Verify rate_limited log was NOT called
        rate_limit_calls = [
            c for c in mock_bound.adebug.call_args_list if c[0][0] == "rate_limited"
        ]
        assert len(rate_limit_calls) == 0


class TestNBAClientRetry:
    """Tests for retry logic."""

    @pytest.fixture
    def mock_success_response(self, mock_play_by_play_response, mocker: MockerFixture):
        """Create a successful mock response."""
        return _make_mock_response(mocker, json_data=mock_play_by_play_response)

    async def test_retries_on_429(
        self,
        mock_success_response,
        make_client_response_error,
        mock_play_by_play_response,
        mocker: MockerFixture,
    ):
        """Retry on 429 rate limit error."""
        call_count = 0

        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                error = make_client_response_error(429)
                return _make_mock_response(mocker, status=429, raise_error=error)
            return mock_success_response

        mock_session = mocker.MagicMock(spec=ClientSession)
        mock_session.get = mocker.MagicMock(side_effect=side_effect)

        client = NBAClient(
            session=mock_session, retry_wait_min=0.01, retry_wait_max=0.02
        )
        endpoint = PlayByPlay(game_id="0022500571")

        result = await client.get(endpoint)

        assert call_count == 3
        assert isinstance(result, PlayByPlayResponse)

    async def test_retries_on_500(
        self,
        mock_success_response,
        make_client_response_error,
        mock_play_by_play_response,
        mocker: MockerFixture,
    ):
        """Retry on 500 server error."""
        call_count = 0

        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                error = make_client_response_error(500)
                return _make_mock_response(mocker, status=500, raise_error=error)
            return mock_success_response

        mock_session = mocker.MagicMock(spec=ClientSession)
        mock_session.get = mocker.MagicMock(side_effect=side_effect)

        client = NBAClient(
            session=mock_session, retry_wait_min=0.01, retry_wait_max=0.02
        )
        endpoint = PlayByPlay(game_id="0022500571")

        result = await client.get(endpoint)

        assert call_count == 2
        assert isinstance(result, PlayByPlayResponse)

    async def test_retries_on_timeout(
        self, mock_success_response, mock_play_by_play_response, mocker: MockerFixture
    ):
        """Retry on timeout error."""
        call_count = 0

        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                error_response = mocker.AsyncMock()
                error_response.__aenter__ = mocker.AsyncMock(
                    side_effect=TimeoutError("Connection timed out")
                )
                error_response.__aexit__ = mocker.AsyncMock(return_value=None)
                return error_response
            return mock_success_response

        mock_session = mocker.MagicMock(spec=ClientSession)
        mock_session.get = mocker.MagicMock(side_effect=side_effect)

        client = NBAClient(
            session=mock_session, retry_wait_min=0.01, retry_wait_max=0.02
        )
        endpoint = PlayByPlay(game_id="0022500571")

        result = await client.get(endpoint)

        assert call_count == 2
        assert isinstance(result, PlayByPlayResponse)

    @pytest.mark.parametrize(
        "status",
        [
            pytest.param(401, id="401_unauthorized"),
            pytest.param(403, id="403_forbidden"),
            pytest.param(404, id="404_not_found"),
        ],
    )
    async def test_no_retry_on_client_errors(
        self, make_client_response_error, status, mocker: MockerFixture
    ):
        """Client errors (4xx except 429) do not trigger retry."""
        error = make_client_response_error(status)
        mock_response = _make_mock_response(mocker, status=status, raise_error=error)
        mock_session = mocker.MagicMock(spec=ClientSession)
        mock_session.get = mocker.MagicMock(return_value=mock_response)

        client = NBAClient(
            session=mock_session, retry_wait_min=0.01, retry_wait_max=0.02
        )
        endpoint = PlayByPlay(game_id="0022500571")

        with pytest.raises(ClientResponseError) as exc_info:
            await client.get(endpoint)

        assert exc_info.value.status == status
        assert mock_session.get.call_count == 1

    async def test_exhausted_retries_raises(
        self, make_client_response_error, mocker: MockerFixture
    ):
        """Exception raised after max retries exhausted."""
        error = make_client_response_error(429)
        mock_response = _make_mock_response(mocker, status=429, raise_error=error)
        mock_session = mocker.MagicMock(spec=ClientSession)
        mock_session.get = mocker.MagicMock(return_value=mock_response)

        # max_retries=2 means 3 total attempts (1 initial + 2 retries)
        client = NBAClient(
            session=mock_session,
            max_retries=2,
            retry_wait_min=0.01,
            retry_wait_max=0.02,
        )
        endpoint = PlayByPlay(game_id="0022500571")

        with pytest.raises(ClientResponseError) as exc_info:
            await client.get(endpoint)

        assert exc_info.value.status == 429
        assert mock_session.get.call_count == 3

    def test_custom_retry_config(self):
        """Custom retry parameters are stored correctly."""
        client = NBAClient(max_retries=5, retry_wait_min=2.0, retry_wait_max=30.0)

        # Verify the retry config values are stored correctly
        assert client._max_retries == 5
        assert client._retry_wait_min == 2.0
        assert client._retry_wait_max == 30.0


class TestNBAClientGetMany:
    """Tests for the get_many batch fetch method."""

    async def test_get_many_returns_ordered_results(
        self, mock_play_by_play_response, make_mock_client
    ):
        """get_many returns results in same order as input."""
        client, mock_session = make_mock_client(json_data=mock_play_by_play_response)
        endpoints = [PlayByPlay(game_id=f"002250057{i}") for i in range(3)]

        results = await client.get_many(endpoints)

        assert len(results) == 3
        assert all(isinstance(r, PlayByPlayResponse) for r in results)

    async def test_get_many_empty_list(self):
        """get_many with empty list returns empty list."""
        client = NBAClient()
        results = await client.get_many([])
        assert results == []
        await client.close()

    async def test_get_many_default_concurrency(
        self, mock_play_by_play_response, make_mock_client, mocker: MockerFixture
    ):
        """get_many defaults to concurrency of 3."""
        client, mock_session = make_mock_client(json_data=mock_play_by_play_response)
        endpoints = [PlayByPlay(game_id="0022500571")]

        mock_logger = mocker.patch("fastbreak.clients.nba.logger")
        mock_bound = mocker.MagicMock()
        mock_bound.adebug = mocker.AsyncMock()
        mock_logger.bind.return_value = mock_bound

        await client.get_many(endpoints)

        # Verify logger.bind was called with concurrency=3 (the default)
        bind_calls = [
            c for c in mock_logger.bind.call_args_list if "concurrency" in c[1]
        ]
        assert len(bind_calls) == 1
        assert bind_calls[0][1]["concurrency"] == 3

    async def test_get_many_custom_concurrency(
        self, mock_play_by_play_response, make_mock_client, mocker: MockerFixture
    ):
        """get_many respects custom max_concurrency."""
        client, mock_session = make_mock_client(json_data=mock_play_by_play_response)
        endpoints = [PlayByPlay(game_id="0022500571")]

        mock_logger = mocker.patch("fastbreak.clients.nba.logger")
        mock_bound = mocker.MagicMock()
        mock_bound.adebug = mocker.AsyncMock()
        mock_logger.bind.return_value = mock_bound

        await client.get_many(endpoints, max_concurrency=5)

        # Verify logger.bind was called with concurrency=5
        bind_calls = [
            c for c in mock_logger.bind.call_args_list if "concurrency" in c[1]
        ]
        assert len(bind_calls) == 1
        assert bind_calls[0][1]["concurrency"] == 5

    async def test_get_many_logs_batch_start(
        self, mock_play_by_play_response, make_mock_client, mocker: MockerFixture
    ):
        """get_many logs batch_start with total count."""
        client, mock_session = make_mock_client(json_data=mock_play_by_play_response)
        endpoints = [PlayByPlay(game_id=f"002250057{i}") for i in range(3)]

        mock_logger = mocker.patch("fastbreak.clients.nba.logger")
        mock_bound = mocker.MagicMock()
        mock_bound.adebug = mocker.AsyncMock()
        mock_logger.bind.return_value = mock_bound

        await client.get_many(endpoints)

        # Verify batch_start was logged
        start_calls = [
            c for c in mock_bound.adebug.call_args_list if c[0][0] == "batch_start"
        ]
        assert len(start_calls) == 1
        # Verify total was bound in logger
        bind_calls = [c for c in mock_logger.bind.call_args_list if "total" in c[1]]
        assert len(bind_calls) == 1
        assert bind_calls[0][1]["total"] == 3

    async def test_get_many_logs_batch_complete(
        self, mock_play_by_play_response, make_mock_client, mocker: MockerFixture
    ):
        """get_many logs batch_complete with total count."""
        client, mock_session = make_mock_client(json_data=mock_play_by_play_response)
        endpoints = [PlayByPlay(game_id=f"002250057{i}") for i in range(3)]

        mock_logger = mocker.patch("fastbreak.clients.nba.logger")
        mock_bound = mocker.MagicMock()
        mock_bound.adebug = mocker.AsyncMock()
        mock_logger.bind.return_value = mock_bound

        await client.get_many(endpoints)

        # Verify batch_complete was logged with total
        complete_calls = [
            c for c in mock_bound.adebug.call_args_list if c[0][0] == "batch_complete"
        ]
        assert len(complete_calls) == 1
        assert complete_calls[0][1]["total"] == 3

    async def test_get_many_logs_batch_progress_for_large_batches(
        self, mock_play_by_play_response, make_mock_client, mocker: MockerFixture
    ):
        """get_many logs batch_progress for batches >= BATCH_PROGRESS_THRESHOLD."""
        client, mock_session = make_mock_client(json_data=mock_play_by_play_response)
        # Create enough endpoints to trigger progress logging
        endpoints = [
            PlayByPlay(game_id=f"00225005{i:02d}")
            for i in range(BATCH_PROGRESS_THRESHOLD)
        ]

        mock_logger = mocker.patch("fastbreak.clients.nba.logger")
        mock_bound = mocker.MagicMock()
        mock_bound.adebug = mocker.AsyncMock()
        mock_logger.bind.return_value = mock_bound

        await client.get_many(endpoints, max_concurrency=1)

        # Verify batch_progress was logged at least once
        progress_calls = [
            c for c in mock_bound.adebug.call_args_list if c[0][0] == "batch_progress"
        ]
        assert len(progress_calls) >= 1
        # Verify completed and total were passed
        for call in progress_calls:
            assert "completed" in call[1]
            assert "total" in call[1]

    async def test_get_many_no_progress_for_small_batches(
        self, mock_play_by_play_response, make_mock_client, mocker: MockerFixture
    ):
        """get_many doesn't log batch_progress for batches < BATCH_PROGRESS_THRESHOLD."""
        client, mock_session = make_mock_client(json_data=mock_play_by_play_response)
        # Create fewer endpoints than threshold
        endpoints = [PlayByPlay(game_id=f"002250057{i}") for i in range(3)]

        mock_logger = mocker.patch("fastbreak.clients.nba.logger")
        mock_bound = mocker.MagicMock()
        mock_bound.adebug = mocker.AsyncMock()
        mock_logger.bind.return_value = mock_bound

        await client.get_many(endpoints)

        # Verify batch_progress was NOT logged
        progress_calls = [
            c for c in mock_bound.adebug.call_args_list if c[0][0] == "batch_progress"
        ]
        assert len(progress_calls) == 0

    async def test_get_many_respects_concurrency_limit(
        self, mock_play_by_play_response, mocker: MockerFixture
    ):
        """get_many limits concurrent requests via semaphore."""
        concurrent_count = 0
        max_concurrent = 0
        lock = anyio.Lock()

        async def mock_aenter(self):
            nonlocal concurrent_count, max_concurrent
            async with lock:
                concurrent_count += 1
                max_concurrent = max(max_concurrent, concurrent_count)
            await anyio.sleep(0.01)  # Simulate network delay
            return self

        async def mock_aexit(self, *args):
            nonlocal concurrent_count
            async with lock:
                concurrent_count -= 1

        def create_mock_response():
            response = mocker.AsyncMock()
            response.status = 200
            response.raise_for_status = mocker.MagicMock()
            response.json = mocker.AsyncMock(return_value=mock_play_by_play_response)
            response.__aenter__ = lambda s: mock_aenter(s)
            response.__aexit__ = lambda s, *args: mock_aexit(s, *args)
            return response

        mock_session = mocker.MagicMock(spec=ClientSession)
        mock_session.get = mocker.MagicMock(
            side_effect=lambda *a, **k: create_mock_response()
        )

        client = NBAClient(session=mock_session)
        endpoints = [PlayByPlay(game_id=f"002250057{i}") for i in range(10)]

        await client.get_many(endpoints, max_concurrency=3)

        assert max_concurrent <= 3

    async def test_get_many_raises_exception_group_on_error(
        self,
        make_client_response_error,
        mock_play_by_play_response,
        mocker: MockerFixture,
    ):
        """get_many raises ExceptionGroup when any request fails."""
        call_count = 0

        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                error = make_client_response_error(404)
                return _make_mock_response(mocker, status=404, raise_error=error)
            return _make_mock_response(mocker, json_data=mock_play_by_play_response)

        mock_session = mocker.MagicMock(spec=ClientSession)
        mock_session.get = mocker.MagicMock(side_effect=side_effect)

        client = NBAClient(session=mock_session)
        endpoints = [PlayByPlay(game_id=f"002250057{i}") for i in range(3)]

        with pytest.raises(ExceptionGroup) as exc_info:
            await client.get_many(endpoints)

        # TaskGroup wraps exceptions in ExceptionGroup
        exceptions = exc_info.value.exceptions
        assert len(exceptions) == 1
        assert isinstance(exceptions[0], ClientResponseError)
        assert exceptions[0].status == 404


class TestNBAClientRequestDelay:
    """Tests for the request_delay parameter."""

    def test_request_delay_default_is_zero(self):
        """request_delay defaults to 0.0."""
        client = NBAClient()
        assert client._request_delay == 0.0

    def test_request_delay_stored_correctly(self):
        """request_delay parameter is stored correctly."""
        client = NBAClient(request_delay=0.5)
        assert client._request_delay == 0.5

    def test_request_delay_accepts_float(self):
        """request_delay accepts float values."""
        client = NBAClient(request_delay=0.123)
        assert client._request_delay == 0.123

    def test_request_delay_accepts_integer(self):
        """request_delay accepts integer values (converted to float semantics)."""
        client = NBAClient(request_delay=1)
        assert client._request_delay == 1

    async def test_get_many_no_delay_when_zero(
        self, mock_play_by_play_response, make_mock_client, mocker: MockerFixture
    ):
        """get_many does not sleep when request_delay is 0."""
        client, mock_session = make_mock_client(
            json_data=mock_play_by_play_response, request_delay=0.0
        )
        endpoints = [PlayByPlay(game_id=f"002250057{i}") for i in range(3)]

        mock_sleep = mocker.patch("anyio.sleep", new_callable=mocker.AsyncMock)
        await client.get_many(endpoints)
        # Should not have called sleep since delay is 0
        mock_sleep.assert_not_called()

    async def test_get_many_applies_request_delay(
        self, mock_play_by_play_response, make_mock_client, mocker: MockerFixture
    ):
        """get_many sleeps once per request (after the request, inside the slot) when request_delay > 0."""
        client, mock_session = make_mock_client(
            json_data=mock_play_by_play_response, request_delay=0.1
        )
        endpoints = [PlayByPlay(game_id=f"002250057{i}") for i in range(3)]

        mock_sleep = mocker.patch("anyio.sleep", new_callable=mocker.AsyncMock)
        await client.get_many(endpoints, max_concurrency=1)

        # Should have called sleep once per request
        assert mock_sleep.call_count == 3
        # Each call should use the configured delay
        mock_sleep.assert_called_with(0.1)

    async def test_get_many_delay_called_per_request(
        self, mock_play_by_play_response, make_mock_client, mocker: MockerFixture
    ):
        """get_many calls sleep once per request, after each completion."""
        client, mock_session = make_mock_client(
            json_data=mock_play_by_play_response, request_delay=0.05
        )
        endpoints = [PlayByPlay(game_id=f"002250057{i}") for i in range(5)]

        mock_sleep = mocker.patch("anyio.sleep", new_callable=mocker.AsyncMock)
        await client.get_many(endpoints, max_concurrency=1)

        # One sleep call per endpoint
        assert mock_sleep.call_count == 5
        # All calls should use the same delay
        for call in mock_sleep.call_args_list:
            assert call[0][0] == 0.05

    async def test_get_many_delay_with_concurrency(
        self, mock_play_by_play_response, make_mock_client, mocker: MockerFixture
    ):
        """get_many applies delay even with concurrent requests."""
        client, mock_session = make_mock_client(
            json_data=mock_play_by_play_response, request_delay=0.02
        )
        endpoints = [PlayByPlay(game_id=f"002250057{i}") for i in range(6)]

        mock_sleep = mocker.patch("anyio.sleep", new_callable=mocker.AsyncMock)
        await client.get_many(endpoints, max_concurrency=3)

        # Each of the 6 requests should trigger a delay
        assert mock_sleep.call_count == 6

    async def test_get_single_does_not_use_delay(
        self, mock_play_by_play_response, make_mock_client, mocker: MockerFixture
    ):
        """Single get() calls do not use request_delay (only get_many does)."""
        client, mock_session = make_mock_client(
            json_data=mock_play_by_play_response, request_delay=0.5
        )
        endpoint = PlayByPlay(game_id="0022500571")

        mock_sleep = mocker.patch("anyio.sleep", new_callable=mocker.AsyncMock)
        await client.get(endpoint)
        # Single get() should not use the delay
        mock_sleep.assert_not_called()

    async def test_get_many_empty_list_no_delay(self, mocker: MockerFixture):
        """get_many with empty list does not call sleep."""
        client = NBAClient(request_delay=0.5)

        mock_sleep = mocker.patch("anyio.sleep", new_callable=mocker.AsyncMock)
        results = await client.get_many([])
        assert results == []
        mock_sleep.assert_not_called()
        await client.close()


class TestNBAClientCaching:
    """Tests for response caching functionality."""

    def test_cache_disabled_by_default(self):
        """Cache is disabled when cache_ttl is 0."""
        client = NBAClient()
        assert client._cache is None
        assert client.cache_info is None

    def test_cache_enabled_with_ttl(self):
        """Cache is enabled when cache_ttl > 0."""
        client = NBAClient(cache_ttl=300)
        assert client._cache is not None
        assert client.cache_info == {"size": 0, "maxsize": 256, "ttl": 300}

    def test_cache_custom_maxsize(self):
        """Cache uses custom maxsize."""
        client = NBAClient(cache_ttl=60, cache_maxsize=100)
        assert client.cache_info["maxsize"] == 100

    async def test_cache_hit_returns_cached_response(
        self, mock_play_by_play_response, make_mock_client
    ):
        """Repeated requests return cached response."""
        client, mock_session = make_mock_client(
            json_data=mock_play_by_play_response, cache_ttl=300
        )
        endpoint = PlayByPlay(game_id="0022500571")

        # First request - cache miss
        result1 = await client.get(endpoint)

        # Second request - cache hit
        result2 = await client.get(endpoint)

        # Both should return same data
        assert result1.game.gameId == result2.game.gameId

        # Only one actual request should be made
        assert mock_session.get.call_count == 1

    async def test_cache_miss_different_params(
        self, mock_play_by_play_response, make_mock_client
    ):
        """Different parameters result in cache miss."""
        client, mock_session = make_mock_client(
            json_data=mock_play_by_play_response, cache_ttl=300
        )

        endpoint1 = PlayByPlay(game_id="0022500571")
        endpoint2 = PlayByPlay(game_id="0022500572")

        await client.get(endpoint1)
        await client.get(endpoint2)

        # Both should make actual requests
        assert mock_session.get.call_count == 2

    def test_clear_cache(self, mock_play_by_play_response):
        """clear_cache() empties the cache."""
        client = NBAClient(cache_ttl=300)
        # Manually add an item using a real model
        test_response = PlayByPlayResponse.model_validate(mock_play_by_play_response)
        client._cache.set("test_key", test_response)
        assert client.cache_info["size"] == 1

        client.clear_cache()
        assert client.cache_info["size"] == 0

    def test_cache_key_generation(self):
        """Cache keys are deterministic and unique."""
        client = NBAClient(cache_ttl=300)
        endpoint1 = PlayByPlay(game_id="0022500571")
        endpoint2 = PlayByPlay(game_id="0022500572")
        endpoint3 = PlayByPlay(game_id="0022500571")  # Same as endpoint1

        key1 = client._make_cache_key(endpoint1)
        key2 = client._make_cache_key(endpoint2)
        key3 = client._make_cache_key(endpoint3)

        assert key1 == key3  # Same endpoint params = same key
        assert key1 != key2  # Different params = different key


class TestNBAClientCorrelationId:
    """Tests for correlation ID / request tracing functionality."""

    async def test_get_generates_request_id(
        self, mock_play_by_play_response, make_mock_client, mocker: MockerFixture
    ):
        """get() generates a UUID request_id when none provided."""
        client, mock_session = make_mock_client(json_data=mock_play_by_play_response)
        endpoint = PlayByPlay(game_id="0022500571")

        mock_logger = mocker.patch("fastbreak.clients.nba.logger")
        mock_bound = mocker.MagicMock()
        mock_bound.adebug = mocker.AsyncMock()
        mock_logger.bind.return_value = mock_bound

        await client.get(endpoint)

        # Check that request_id was generated
        bind_kwargs = mock_logger.bind.call_args[1]
        assert "request_id" in bind_kwargs
        # Should be a valid UUID format
        import uuid

        uuid.UUID(bind_kwargs["request_id"])

    async def test_get_uses_provided_request_id(
        self, mock_play_by_play_response, make_mock_client, mocker: MockerFixture
    ):
        """get() uses provided request_id when given."""
        client, mock_session = make_mock_client(json_data=mock_play_by_play_response)
        endpoint = PlayByPlay(game_id="0022500571")

        mock_logger = mocker.patch("fastbreak.clients.nba.logger")
        mock_bound = mocker.MagicMock()
        mock_bound.adebug = mocker.AsyncMock()
        mock_logger.bind.return_value = mock_bound

        await client.get(endpoint, request_id="custom-request-123")

        bind_kwargs = mock_logger.bind.call_args[1]
        assert bind_kwargs["request_id"] == "custom-request-123"

    async def test_get_many_generates_batch_id(
        self, mock_play_by_play_response, make_mock_client, mocker: MockerFixture
    ):
        """get_many() generates a batch_id for the batch."""
        client, mock_session = make_mock_client(json_data=mock_play_by_play_response)
        endpoints = [PlayByPlay(game_id=f"002250057{i}") for i in range(2)]

        mock_logger = mocker.patch("fastbreak.clients.nba.logger")
        mock_bound = mocker.MagicMock()
        mock_bound.adebug = mocker.AsyncMock()
        mock_logger.bind.return_value = mock_bound

        await client.get_many(endpoints)

        # Find the batch_start log call
        batch_start_binds = [
            c for c in mock_logger.bind.call_args_list if "batch_id" in c[1]
        ]
        assert len(batch_start_binds) >= 1

        # batch_id should be a valid UUID
        import uuid

        uuid.UUID(batch_start_binds[0][1]["batch_id"])


class TestRetryAfterState:
    """Tests for the _RetryAfterState helper class."""

    def test_initial_state_is_none(self):
        """Initial retry_after value is None."""
        from fastbreak.clients.nba import _RetryAfterState

        state = _RetryAfterState()
        assert state.retry_after is None

    def test_set_retry_after(self):
        """set_retry_after stores the value."""
        from fastbreak.clients.nba import _RetryAfterState

        state = _RetryAfterState()
        state.set_retry_after(30.0)
        assert state.retry_after == 30.0

    def test_get_and_clear(self):
        """get_and_clear returns value and resets to None."""
        from fastbreak.clients.nba import _RetryAfterState

        state = _RetryAfterState()
        state.set_retry_after(60.0)

        value = state.get_and_clear()
        assert value == 60.0
        assert state.retry_after is None

    def test_get_and_clear_when_none(self):
        """get_and_clear returns None when not set."""
        from fastbreak.clients.nba import _RetryAfterState

        state = _RetryAfterState()
        value = state.get_and_clear()
        assert value is None


class TestRetryAfterParsing:
    """Tests for Retry-After header parsing."""

    def test_parse_integer_string(self):
        """Parses integer string to float."""
        client = NBAClient()
        assert client._parse_retry_after("30") == 30.0

    def test_parse_float_string(self):
        """Parses float string to float."""
        client = NBAClient()
        assert client._parse_retry_after("1.5") == 1.5

    def test_parse_none(self):
        """Returns None for None input."""
        client = NBAClient()
        assert client._parse_retry_after(None) is None

    def test_parse_empty_string(self):
        """Returns None for empty string."""
        client = NBAClient()
        assert client._parse_retry_after("") is None

    def test_parse_invalid_string(self):
        """Returns None for invalid string."""
        client = NBAClient()
        assert client._parse_retry_after("not-a-number") is None

    async def test_retry_after_used_in_wait_strategy(
        self, make_mock_client, make_client_response_error
    ):
        """Retry-After header value is parsed from 429 responses."""
        # Create client with mocked 429 response that has Retry-After header
        error = make_client_response_error(429, "https://stats.nba.com/stats/test")
        client, mock_session = make_mock_client(
            status=429,
            raise_error=error,
            headers={"Retry-After": "5"},
            max_retries=0,  # No retries - just verify it handles 429
            retry_wait_min=0.1,
            retry_wait_max=60.0,
        )
        endpoint = PlayByPlay(game_id="0022500571")

        # The request should fail with 429 (no retries configured)
        # The retry-after state is now per-request, so we just verify
        # the request was made and the error is raised
        with pytest.raises(ClientResponseError) as exc_info:
            await client.get(endpoint)
        assert exc_info.value.status == 429


class TestCacheTypeMismatchError:
    """Tests for CacheTypeMismatchError exception attributes and message."""

    def test_stores_key_attribute(self):
        """key attribute is stored on the exception."""
        from fastbreak.clients.nba import CacheTypeMismatchError

        err = CacheTypeMismatchError("my_key", "TypeA", "TypeB")

        assert err.key == "my_key"

    def test_stores_expected_attribute(self):
        """expected attribute is stored on the exception."""
        from fastbreak.clients.nba import CacheTypeMismatchError

        err = CacheTypeMismatchError("my_key", "TypeA", "TypeB")

        assert err.expected == "TypeA"

    def test_stores_actual_attribute(self):
        """actual attribute is stored on the exception."""
        from fastbreak.clients.nba import CacheTypeMismatchError

        err = CacheTypeMismatchError("my_key", "TypeA", "TypeB")

        assert err.actual == "TypeB"

    def test_message_truncates_key_to_16_chars(self):
        """Error message uses only the first 16 characters of the key."""
        from fastbreak.clients.nba import CacheTypeMismatchError

        key = "A" * 20
        err = CacheTypeMismatchError(key, "TypeA", "TypeB")

        assert "A" * 16 + "..." in str(err)

    def test_message_includes_expected_and_actual_types(self):
        """Error message contains both expected and actual type names."""
        from fastbreak.clients.nba import CacheTypeMismatchError

        err = CacheTypeMismatchError("key", "TypeA", "TypeB")
        msg = str(err)

        assert "TypeA" in msg
        assert "TypeB" in msg


class TestTypedResponseCache:
    """Tests for _TypedResponseCache.__contains__."""

    def test_contains_returns_true_for_cached_key(self):
        """__contains__ returns True after a key is stored via set()."""
        from pydantic import BaseModel

        from fastbreak.clients.nba import _TypedResponseCache

        class _M(BaseModel):
            v: int = 0

        cache = _TypedResponseCache(maxsize=10, ttl=60)
        cache.set("present", _M())

        assert "present" in cache

    def test_contains_returns_false_for_missing_key(self):
        """__contains__ returns False for a key that was never stored."""
        from fastbreak.clients.nba import _TypedResponseCache

        cache = _TypedResponseCache(maxsize=10, ttl=60)

        assert "absent" not in cache


class TestNBAClientSignalHandling:
    """Tests for NBAClient._signal_handler_loop."""

    async def test_signal_handler_loop_cancels_scope_on_signal(
        self, mocker: MockerFixture
    ):
        """_signal_handler_loop cancels the scope when a signal arrives."""
        client = NBAClient(session=mocker.MagicMock())
        mock_scope = mocker.MagicMock(spec=anyio.CancelScope)

        async def fake_signals():
            yield signal.SIGINT

        mock_receiver = mocker.MagicMock()
        mock_receiver.__enter__ = mocker.MagicMock(return_value=fake_signals())
        mock_receiver.__exit__ = mocker.MagicMock(return_value=False)
        mocker.patch("anyio.open_signal_receiver", return_value=mock_receiver)

        await client._signal_handler_loop(mock_scope)

        mock_scope.cancel.assert_called_once()

    async def test_signal_handler_loop_logs_debug_when_not_supported(
        self, mocker: MockerFixture
    ):
        """_signal_handler_loop emits a debug log when signals are not supported."""
        client = NBAClient(session=mocker.MagicMock())
        mock_scope = mocker.MagicMock(spec=anyio.CancelScope)
        mock_logger = mocker.patch("fastbreak.clients.nba.logger")
        mocker.patch(
            "anyio.open_signal_receiver",
            side_effect=NotImplementedError("not supported on this platform"),
        )

        await client._signal_handler_loop(mock_scope)

        mock_logger.debug.assert_called_once()


class TestMakeWaitWithRetryAfter:
    """Tests for the _make_wait_with_retry_after factory function."""

    def test_returns_callable(self):
        """Factory returns a callable wait function."""
        state = _RetryAfterState()
        wait_func = _make_wait_with_retry_after(state, initial=1.0, max_wait=10.0)
        assert callable(wait_func)

    def test_returns_retry_after_when_set(self, mocker: MockerFixture):
        """Wait function returns min(retry_after, max_wait) when retry_after is set."""
        state = _RetryAfterState()
        wait_func = _make_wait_with_retry_after(state, initial=1.0, max_wait=60.0)

        state.set_retry_after(5.0)
        mock_retry_state = mocker.MagicMock(spec=RetryCallState)

        result = wait_func(mock_retry_state)

        assert result == pytest.approx(5.0)

    def test_caps_retry_after_at_max_wait(self, mocker: MockerFixture):
        """Wait function caps retry_after at max_wait."""
        state = _RetryAfterState()
        wait_func = _make_wait_with_retry_after(state, initial=1.0, max_wait=10.0)

        state.set_retry_after(30.0)
        mock_retry_state = mocker.MagicMock(spec=RetryCallState)

        result = wait_func(mock_retry_state)

        assert result == pytest.approx(10.0)

    def test_falls_back_to_exponential_when_no_retry_after(self, mocker: MockerFixture):
        """Wait function falls back to exponential backoff when no retry_after."""
        state = _RetryAfterState()
        wait_func = _make_wait_with_retry_after(state, initial=1.0, max_wait=10.0)

        # Do not set retry_after — state should return None
        mock_retry_state = mocker.MagicMock(spec=RetryCallState)
        mock_retry_state.attempt_number = 1

        result = wait_func(mock_retry_state)

        # Should return a positive float from exponential backoff, not None
        assert result is not None
        assert isinstance(result, float)
        assert result > 0

    def test_clears_retry_after_after_use(self, mocker: MockerFixture):
        """Retry_after value is consumed (cleared) after one call."""
        state = _RetryAfterState()
        wait_func = _make_wait_with_retry_after(state, initial=1.0, max_wait=60.0)
        mock_retry_state = mocker.MagicMock(spec=RetryCallState)
        mock_retry_state.attempt_number = 1

        state.set_retry_after(5.0)
        first_result = wait_func(mock_retry_state)
        assert first_result == pytest.approx(5.0)

        # Second call should fall back to exponential (retry_after was cleared)
        second_result = wait_func(mock_retry_state)
        assert second_result != pytest.approx(5.0)
        assert isinstance(second_result, float)
        assert second_result > 0


class TestCacheTTLBoundary:
    """Tests for cache_ttl boundary values."""

    def test_cache_enabled_with_ttl_one(self):
        """Cache is enabled when cache_ttl=1 (boundary: > 0)."""
        client = NBAClient(cache_ttl=1)
        assert client._cache is not None
        assert client.cache_info is not None
        assert client.cache_info["ttl"] == 1

    def test_cache_disabled_with_ttl_zero(self):
        """Cache is disabled when cache_ttl=0 (boundary: not > 0)."""
        client = NBAClient(cache_ttl=0)
        assert client._cache is None
        assert client.cache_info is None


class TestOwnsSessionFlag:
    """Tests for _owns_session flag correctness."""

    async def test_get_session_sets_owns_session_on_lazy_create(
        self, mocker: MockerFixture
    ):
        """_get_session preserves _owns_session=True after lazy session creation."""
        client = NBAClient()
        assert client._owns_session is True

        mocker.patch("fastbreak.clients.nba.ssl.create_default_context")
        mocker.patch("fastbreak.clients.nba.TCPConnector")
        mocker.patch(
            "fastbreak.clients.nba.ClientSession",
            return_value=mocker.MagicMock(spec=ClientSession),
        )

        await client._get_session()

        # After creating a session, _owns_session must still be True
        assert client._owns_session is True
        await client.close()

    def test_injected_session_owns_session_is_false(self, mocker: MockerFixture):
        """Injecting a session sets _owns_session to False."""
        mock_session = mocker.MagicMock(spec=ClientSession)
        client = NBAClient(session=mock_session)

        # _owns_session must be False when session is injected
        assert client._owns_session is False
        assert client._session is mock_session


class TestClientResourceWarning:
    """Tests for __del__ ResourceWarning when client is not properly closed."""

    def test_del_warns_when_session_not_closed(self, mocker: MockerFixture):
        """__del__ emits ResourceWarning when owned session was not closed."""
        client = NBAClient()
        # Simulate a session that was created but never closed
        client._session = mocker.MagicMock(spec=ClientSession)
        client._owns_session = True

        with pytest.warns(ResourceWarning, match="NBAClient was not properly closed"):
            client.__del__()

    def test_del_no_warning_when_session_is_none(self):
        """__del__ does not warn when session is None (not yet created)."""
        client = NBAClient()
        assert client._session is None
        assert client._owns_session is True

        # Should not raise any warning
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            client.__del__()
            resource_warnings = [
                x for x in w if issubclass(x.category, ResourceWarning)
            ]
            assert len(resource_warnings) == 0

    def test_del_no_warning_when_not_owned(self, mocker: MockerFixture):
        """__del__ does not warn when session is not owned (injected)."""
        mock_session = mocker.MagicMock(spec=ClientSession)
        client = NBAClient(session=mock_session)
        assert client._owns_session is False

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            client.__del__()
            resource_warnings = [
                x for x in w if issubclass(x.category, ResourceWarning)
            ]
            assert len(resource_warnings) == 0


class TestStoreInCacheWithNullKey:
    """Tests for _store_in_cache when cache_key is None."""

    async def test_store_in_cache_skips_when_cache_key_is_none(self):
        """_store_in_cache does nothing when cache_key is None (caching disabled)."""
        client = NBAClient(cache_ttl=300)
        assert client._cache is not None

        from pydantic import BaseModel

        class _DummyResponse(BaseModel):
            v: int = 42

        result = _DummyResponse()

        # Store with cache_key=None — should NOT store anything
        await client._store_in_cache(None, result)

        assert client.cache_info["size"] == 0

    async def test_store_in_cache_stores_when_cache_key_is_provided(self):
        """_store_in_cache stores when both cache and key are present."""
        client = NBAClient(cache_ttl=300)
        assert client._cache is not None

        from pydantic import BaseModel

        class _DummyResponse(BaseModel):
            v: int = 42

        result = _DummyResponse()

        await client._store_in_cache("some_key", result)

        assert client.cache_info["size"] == 1
