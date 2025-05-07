import json
import sys
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


def log(
    message: str,
    level: LogLevel = LogLevel.INFO,
    extra: Optional[Dict[str, Any]] = None,
) -> None:
    log_entry = {
        "message": message,
        "timestamp": datetime.now().isoformat(),
        "level": level,
    }

    if extra:
        log_entry.update(extra)

    print(json.dumps(log_entry), file=sys.stdout)


def debug(message: str, extra: Optional[Dict[str, Any]] = None) -> None:
    log(message, LogLevel.DEBUG, extra)


def info(message: str, extra: Optional[Dict[str, Any]] = None) -> None:
    log(message, LogLevel.INFO, extra)


def warning(message: str, extra: Optional[Dict[str, Any]] = None) -> None:
    log(message, LogLevel.WARNING, extra)


def error(message: str, extra: Optional[Dict[str, Any]] = None) -> None:
    log(message, LogLevel.ERROR, extra)


def critical(message: str, extra: Optional[Dict[str, Any]] = None) -> None:
    log(message, LogLevel.CRITICAL, extra)
