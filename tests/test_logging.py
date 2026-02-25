"""Tests for the logging module.

The logging module configures structlog at import time based on environment
variables. To test different configurations, we use subprocess to run
Python code with different environment settings.
"""

import importlib
import logging
import os
import subprocess
import sys

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

    def test_logger_bind_returns_bound_logger(self) -> None:
        """Logger.bind() should return a bound logger with context."""
        from fastbreak.logging import logger

        bound = logger.bind(user_id="123", action="test")
        # Bound logger should be usable
        bound.debug("bound debug event")
        bound.info("bound info event")
        bound.warning("bound warning event")

    def test_logger_methods_exist(self) -> None:
        """Logger should have standard logging methods."""
        from fastbreak.logging import logger

        assert hasattr(logger, "debug")
        assert hasattr(logger, "info")
        assert hasattr(logger, "warning")
        assert hasattr(logger, "error")
        assert hasattr(logger, "bind")


class TestLoggingLevelMap:
    """Tests for the log level mapping."""

    def test_level_map_contains_standard_levels(self) -> None:
        """Level map should contain all standard log levels."""
        from fastbreak.logging import _LEVEL_MAP

        assert "DEBUG" in _LEVEL_MAP
        assert "INFO" in _LEVEL_MAP
        assert "WARNING" in _LEVEL_MAP
        assert "WARN" in _LEVEL_MAP  # Alias
        assert "ERROR" in _LEVEL_MAP
        assert "CRITICAL" in _LEVEL_MAP
        assert "SILENT" in _LEVEL_MAP

    def test_level_map_values_are_correct(self) -> None:
        """Level map values should match logging constants."""
        from fastbreak.logging import _LEVEL_MAP

        assert _LEVEL_MAP["DEBUG"] == logging.DEBUG
        assert _LEVEL_MAP["INFO"] == logging.INFO
        assert _LEVEL_MAP["WARNING"] == logging.WARNING
        assert _LEVEL_MAP["WARN"] == logging.WARNING
        assert _LEVEL_MAP["ERROR"] == logging.ERROR
        assert _LEVEL_MAP["CRITICAL"] == logging.CRITICAL

    def test_silent_level_is_above_critical(self) -> None:
        """SILENT level should be above CRITICAL to suppress all output."""
        from fastbreak.logging import _LEVEL_MAP

        assert _LEVEL_MAP["SILENT"] > logging.CRITICAL


class TestLoggingEnvironmentVariables:
    """Tests for environment variable configuration.

    These tests use subprocess to test different environment configurations
    since the logging module configures itself at import time.
    """

    def _run_logging_test(
        self, env_vars: dict, code: str
    ) -> subprocess.CompletedProcess:
        """Run Python code with specific environment variables."""
        import os

        env = os.environ.copy()
        # Clear any existing fastbreak logging vars
        env.pop("FASTBREAK_LOG_LEVEL", None)
        # Set the test vars
        env.update(env_vars)

        return subprocess.run(
            [sys.executable, "-c", code],
            env=env,
            capture_output=True,
            text=True,
            timeout=10,
        )

    def test_default_level_is_warning(self) -> None:
        """Default log level should be WARNING when no env vars are set."""
        code = """
import logging
from fastbreak.logging import _log_level
assert _log_level == logging.WARNING, f"Expected WARNING, got {_log_level}"
print("OK")
"""
        result = self._run_logging_test({}, code)
        assert result.returncode == 0, f"Test failed: {result.stderr}"
        assert "OK" in result.stdout

    def test_log_level_debug(self) -> None:
        """FASTBREAK_LOG_LEVEL=DEBUG should set DEBUG level."""
        code = """
import logging
from fastbreak.logging import _log_level
assert _log_level == logging.DEBUG, f"Expected DEBUG, got {_log_level}"
print("OK")
"""
        result = self._run_logging_test({"FASTBREAK_LOG_LEVEL": "DEBUG"}, code)
        assert result.returncode == 0, f"Test failed: {result.stderr}"
        assert "OK" in result.stdout

    def test_log_level_info(self) -> None:
        """FASTBREAK_LOG_LEVEL=INFO should set INFO level."""
        code = """
import logging
from fastbreak.logging import _log_level
assert _log_level == logging.INFO, f"Expected INFO, got {_log_level}"
print("OK")
"""
        result = self._run_logging_test({"FASTBREAK_LOG_LEVEL": "INFO"}, code)
        assert result.returncode == 0, f"Test failed: {result.stderr}"
        assert "OK" in result.stdout

    def test_log_level_warning(self) -> None:
        """FASTBREAK_LOG_LEVEL=WARNING should set WARNING level."""
        code = """
import logging
from fastbreak.logging import _log_level
assert _log_level == logging.WARNING, f"Expected WARNING, got {_log_level}"
print("OK")
"""
        result = self._run_logging_test({"FASTBREAK_LOG_LEVEL": "WARNING"}, code)
        assert result.returncode == 0, f"Test failed: {result.stderr}"
        assert "OK" in result.stdout

    def test_log_level_error(self) -> None:
        """FASTBREAK_LOG_LEVEL=ERROR should set ERROR level."""
        code = """
import logging
from fastbreak.logging import _log_level
assert _log_level == logging.ERROR, f"Expected ERROR, got {_log_level}"
print("OK")
"""
        result = self._run_logging_test({"FASTBREAK_LOG_LEVEL": "ERROR"}, code)
        assert result.returncode == 0, f"Test failed: {result.stderr}"
        assert "OK" in result.stdout

    def test_log_level_silent(self) -> None:
        """FASTBREAK_LOG_LEVEL=SILENT should suppress all output."""
        code = """
import logging
from fastbreak.logging import _log_level, _LEVEL_MAP
assert _log_level == _LEVEL_MAP["SILENT"], f"Expected SILENT level, got {_log_level}"
assert _log_level > logging.CRITICAL, "SILENT should be above CRITICAL"
print("OK")
"""
        result = self._run_logging_test({"FASTBREAK_LOG_LEVEL": "SILENT"}, code)
        assert result.returncode == 0, f"Test failed: {result.stderr}"
        assert "OK" in result.stdout

    def test_log_level_case_insensitive(self) -> None:
        """Log level should be case insensitive."""
        code = """
import logging
from fastbreak.logging import _log_level
assert _log_level == logging.DEBUG, f"Expected DEBUG, got {_log_level}"
print("OK")
"""
        # Test lowercase
        result = self._run_logging_test({"FASTBREAK_LOG_LEVEL": "debug"}, code)
        assert result.returncode == 0, f"Test failed: {result.stderr}"
        assert "OK" in result.stdout

    def test_invalid_log_level_defaults_to_warning(self) -> None:
        """Invalid log level should default to WARNING."""
        code = """
import logging
from fastbreak.logging import _log_level
assert _log_level == logging.WARNING, f"Expected WARNING (default), got {_log_level}"
print("OK")
"""
        result = self._run_logging_test({"FASTBREAK_LOG_LEVEL": "INVALID"}, code)
        assert result.returncode == 0, f"Test failed: {result.stderr}"
        assert "OK" in result.stdout

    def test_warn_alias_works(self) -> None:
        """WARN should work as alias for WARNING."""
        code = """
import logging
from fastbreak.logging import _log_level
assert _log_level == logging.WARNING, f"Expected WARNING, got {_log_level}"
print("OK")
"""
        result = self._run_logging_test({"FASTBREAK_LOG_LEVEL": "WARN"}, code)
        assert result.returncode == 0, f"Test failed: {result.stderr}"
        assert "OK" in result.stdout


class TestLoggingOutput:
    """Tests for actual logging output behavior."""

    def _run_logging_output_test(
        self, env_vars: dict, log_level: str
    ) -> subprocess.CompletedProcess:
        """Run code that produces log output and capture it."""
        code = f"""
from fastbreak.logging import logger
logger.{log_level}("test_message", key="value")
"""
        import os

        env = os.environ.copy()
        env.pop("FASTBREAK_LOG_LEVEL", None)
        env.update(env_vars)

        return subprocess.run(
            [sys.executable, "-c", code],
            env=env,
            capture_output=True,
            text=True,
            timeout=10,
        )

    def test_debug_message_shown_at_debug_level(self) -> None:
        """Debug messages should be shown when level is DEBUG."""
        result = self._run_logging_output_test(
            {"FASTBREAK_LOG_LEVEL": "DEBUG"}, "debug"
        )
        assert result.returncode == 0
        # Debug message should appear in stderr (structlog output)
        assert "test_message" in result.stderr or "test_message" in result.stdout

    def test_debug_message_hidden_at_warning_level(self) -> None:
        """Debug messages should be hidden when level is WARNING."""
        result = self._run_logging_output_test(
            {"FASTBREAK_LOG_LEVEL": "WARNING"}, "debug"
        )
        assert result.returncode == 0
        # Debug message should NOT appear
        assert "test_message" not in result.stderr
        assert "test_message" not in result.stdout

    def test_warning_message_shown_at_warning_level(self) -> None:
        """Warning messages should be shown when level is WARNING."""
        result = self._run_logging_output_test(
            {"FASTBREAK_LOG_LEVEL": "WARNING"}, "warning"
        )
        assert result.returncode == 0
        # Warning message should appear
        assert "test_message" in result.stderr or "test_message" in result.stdout

    def test_warning_message_hidden_at_error_level(self) -> None:
        """Warning messages should be hidden when level is ERROR."""
        result = self._run_logging_output_test(
            {"FASTBREAK_LOG_LEVEL": "ERROR"}, "warning"
        )
        assert result.returncode == 0
        # Warning message should NOT appear
        assert "test_message" not in result.stderr
        assert "test_message" not in result.stdout

    def test_error_message_shown_at_error_level(self) -> None:
        """Error messages should be shown when level is ERROR."""
        result = self._run_logging_output_test(
            {"FASTBREAK_LOG_LEVEL": "ERROR"}, "error"
        )
        assert result.returncode == 0
        # Error message should appear
        assert "test_message" in result.stderr or "test_message" in result.stdout

    def test_silent_suppresses_all_messages(self) -> None:
        """SILENT level should suppress all messages including errors."""
        result = self._run_logging_output_test(
            {"FASTBREAK_LOG_LEVEL": "SILENT"}, "error"
        )
        assert result.returncode == 0
        # No messages should appear
        assert "test_message" not in result.stderr
        assert "test_message" not in result.stdout

    def test_info_message_shown_at_info_level(self) -> None:
        """Info messages should be shown when level is INFO."""
        result = self._run_logging_output_test({"FASTBREAK_LOG_LEVEL": "INFO"}, "info")
        assert result.returncode == 0
        # Info message should appear
        assert "test_message" in result.stderr or "test_message" in result.stdout

    def test_info_message_hidden_at_warning_level(self) -> None:
        """Info messages should be hidden when level is WARNING."""
        result = self._run_logging_output_test(
            {"FASTBREAK_LOG_LEVEL": "WARNING"}, "info"
        )
        assert result.returncode == 0
        # Info message should NOT appear
        assert "test_message" not in result.stderr
        assert "test_message" not in result.stdout


class TestLoggingModuleReload:
    """Tests that reload the logging module to cover import-time branches.

    These tests use importlib.reload() to reload the logging module
    with different environment variables set, allowing coverage to be
    collected on import-time configuration code.
    """

    @pytest.fixture(autouse=True)
    def cleanup_env(self):
        """Clean up environment variables after each test."""
        original_log_level = os.environ.get("FASTBREAK_LOG_LEVEL")
        yield
        # Restore original values
        if original_log_level is not None:
            os.environ["FASTBREAK_LOG_LEVEL"] = original_log_level
        else:
            os.environ.pop("FASTBREAK_LOG_LEVEL", None)

    def test_reload_with_log_level_info(self) -> None:
        """Reload module with FASTBREAK_LOG_LEVEL=INFO to cover level map branch."""
        import fastbreak.logging as log_module

        os.environ["FASTBREAK_LOG_LEVEL"] = "INFO"

        importlib.reload(log_module)

        assert log_module._log_level == logging.INFO

    def test_reload_with_silent_mode(self) -> None:
        """Reload module with FASTBREAK_LOG_LEVEL=SILENT to cover silent branch."""
        import fastbreak.logging as log_module

        os.environ["FASTBREAK_LOG_LEVEL"] = "SILENT"

        importlib.reload(log_module)

        assert log_module._log_level > logging.CRITICAL
