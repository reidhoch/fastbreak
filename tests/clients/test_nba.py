import asyncio
import ssl
from unittest.mock import ANY, AsyncMock, MagicMock, call, patch

import certifi
import pytest
import structlog
from aiohttp import ClientSession, ClientTimeout, TCPConnector
from structlog.testing import capture_logs
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

    def test_retries_on_429(self):
        """429 Too Many Requests triggers retry."""
        from aiohttp import ClientResponseError, RequestInfo
        from multidict import CIMultiDict
        from yarl import URL

        request_info = RequestInfo(
            url=URL("https://test.com"),
            method="GET",
            headers=CIMultiDict(),
            real_url=URL("https://test.com"),
        )
        exc = ClientResponseError(request_info=request_info, history=(), status=429)
        assert _is_retryable_error(exc) is True

    def test_retries_on_500(self):
        """500 Server Error triggers retry."""
        from aiohttp import ClientResponseError, RequestInfo
        from multidict import CIMultiDict
        from yarl import URL

        request_info = RequestInfo(
            url=URL("https://test.com"),
            method="GET",
            headers=CIMultiDict(),
            real_url=URL("https://test.com"),
        )
        exc = ClientResponseError(request_info=request_info, history=(), status=500)
        assert _is_retryable_error(exc) is True

    def test_retries_on_503(self):
        """503 Service Unavailable triggers retry."""
        from aiohttp import ClientResponseError, RequestInfo
        from multidict import CIMultiDict
        from yarl import URL

        request_info = RequestInfo(
            url=URL("https://test.com"),
            method="GET",
            headers=CIMultiDict(),
            real_url=URL("https://test.com"),
        )
        exc = ClientResponseError(request_info=request_info, history=(), status=503)
        assert _is_retryable_error(exc) is True

    def test_no_retry_on_404(self):
        """404 Not Found does not trigger retry."""
        from aiohttp import ClientResponseError, RequestInfo
        from multidict import CIMultiDict
        from yarl import URL

        request_info = RequestInfo(
            url=URL("https://test.com"),
            method="GET",
            headers=CIMultiDict(),
            real_url=URL("https://test.com"),
        )
        exc = ClientResponseError(request_info=request_info, history=(), status=404)
        assert _is_retryable_error(exc) is False

    def test_no_retry_on_400(self):
        """400 Bad Request does not trigger retry."""
        from aiohttp import ClientResponseError, RequestInfo
        from multidict import CIMultiDict
        from yarl import URL

        request_info = RequestInfo(
            url=URL("https://test.com"),
            method="GET",
            headers=CIMultiDict(),
            real_url=URL("https://test.com"),
        )
        exc = ClientResponseError(request_info=request_info, history=(), status=400)
        assert _is_retryable_error(exc) is False

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
        assert client._timeout.total == 30

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


class TestNBAClientGet:
    """Tests for the get method."""

    @pytest.mark.asyncio
    async def test_get_returns_parsed_response(self, mock_play_by_play_response):
        """get() fetches data and returns parsed model."""
        mock_response = AsyncMock()
        mock_response.status = 200
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
        mock_response.status = 200
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
        assert call_args[1]["params"] == {
            "GameID": "0022500571",
            "EndPeriod": "0",
            "StartPeriod": "0",
        }

    @pytest.mark.asyncio
    async def test_get_logs_request_attempt(self, mock_play_by_play_response):
        """get() logs request attempt with correct parameters."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json = AsyncMock(return_value=mock_play_by_play_response)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        mock_session = MagicMock(spec=ClientSession)
        mock_session.get = MagicMock(return_value=mock_response)

        client = NBAClient(session=mock_session)
        endpoint = PlayByPlay("0022500571")

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
    async def test_get_logs_success(self, mock_play_by_play_response):
        """get() logs success with attempt number."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json = AsyncMock(return_value=mock_play_by_play_response)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        mock_session = MagicMock(spec=ClientSession)
        mock_session.get = MagicMock(return_value=mock_response)

        client = NBAClient(session=mock_session)
        endpoint = PlayByPlay("0022500571")

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
    async def test_get_logs_rate_limited_on_429(self):
        """get() logs rate_limited when receiving 429 status."""
        from aiohttp import ClientResponseError, RequestInfo
        from multidict import CIMultiDict, CIMultiDictProxy
        from yarl import URL

        mock_response = AsyncMock()
        mock_response.status = HTTP_TOO_MANY_REQUESTS
        mock_response.headers = CIMultiDictProxy(CIMultiDict({"Retry-After": "30"}))

        request_info = RequestInfo(
            url=URL("https://stats.nba.com/stats/test"),
            method="GET",
            headers=CIMultiDict(),
            real_url=URL("https://stats.nba.com/stats/test"),
        )
        error = ClientResponseError(request_info=request_info, history=(), status=429)
        mock_response.raise_for_status = MagicMock(side_effect=error)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        mock_session = MagicMock(spec=ClientSession)
        mock_session.get = MagicMock(return_value=mock_response)

        client = NBAClient(session=mock_session, max_retries=0, retry_wait_min=0.01)
        endpoint = PlayByPlay("0022500571")

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
    async def test_get_logs_validation_failed(self):
        """get() logs validation_failed when parsing fails."""
        invalid_response = {"invalid": "data"}

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json = AsyncMock(return_value=invalid_response)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        mock_session = MagicMock(spec=ClientSession)
        mock_session.get = MagicMock(return_value=mock_response)

        client = NBAClient(session=mock_session)
        endpoint = PlayByPlay("0022500571")

        with patch("fastbreak.clients.nba.logger") as mock_logger:
            mock_bound = MagicMock()
            mock_bound.adebug = AsyncMock()
            mock_logger.bind.return_value = mock_bound

            with pytest.raises(Exception):  # ValidationError
                await client.get(endpoint)

            # Verify validation_failed log was called
            validation_calls = [
                c
                for c in mock_bound.adebug.call_args_list
                if c[0][0] == "validation_failed"
            ]
            assert len(validation_calls) == 1
            call_kwargs = validation_calls[0][1]
            assert "error" in call_kwargs
            assert call_kwargs["error"] is not None  # error string should be set
            assert call_kwargs["endpoint"] == "playbyplayv3"
            assert call_kwargs["response_keys"] == ["invalid"]

    @pytest.mark.asyncio
    async def test_get_rate_limited_not_logged_for_non_429(
        self, mock_play_by_play_response
    ):
        """get() only logs rate_limited for 429 status, not other statuses."""
        mock_response = AsyncMock()
        mock_response.status = 200  # Not 429
        mock_response.raise_for_status = MagicMock()
        mock_response.json = AsyncMock(return_value=mock_play_by_play_response)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        mock_session = MagicMock(spec=ClientSession)
        mock_session.get = MagicMock(return_value=mock_response)

        client = NBAClient(session=mock_session)
        endpoint = PlayByPlay("0022500571")

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
        response = AsyncMock()
        response.status = 200
        response.raise_for_status = MagicMock()
        response.json = AsyncMock(return_value=mock_play_by_play_response)
        response.__aenter__ = AsyncMock(return_value=response)
        response.__aexit__ = AsyncMock(return_value=None)
        return response

    @pytest.fixture
    def mock_error_response(self):
        """Create a factory for error responses."""
        from aiohttp import ClientResponseError, RequestInfo
        from multidict import CIMultiDict
        from yarl import URL

        def _make_error(status: int):
            request_info = RequestInfo(
                url=URL("https://stats.nba.com/stats/test"),
                method="GET",
                headers=CIMultiDict(),
                real_url=URL("https://stats.nba.com/stats/test"),
            )
            return ClientResponseError(
                request_info=request_info,
                history=(),
                status=status,
            )

        return _make_error

    @pytest.mark.asyncio
    async def test_retries_on_429(
        self, mock_success_response, mock_error_response, mock_play_by_play_response
    ):
        """Retry on 429 rate limit error."""
        from multidict import CIMultiDict, CIMultiDictProxy

        call_count = 0

        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                error_response = AsyncMock()
                error_response.status = 429
                error_response.headers = CIMultiDictProxy(CIMultiDict())
                error_response.raise_for_status = MagicMock(
                    side_effect=mock_error_response(429)
                )
                error_response.__aenter__ = AsyncMock(return_value=error_response)
                error_response.__aexit__ = AsyncMock(return_value=None)
                return error_response
            return mock_success_response

        mock_session = MagicMock(spec=ClientSession)
        mock_session.get = MagicMock(side_effect=side_effect)

        client = NBAClient(
            session=mock_session, retry_wait_min=0.01, retry_wait_max=0.02
        )
        endpoint = PlayByPlay("0022500571")

        result = await client.get(endpoint)

        assert call_count == 3
        assert isinstance(result, PlayByPlayResponse)

    @pytest.mark.asyncio
    async def test_retries_on_500(
        self, mock_success_response, mock_error_response, mock_play_by_play_response
    ):
        """Retry on 500 server error."""
        call_count = 0

        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                error_response = AsyncMock()
                error_response.status = 500
                error_response.raise_for_status = MagicMock(
                    side_effect=mock_error_response(500)
                )
                error_response.__aenter__ = AsyncMock(return_value=error_response)
                error_response.__aexit__ = AsyncMock(return_value=None)
                return error_response
            return mock_success_response

        mock_session = MagicMock(spec=ClientSession)
        mock_session.get = MagicMock(side_effect=side_effect)

        client = NBAClient(
            session=mock_session, retry_wait_min=0.01, retry_wait_max=0.02
        )
        endpoint = PlayByPlay("0022500571")

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
        endpoint = PlayByPlay("0022500571")

        result = await client.get(endpoint)

        assert call_count == 2
        assert isinstance(result, PlayByPlayResponse)

    @pytest.mark.asyncio
    async def test_no_retry_on_404(self, mock_error_response):
        """No retry on 404 client error."""
        from aiohttp import ClientResponseError

        error_response = AsyncMock()
        error_response.status = 404
        error_response.raise_for_status = MagicMock(
            side_effect=mock_error_response(404)
        )
        error_response.__aenter__ = AsyncMock(return_value=error_response)
        error_response.__aexit__ = AsyncMock(return_value=None)

        mock_session = MagicMock(spec=ClientSession)
        mock_session.get = MagicMock(return_value=error_response)

        client = NBAClient(
            session=mock_session, retry_wait_min=0.01, retry_wait_max=0.02
        )
        endpoint = PlayByPlay("0022500571")

        with pytest.raises(ClientResponseError) as exc_info:
            await client.get(endpoint)

        assert exc_info.value.status == 404
        assert mock_session.get.call_count == 1

    @pytest.mark.asyncio
    async def test_no_retry_on_401(self, mock_error_response):
        """No retry on 401 auth error."""
        from aiohttp import ClientResponseError

        error_response = AsyncMock()
        error_response.status = 401
        error_response.raise_for_status = MagicMock(
            side_effect=mock_error_response(401)
        )
        error_response.__aenter__ = AsyncMock(return_value=error_response)
        error_response.__aexit__ = AsyncMock(return_value=None)

        mock_session = MagicMock(spec=ClientSession)
        mock_session.get = MagicMock(return_value=error_response)

        client = NBAClient(
            session=mock_session, retry_wait_min=0.01, retry_wait_max=0.02
        )
        endpoint = PlayByPlay("0022500571")

        with pytest.raises(ClientResponseError) as exc_info:
            await client.get(endpoint)

        assert exc_info.value.status == 401
        assert mock_session.get.call_count == 1

    @pytest.mark.asyncio
    async def test_exhausted_retries_raises(self, mock_error_response):
        """Exception raised after max retries exhausted."""
        from aiohttp import ClientResponseError
        from multidict import CIMultiDict, CIMultiDictProxy

        error_response = AsyncMock()
        error_response.status = 429
        error_response.headers = CIMultiDictProxy(CIMultiDict())
        error_response.raise_for_status = MagicMock(
            side_effect=mock_error_response(429)
        )
        error_response.__aenter__ = AsyncMock(return_value=error_response)
        error_response.__aexit__ = AsyncMock(return_value=None)

        mock_session = MagicMock(spec=ClientSession)
        mock_session.get = MagicMock(return_value=error_response)

        # max_retries=2 means 3 total attempts (1 initial + 2 retries)
        client = NBAClient(
            session=mock_session,
            max_retries=2,
            retry_wait_min=0.01,
            retry_wait_max=0.02,
        )
        endpoint = PlayByPlay("0022500571")

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
    async def test_get_many_returns_ordered_results(self, mock_play_by_play_response):
        """get_many returns results in same order as input."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json = AsyncMock(return_value=mock_play_by_play_response)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        mock_session = MagicMock(spec=ClientSession)
        mock_session.get = MagicMock(return_value=mock_response)

        client = NBAClient(session=mock_session)
        endpoints = [PlayByPlay(f"002250057{i}") for i in range(3)]

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
    async def test_get_many_default_concurrency(self, mock_play_by_play_response):
        """get_many defaults to concurrency of 10."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json = AsyncMock(return_value=mock_play_by_play_response)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        mock_session = MagicMock(spec=ClientSession)
        mock_session.get = MagicMock(return_value=mock_response)

        client = NBAClient(session=mock_session)
        endpoints = [PlayByPlay("0022500571")]

        with patch("fastbreak.clients.nba.logger") as mock_logger:
            mock_bound = MagicMock()
            mock_bound.adebug = AsyncMock()
            mock_logger.bind.return_value = mock_bound

            await client.get_many(endpoints)

            # Verify logger.bind was called with concurrency=10
            bind_calls = [
                c for c in mock_logger.bind.call_args_list if "concurrency" in c[1]
            ]
            assert len(bind_calls) == 1
            assert bind_calls[0][1]["concurrency"] == 10

    @pytest.mark.asyncio
    async def test_get_many_custom_concurrency(self, mock_play_by_play_response):
        """get_many respects custom max_concurrency."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json = AsyncMock(return_value=mock_play_by_play_response)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        mock_session = MagicMock(spec=ClientSession)
        mock_session.get = MagicMock(return_value=mock_response)

        client = NBAClient(session=mock_session)
        endpoints = [PlayByPlay("0022500571")]

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
    async def test_get_many_logs_batch_start(self, mock_play_by_play_response):
        """get_many logs batch_start with total count."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json = AsyncMock(return_value=mock_play_by_play_response)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        mock_session = MagicMock(spec=ClientSession)
        mock_session.get = MagicMock(return_value=mock_response)

        client = NBAClient(session=mock_session)
        endpoints = [PlayByPlay(f"002250057{i}") for i in range(3)]

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
    async def test_get_many_logs_batch_complete(self, mock_play_by_play_response):
        """get_many logs batch_complete with total count."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json = AsyncMock(return_value=mock_play_by_play_response)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        mock_session = MagicMock(spec=ClientSession)
        mock_session.get = MagicMock(return_value=mock_response)

        client = NBAClient(session=mock_session)
        endpoints = [PlayByPlay(f"002250057{i}") for i in range(3)]

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
        self, mock_play_by_play_response
    ):
        """get_many logs batch_progress for batches >= BATCH_PROGRESS_THRESHOLD."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json = AsyncMock(return_value=mock_play_by_play_response)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        mock_session = MagicMock(spec=ClientSession)
        mock_session.get = MagicMock(return_value=mock_response)

        client = NBAClient(session=mock_session)
        # Create enough endpoints to trigger progress logging
        endpoints = [
            PlayByPlay(f"00225005{i:02d}") for i in range(BATCH_PROGRESS_THRESHOLD)
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
        self, mock_play_by_play_response
    ):
        """get_many doesn't log batch_progress for batches < BATCH_PROGRESS_THRESHOLD."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json = AsyncMock(return_value=mock_play_by_play_response)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        mock_session = MagicMock(spec=ClientSession)
        mock_session.get = MagicMock(return_value=mock_response)

        client = NBAClient(session=mock_session)
        # Create fewer endpoints than threshold
        endpoints = [PlayByPlay(f"002250057{i}") for i in range(3)]

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
        endpoints = [PlayByPlay(f"002250057{i}") for i in range(10)]

        await client.get_many(endpoints, max_concurrency=3)

        assert max_concurrent <= 3

    @pytest.mark.asyncio
    async def test_get_many_raises_exception_group_on_error(
        self, mock_play_by_play_response
    ):
        """get_many raises ExceptionGroup when any request fails."""
        from aiohttp import ClientResponseError, RequestInfo
        from multidict import CIMultiDict
        from yarl import URL

        call_count = 0

        def make_error():
            request_info = RequestInfo(
                url=URL("https://stats.nba.com/stats/test"),
                method="GET",
                headers=CIMultiDict(),
                real_url=URL("https://stats.nba.com/stats/test"),
            )
            return ClientResponseError(
                request_info=request_info,
                history=(),
                status=404,
            )

        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                error_response = AsyncMock()
                error_response.status = 404
                error_response.raise_for_status = MagicMock(side_effect=make_error())
                error_response.__aenter__ = AsyncMock(return_value=error_response)
                error_response.__aexit__ = AsyncMock(return_value=None)
                return error_response
            response = AsyncMock()
            response.status = 200
            response.raise_for_status = MagicMock()
            response.json = AsyncMock(return_value=mock_play_by_play_response)
            response.__aenter__ = AsyncMock(return_value=response)
            response.__aexit__ = AsyncMock(return_value=None)
            return response

        mock_session = MagicMock(spec=ClientSession)
        mock_session.get = MagicMock(side_effect=side_effect)

        client = NBAClient(session=mock_session)
        endpoints = [PlayByPlay(f"002250057{i}") for i in range(3)]

        with pytest.raises(ExceptionGroup) as exc_info:
            await client.get_many(endpoints)

        # TaskGroup wraps exceptions in ExceptionGroup
        exceptions = exc_info.value.exceptions
        assert len(exceptions) == 1
        assert isinstance(exceptions[0], ClientResponseError)
        assert exceptions[0].status == 404
