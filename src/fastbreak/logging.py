"""Structured logging for fastbreak.

Logging is controlled by the FASTBREAK_DEBUG environment variable.
Set FASTBREAK_DEBUG=1 to see debug output.
"""

from __future__ import annotations

import logging
import os

import structlog

_debug_enabled = os.environ.get("FASTBREAK_DEBUG", "").lower() in ("1", "true", "yes")

if _debug_enabled:
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.DEBUG),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
    )
else:
    # Silent mode - set level above CRITICAL to filter everything
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(logging.CRITICAL),
        logger_factory=structlog.ReturnLoggerFactory(),
    )

logger = structlog.get_logger("fastbreak")
