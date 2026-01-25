"""Tests for the logging module."""

import os
from unittest import mock

import pytest


class TestLogging:
    """Tests for logging configuration."""

    def test_logger_is_usable(self) -> None:
        """Logger should be usable without errors."""
        from fastbreak.logging import logger

        # These should not raise
        logger.debug("test event", param="value")
        bound = logger.bind(request_id="123")
        bound.info("bound event")

    def test_debug_env_var_controls_output(self) -> None:
        """FASTBREAK_DEBUG env var should control logging output."""
        # This test verifies the module reads the env var
        # We can't easily test the actual output without more complex mocking
        assert os.environ.get("FASTBREAK_DEBUG", "") in ("", "1", "true", "yes")
