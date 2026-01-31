"""Structured logging for fastbreak.

Logging is controlled by the FASTBREAK_LOG_LEVEL environment variable:
- FASTBREAK_LOG_LEVEL=DEBUG  - Show all messages (debug, info, warning, error)
- FASTBREAK_LOG_LEVEL=INFO   - Show info and above
- FASTBREAK_LOG_LEVEL=WARNING - Show warnings and errors (default)
- FASTBREAK_LOG_LEVEL=ERROR  - Show only errors
- FASTBREAK_LOG_LEVEL=SILENT - Suppress all logging

Legacy support: FASTBREAK_DEBUG=1 is equivalent to FASTBREAK_LOG_LEVEL=DEBUG
"""

from __future__ import annotations

import logging
import os

import structlog

# Determine log level from environment
_log_level_str = os.environ.get("FASTBREAK_LOG_LEVEL", "").upper()
_debug_enabled = os.environ.get("FASTBREAK_DEBUG", "").lower() in ("1", "true", "yes")

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

# Legacy FASTBREAK_DEBUG=1 means DEBUG level
if _debug_enabled:
    _log_level = logging.DEBUG
elif _log_level_str in _LEVEL_MAP:
    _log_level = _LEVEL_MAP[_log_level_str]
else:
    # Default: show warnings and errors so users see important diagnostics
    _log_level = logging.WARNING

if _log_level <= logging.CRITICAL:
    # Normal logging mode - show messages at configured level and above
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(_log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
    )
else:
    # Silent mode - discard all log messages
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(_log_level),
        logger_factory=structlog.ReturnLoggerFactory(),
    )

logger = structlog.get_logger("fastbreak")
