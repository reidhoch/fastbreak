import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import certifi
import pytest
from aiohttp import ClientResponseError, ClientSession, ClientTimeout
from pydantic import ValidationError
from tenacity import wait_exponential_jitter

from fastbreak.clients.nba import (
    BATCH_PROGRESS_THRESHOLD,
    HTTP_SERVER_ERROR_MIN,
    HTTP_TOO_MANY_REQUESTS,
    NBAClient,
    _is_retryable_error,
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
        """Default max_retries is 3 (4 total attempts)."""
        client = NBAClient()
        # stop_after_attempt(max_retries + 1) = stop_after_attempt(4)
        assert client._retry.stop.max_attempt_number == 4

    def test_custom_max_retries(self):
        """Custom max_retries is respected."""
        client = NBAClient(max_retries=5)
        assert client._retry.stop.max_attempt_number == 6

    def test_default_retry_wait_strategy(self):
        """Default wait strategy uses correct min/max values."""
        client = NBAClient()
        wait_strategy = client._retry.wait
        # Verify it's an exponential jitter strategy
        assert isinstance(wait_strategy, wait_exponential_jitter)
        # Verify initial (min) is 1.0
        assert wait_strategy.initial == 1.0
        # Verify max is 10.0
        assert wait_strategy.max == 10.0

    def test_custom_retry_wait_min(self):
        """Custom retry_wait_min is applied to wait strategy."""
        client = NBAClient(retry_wait_min=2.5)
        assert client._retry.wait.initial == 2.5

    def test_custom_retry_wait_max(self):
        """Custom retry_wait_max is applied to wait strategy."""
        client = NBAClient(retry_wait_max=30.0)
        assert client._retry.wait.max == 30.0

    def test_custom_retry_wait_both(self):
        """Custom retry_wait_min and max are both applied."""
        client = NBAClient(retry_wait_min=0.5, retry_wait_max=5.0)
        assert client._retry.wait.initial == 0.5
        assert client._retry.wait.max == 5.0

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


class TestNBAClientGetSession:
    """Tests for _get_session method."""

    @pytest.mark.asyncio
    async def test_creates_ssl_context_with_certifi(self):
        """_get_session creates SSL context using certifi CA bundle."""
        client = NBAClient()

        with (
            patch("fastbreak.clients.nba.ssl.create_default_context") as mock_ssl,
            patch("fastbreak.clients.nba.TCPConnector") as mock_connector_cls,
            patch("fastbreak.clients.nba.ClientSession") as mock_session_cls,
        ):
            mock_ssl.return_value = MagicMock()
            mock_connector_cls.return_value = MagicMock()
            mock_session_cls.return_value = MagicMock(spec=ClientSession)

            await client._get_session()

            mock_ssl.assert_called_once_with(cafile=certifi.where())

        await client.close()

    @pytest.mark.asyncio
    async def test_creates_connector_with_correct_params(self):
        """_get_session creates TCPConnector with correct parameters."""
        client = NBAClient()

        with (
            patch("fastbreak.clients.nba.ssl.create_default_context") as mock_ssl,
            patch("fastbreak.clients.nba.TCPConnector") as mock_connector_cls,
            patch("fastbreak.clients.nba.ClientSession") as mock_session_cls,
        ):
            mock_ssl_ctx = MagicMock()
            mock_ssl.return_value = mock_ssl_ctx
            mock_connector = MagicMock()
            mock_connector_cls.return_value = mock_connector
            mock_session_cls.return_value = MagicMock(spec=ClientSession)

            await client._get_session()

            mock_connector_cls.assert_called_once_with(
                limit_per_host=10,
                ssl=mock_ssl_ctx,
                ttl_dns_cache=300,
            )

        await client.close()

    @pytest.mark.asyncio
    async def test_creates_session_with_correct_params(self):
        """_get_session creates ClientSession with correct parameters."""
        client = NBAClient()

        with (
            patch("fastbreak.clients.nba.ssl.create_default_context") as mock_ssl,
            patch("fastbreak.clients.nba.TCPConnector") as mock_connector_cls,
            patch("fastbreak.clients.nba.ClientSession") as mock_session_cls,
        ):
            mock_ssl.return_value = MagicMock()
            mock_connector = MagicMock()
            mock_connector_cls.return_value = mock_connector
            mock_session = MagicMock(spec=ClientSession)
            mock_session_cls.return_value = mock_session

            result = await client._get_session()

            mock_session_cls.assert_called_once_with(
                connector=mock_connector,
                headers=NBAClient.DEFAULT_HEADERS,
                timeout=client._timeout,
            )
            assert result is mock_session

        await client.close()

    @pytest.mark.asyncio
    async def test_reuses_existing_session(self):
        """_get_session returns existing session if present."""
        mock_session = MagicMock(spec=ClientSession)
        client = NBAClient(session=mock_session)

        session = await client._get_session()

        assert session is mock_session

    @pytest.mark.asyncio
    async def test_session_created_only_once(self):
        """_get_session only creates session on first call."""
        client = NBAClient()

        with (
            patch("fastbreak.clients.nba.ssl.create_default_context"),
            patch("fastbreak.clients.nba.TCPConnector"),
            patch("fastbreak.clients.nba.ClientSession") as mock_session_cls,
        ):
            mock_session = MagicMock(spec=ClientSession)
            mock_session_cls.return_value = mock_session

            session1 = await client._get_session()
            session2 = await client._get_session()

            assert session1 is session2
            assert mock_session_cls.call_count == 1

        await client.close()


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


class TestNBAClientClose:
    """Tests for close method."""

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

    @pytest.mark.asyncio
    async def test_close_does_not_close_external_session(self):
        """close() doesn't close externally provided session."""
        external_session = MagicMock(spec=ClientSession)
        external_session.close = AsyncMock()
        client = NBAClient(session=external_session)

        await client.close()

        external_session.close.assert_not_called()


# Helper to create mock HTTP responses
def _make_mock_response(
    status: int = 200,
    json_data: dict | None = None,
    raise_error: Exception | None = None,
    headers: dict | None = None,
):
    """Create a mock aiohttp response for testing."""
    from multidict import CIMultiDict, CIMultiDictProxy

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
    return response


class TestNBAClientGet:
    """Tests for the get method."""

    @pytest.mark.asyncio
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

    @pytest.mark.asyncio
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

    @pytest.mark.asyncio
    async def test_get_logs_request_attempt(
        self, mock_play_by_play_response, make_mock_client
    ):
        """get() logs request attempt with correct parameters."""
        client, mock_session = make_mock_client(json_data=mock_play_by_play_response)
        endpoint = PlayByPlay(game_id="0022500571")

        with patch("fastbreak.clients.nba.logger") as mock_logger:
            mock_bound = MagicMock()
            mock_bound.adebug = AsyncMock()
            mock_logger.bind.return_value = mock_bound

            await client.get(endpoint)

            # Verify logger.bind was called with endpoint path
            mock_logger.bind.assert_called_with(endpoint="playbyplayv3")

            # Verify request_attempt log was called with all params
            request_log_calls = [
                c
                for c in mock_bound.adebug.call_args_list
                if c[0][0] == "request_attempt"
            ]
            assert len(request_log_calls) == 1
            call_kwargs = request_log_calls[0][1]
            assert call_kwargs["attempt"] == 1
            assert call_kwargs["url"] == "https://stats.nba.com/stats/playbyplayv3"
            assert call_kwargs["params"] == endpoint.params()

    @pytest.mark.asyncio
    async def test_get_logs_success(self, mock_play_by_play_response, make_mock_client):
        """get() logs success with attempt number."""
        client, mock_session = make_mock_client(json_data=mock_play_by_play_response)
        endpoint = PlayByPlay(game_id="0022500571")

        with patch("fastbreak.clients.nba.logger") as mock_logger:
            mock_bound = MagicMock()
            mock_bound.adebug = AsyncMock()
            mock_logger.bind.return_value = mock_bound

            await client.get(endpoint)

            # Verify success log was called
            success_calls = [
                c
                for c in mock_bound.adebug.call_args_list
                if c[0][0] == "request_success"
            ]
            assert len(success_calls) == 1
            assert success_calls[0][1]["attempt"] == 1

    @pytest.mark.asyncio
    async def test_get_logs_rate_limited_on_429(
        self, make_client_response_error, make_mock_client
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

        with patch("fastbreak.clients.nba.logger") as mock_logger:
            mock_bound = MagicMock()
            mock_bound.adebug = AsyncMock()
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
            assert call_kwargs["retry_after"] == "30"
            assert call_kwargs["attempt"] == 1

    @pytest.mark.asyncio
    async def test_get_logs_validation_failed(self, make_mock_client):
        """get() logs validation_failed and re-raises ValidationError with context."""
        client, mock_session = make_mock_client(json_data={"invalid": "data"})
        endpoint = PlayByPlay(game_id="0022500571")

        with patch("fastbreak.clients.nba.logger") as mock_logger:
            mock_bound = MagicMock()
            mock_bound.adebug = AsyncMock()
            mock_bound.awarning = AsyncMock()
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

    @pytest.mark.asyncio
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

    @pytest.mark.asyncio
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

    @pytest.mark.asyncio
    async def test_get_validation_error_log_includes_response_keys(
        self, make_mock_client
    ):
        """Logged validation error should include response keys for debugging."""
        # Response with unexpected structure
        client, mock_session = make_mock_client(
            json_data={"unexpected_key1": "value1", "unexpected_key2": "value2"}
        )
        endpoint = PlayByPlay(game_id="0022500571")

        with patch("fastbreak.clients.nba.logger") as mock_logger:
            mock_bound = MagicMock()
            mock_bound.adebug = AsyncMock()
            mock_bound.awarning = AsyncMock()
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

    @pytest.mark.asyncio
    async def test_get_rate_limited_not_logged_for_non_429(
        self, mock_play_by_play_response, make_mock_client
    ):
        """get() only logs rate_limited for 429 status, not other statuses."""
        client, mock_session = make_mock_client(json_data=mock_play_by_play_response)
        endpoint = PlayByPlay(game_id="0022500571")

        with patch("fastbreak.clients.nba.logger") as mock_logger:
            mock_bound = MagicMock()
            mock_bound.adebug = AsyncMock()
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
    def mock_success_response(self, mock_play_by_play_response):
        """Create a successful mock response."""
        return _make_mock_response(json_data=mock_play_by_play_response)

    @pytest.mark.asyncio
    async def test_retries_on_429(
        self,
        mock_success_response,
        make_client_response_error,
        mock_play_by_play_response,
    ):
        """Retry on 429 rate limit error."""
        call_count = 0

        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                error = make_client_response_error(429)
                return _make_mock_response(status=429, raise_error=error)
            return mock_success_response

        mock_session = MagicMock(spec=ClientSession)
        mock_session.get = MagicMock(side_effect=side_effect)

        client = NBAClient(
            session=mock_session, retry_wait_min=0.01, retry_wait_max=0.02
        )
        endpoint = PlayByPlay(game_id="0022500571")

        result = await client.get(endpoint)

        assert call_count == 3
        assert isinstance(result, PlayByPlayResponse)

    @pytest.mark.asyncio
    async def test_retries_on_500(
        self,
        mock_success_response,
        make_client_response_error,
        mock_play_by_play_response,
    ):
        """Retry on 500 server error."""
        call_count = 0

        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                error = make_client_response_error(500)
                return _make_mock_response(status=500, raise_error=error)
            return mock_success_response

        mock_session = MagicMock(spec=ClientSession)
        mock_session.get = MagicMock(side_effect=side_effect)

        client = NBAClient(
            session=mock_session, retry_wait_min=0.01, retry_wait_max=0.02
        )
        endpoint = PlayByPlay(game_id="0022500571")

        result = await client.get(endpoint)

        assert call_count == 2
        assert isinstance(result, PlayByPlayResponse)

    @pytest.mark.asyncio
    async def test_retries_on_timeout(
        self, mock_success_response, mock_play_by_play_response
    ):
        """Retry on timeout error."""
        call_count = 0

        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                error_response = AsyncMock()
                error_response.__aenter__ = AsyncMock(
                    side_effect=TimeoutError("Connection timed out")
                )
                error_response.__aexit__ = AsyncMock(return_value=None)
                return error_response
            return mock_success_response

        mock_session = MagicMock(spec=ClientSession)
        mock_session.get = MagicMock(side_effect=side_effect)

        client = NBAClient(
            session=mock_session, retry_wait_min=0.01, retry_wait_max=0.02
        )
        endpoint = PlayByPlay(game_id="0022500571")

        result = await client.get(endpoint)

        assert call_count == 2
        assert isinstance(result, PlayByPlayResponse)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "status",
        [
            pytest.param(401, id="401_unauthorized"),
            pytest.param(403, id="403_forbidden"),
            pytest.param(404, id="404_not_found"),
        ],
    )
    async def test_no_retry_on_client_errors(self, make_client_response_error, status):
        """Client errors (4xx except 429) do not trigger retry."""
        error = make_client_response_error(status)
        mock_response = _make_mock_response(status=status, raise_error=error)
        mock_session = MagicMock(spec=ClientSession)
        mock_session.get = MagicMock(return_value=mock_response)

        client = NBAClient(
            session=mock_session, retry_wait_min=0.01, retry_wait_max=0.02
        )
        endpoint = PlayByPlay(game_id="0022500571")

        with pytest.raises(ClientResponseError) as exc_info:
            await client.get(endpoint)

        assert exc_info.value.status == status
        assert mock_session.get.call_count == 1

    @pytest.mark.asyncio
    async def test_exhausted_retries_raises(self, make_client_response_error):
        """Exception raised after max retries exhausted."""
        error = make_client_response_error(429)
        mock_response = _make_mock_response(status=429, raise_error=error)
        mock_session = MagicMock(spec=ClientSession)
        mock_session.get = MagicMock(return_value=mock_response)

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

        # Verify the retry config was built with correct stop condition
        # stop_after_attempt(6) since max_retries=5 means 6 total attempts
        assert client._retry.stop.max_attempt_number == 6


class TestNBAClientGetMany:
    """Tests for the get_many batch fetch method."""

    @pytest.mark.asyncio
    async def test_get_many_returns_ordered_results(
        self, mock_play_by_play_response, make_mock_client
    ):
        """get_many returns results in same order as input."""
        client, mock_session = make_mock_client(json_data=mock_play_by_play_response)
        endpoints = [PlayByPlay(game_id=f"002250057{i}") for i in range(3)]

        results = await client.get_many(endpoints)

        assert len(results) == 3
        assert all(isinstance(r, PlayByPlayResponse) for r in results)

    @pytest.mark.asyncio
    async def test_get_many_empty_list(self):
        """get_many with empty list returns empty list."""
        client = NBAClient()
        results = await client.get_many([])
        assert results == []
        await client.close()

    @pytest.mark.asyncio
    async def test_get_many_default_concurrency(
        self, mock_play_by_play_response, make_mock_client
    ):
        """get_many defaults to concurrency of 3."""
        client, mock_session = make_mock_client(json_data=mock_play_by_play_response)
        endpoints = [PlayByPlay(game_id="0022500571")]

        with patch("fastbreak.clients.nba.logger") as mock_logger:
            mock_bound = MagicMock()
            mock_bound.adebug = AsyncMock()
            mock_logger.bind.return_value = mock_bound

            await client.get_many(endpoints)

            # Verify logger.bind was called with concurrency=3 (the default)
            bind_calls = [
                c for c in mock_logger.bind.call_args_list if "concurrency" in c[1]
            ]
            assert len(bind_calls) == 1
            assert bind_calls[0][1]["concurrency"] == 3

    @pytest.mark.asyncio
    async def test_get_many_custom_concurrency(
        self, mock_play_by_play_response, make_mock_client
    ):
        """get_many respects custom max_concurrency."""
        client, mock_session = make_mock_client(json_data=mock_play_by_play_response)
        endpoints = [PlayByPlay(game_id="0022500571")]

        with patch("fastbreak.clients.nba.logger") as mock_logger:
            mock_bound = MagicMock()
            mock_bound.adebug = AsyncMock()
            mock_logger.bind.return_value = mock_bound

            await client.get_many(endpoints, max_concurrency=5)

            # Verify logger.bind was called with concurrency=5
            bind_calls = [
                c for c in mock_logger.bind.call_args_list if "concurrency" in c[1]
            ]
            assert len(bind_calls) == 1
            assert bind_calls[0][1]["concurrency"] == 5

    @pytest.mark.asyncio
    async def test_get_many_logs_batch_start(
        self, mock_play_by_play_response, make_mock_client
    ):
        """get_many logs batch_start with total count."""
        client, mock_session = make_mock_client(json_data=mock_play_by_play_response)
        endpoints = [PlayByPlay(game_id=f"002250057{i}") for i in range(3)]

        with patch("fastbreak.clients.nba.logger") as mock_logger:
            mock_bound = MagicMock()
            mock_bound.adebug = AsyncMock()
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

    @pytest.mark.asyncio
    async def test_get_many_logs_batch_complete(
        self, mock_play_by_play_response, make_mock_client
    ):
        """get_many logs batch_complete with total count."""
        client, mock_session = make_mock_client(json_data=mock_play_by_play_response)
        endpoints = [PlayByPlay(game_id=f"002250057{i}") for i in range(3)]

        with patch("fastbreak.clients.nba.logger") as mock_logger:
            mock_bound = MagicMock()
            mock_bound.adebug = AsyncMock()
            mock_logger.bind.return_value = mock_bound

            await client.get_many(endpoints)

            # Verify batch_complete was logged with total
            complete_calls = [
                c
                for c in mock_bound.adebug.call_args_list
                if c[0][0] == "batch_complete"
            ]
            assert len(complete_calls) == 1
            assert complete_calls[0][1]["total"] == 3

    @pytest.mark.asyncio
    async def test_get_many_logs_batch_progress_for_large_batches(
        self, mock_play_by_play_response, make_mock_client
    ):
        """get_many logs batch_progress for batches >= BATCH_PROGRESS_THRESHOLD."""
        client, mock_session = make_mock_client(json_data=mock_play_by_play_response)
        # Create enough endpoints to trigger progress logging
        endpoints = [
            PlayByPlay(game_id=f"00225005{i:02d}")
            for i in range(BATCH_PROGRESS_THRESHOLD)
        ]

        with patch("fastbreak.clients.nba.logger") as mock_logger:
            mock_bound = MagicMock()
            mock_bound.adebug = AsyncMock()
            mock_logger.bind.return_value = mock_bound

            await client.get_many(endpoints, max_concurrency=1)

            # Verify batch_progress was logged at least once
            progress_calls = [
                c
                for c in mock_bound.adebug.call_args_list
                if c[0][0] == "batch_progress"
            ]
            assert len(progress_calls) >= 1
            # Verify completed and total were passed
            for call in progress_calls:
                assert "completed" in call[1]
                assert "total" in call[1]

    @pytest.mark.asyncio
    async def test_get_many_no_progress_for_small_batches(
        self, mock_play_by_play_response, make_mock_client
    ):
        """get_many doesn't log batch_progress for batches < BATCH_PROGRESS_THRESHOLD."""
        client, mock_session = make_mock_client(json_data=mock_play_by_play_response)
        # Create fewer endpoints than threshold
        endpoints = [PlayByPlay(game_id=f"002250057{i}") for i in range(3)]

        with patch("fastbreak.clients.nba.logger") as mock_logger:
            mock_bound = MagicMock()
            mock_bound.adebug = AsyncMock()
            mock_logger.bind.return_value = mock_bound

            await client.get_many(endpoints)

            # Verify batch_progress was NOT logged
            progress_calls = [
                c
                for c in mock_bound.adebug.call_args_list
                if c[0][0] == "batch_progress"
            ]
            assert len(progress_calls) == 0

    @pytest.mark.asyncio
    async def test_get_many_respects_concurrency_limit(
        self, mock_play_by_play_response
    ):
        """get_many limits concurrent requests via semaphore."""
        concurrent_count = 0
        max_concurrent = 0
        lock = asyncio.Lock()

        async def mock_aenter(self):
            nonlocal concurrent_count, max_concurrent
            async with lock:
                concurrent_count += 1
                max_concurrent = max(max_concurrent, concurrent_count)
            await asyncio.sleep(0.01)  # Simulate network delay
            return self

        async def mock_aexit(self, *args):
            nonlocal concurrent_count
            async with lock:
                concurrent_count -= 1

        def create_mock_response():
            response = AsyncMock()
            response.status = 200
            response.raise_for_status = MagicMock()
            response.json = AsyncMock(return_value=mock_play_by_play_response)
            response.__aenter__ = lambda s: mock_aenter(s)
            response.__aexit__ = lambda s, *args: mock_aexit(s, *args)
            return response

        mock_session = MagicMock(spec=ClientSession)
        mock_session.get = MagicMock(side_effect=lambda *a, **k: create_mock_response())

        client = NBAClient(session=mock_session)
        endpoints = [PlayByPlay(game_id=f"002250057{i}") for i in range(10)]

        await client.get_many(endpoints, max_concurrency=3)

        assert max_concurrent <= 3

    @pytest.mark.asyncio
    async def test_get_many_raises_exception_group_on_error(
        self, make_client_response_error, mock_play_by_play_response
    ):
        """get_many raises ExceptionGroup when any request fails."""
        call_count = 0

        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                error = make_client_response_error(404)
                return _make_mock_response(status=404, raise_error=error)
            return _make_mock_response(json_data=mock_play_by_play_response)

        mock_session = MagicMock(spec=ClientSession)
        mock_session.get = MagicMock(side_effect=side_effect)

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

    @pytest.mark.asyncio
    async def test_get_many_no_delay_when_zero(
        self, mock_play_by_play_response, make_mock_client
    ):
        """get_many does not sleep when request_delay is 0."""
        client, mock_session = make_mock_client(
            json_data=mock_play_by_play_response, request_delay=0.0
        )
        endpoints = [PlayByPlay(game_id=f"002250057{i}") for i in range(3)]

        with patch(
            "fastbreak.clients.nba.asyncio.sleep", new_callable=AsyncMock
        ) as mock_sleep:
            await client.get_many(endpoints)
            # Should not have called sleep since delay is 0
            mock_sleep.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_many_applies_request_delay(
        self, mock_play_by_play_response, make_mock_client
    ):
        """get_many sleeps between requests when request_delay > 0."""
        client, mock_session = make_mock_client(
            json_data=mock_play_by_play_response, request_delay=0.1
        )
        endpoints = [PlayByPlay(game_id=f"002250057{i}") for i in range(3)]

        with patch(
            "fastbreak.clients.nba.asyncio.sleep", new_callable=AsyncMock
        ) as mock_sleep:
            await client.get_many(endpoints, max_concurrency=1)

            # Should have called sleep once per request
            assert mock_sleep.call_count == 3
            # Each call should use the configured delay
            mock_sleep.assert_called_with(0.1)

    @pytest.mark.asyncio
    async def test_get_many_delay_called_per_request(
        self, mock_play_by_play_response, make_mock_client
    ):
        """get_many calls sleep before each request, not just between them."""
        client, mock_session = make_mock_client(
            json_data=mock_play_by_play_response, request_delay=0.05
        )
        endpoints = [PlayByPlay(game_id=f"002250057{i}") for i in range(5)]

        with patch(
            "fastbreak.clients.nba.asyncio.sleep", new_callable=AsyncMock
        ) as mock_sleep:
            await client.get_many(endpoints, max_concurrency=1)

            # One sleep call per endpoint
            assert mock_sleep.call_count == 5
            # All calls should use the same delay
            for call in mock_sleep.call_args_list:
                assert call[0][0] == 0.05

    @pytest.mark.asyncio
    async def test_get_many_delay_with_concurrency(
        self, mock_play_by_play_response, make_mock_client
    ):
        """get_many applies delay even with concurrent requests."""
        client, mock_session = make_mock_client(
            json_data=mock_play_by_play_response, request_delay=0.02
        )
        endpoints = [PlayByPlay(game_id=f"002250057{i}") for i in range(6)]

        with patch(
            "fastbreak.clients.nba.asyncio.sleep", new_callable=AsyncMock
        ) as mock_sleep:
            await client.get_many(endpoints, max_concurrency=3)

            # Each of the 6 requests should trigger a delay
            assert mock_sleep.call_count == 6

    @pytest.mark.asyncio
    async def test_get_single_does_not_use_delay(
        self, mock_play_by_play_response, make_mock_client
    ):
        """Single get() calls do not use request_delay (only get_many does)."""
        client, mock_session = make_mock_client(
            json_data=mock_play_by_play_response, request_delay=0.5
        )
        endpoint = PlayByPlay(game_id="0022500571")

        with patch(
            "fastbreak.clients.nba.asyncio.sleep", new_callable=AsyncMock
        ) as mock_sleep:
            await client.get(endpoint)
            # Single get() should not use the delay
            mock_sleep.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_many_empty_list_no_delay(self):
        """get_many with empty list does not call sleep."""
        client = NBAClient(request_delay=0.5)

        with patch(
            "fastbreak.clients.nba.asyncio.sleep", new_callable=AsyncMock
        ) as mock_sleep:
            results = await client.get_many([])
            assert results == []
            mock_sleep.assert_not_called()

        await client.close()
