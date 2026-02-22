"""Structured logging for fastbreak.

Logging is configured automatically at import time, but only if structlog
hasn't already been configured by the application. This allows applications
to set up their own structlog configuration before importing fastbreak.

Logging is controlled by environment variables:

FASTBREAK_LOG_LEVEL:
- DEBUG   - Show all messages (debug, info, warning, error)
- INFO    - Show info and above
- WARNING - Show warnings and errors (default)
- ERROR   - Show only errors
- SILENT  - Suppress all logging

FASTBREAK_LOG_FORMAT:
- console - Human-readable colored output for development (default)
- json    - JSON output for production/log aggregation systems
"""

from __future__ import annotations

import logging
import os

import structlog

# Determine log level from environment
_log_level_str = os.environ.get("FASTBREAK_LOG_LEVEL", "").upper()
_log_format = os.environ.get("FASTBREAK_LOG_FORMAT", "console").lower()

# Map string levels to logging constants
_LEVEL_MAP = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "WARN": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
    "SILENT": logging.CRITICAL + 10,  # Above CRITICAL = nothing shown
}

_log_level = _LEVEL_MAP.get(_log_level_str, logging.WARNING)

# Select renderer based on format
_renderer: structlog.processors.JSONRenderer | structlog.dev.ConsoleRenderer
if _log_format == "json":
    _renderer = structlog.processors.JSONRenderer()
else:
    _renderer = structlog.dev.ConsoleRenderer()

# Only configure if the application hasn't already configured structlog
if not structlog.is_configured():
    if _log_level <= logging.CRITICAL:
        # Normal logging mode - show messages at configured level and above
        structlog.configure(
            processors=[
                structlog.contextvars.merge_contextvars,
                structlog.processors.add_log_level,
                structlog.processors.TimeStamper(fmt="iso"),
                _renderer,
            ],
            wrapper_class=structlog.make_filtering_bound_logger(_log_level),
            context_class=dict,
            logger_factory=structlog.PrintLoggerFactory(),
        )
    else:
        # Silent mode - discard all log messages by using highest standard level
        # and a logger factory that discards output
        structlog.configure(
            wrapper_class=structlog.make_filtering_bound_logger(logging.CRITICAL),
            logger_factory=structlog.ReturnLoggerFactory(),
        )

logger = structlog.get_logger("fastbreak")
