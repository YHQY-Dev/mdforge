from __future__ import annotations

import sys
from pathlib import Path

from loguru import logger


def setup_logging(log_dir: Path | None = None) -> Path:
    """Configure loguru: console + rotating file under log_dir."""
    logger.remove()
    # PyInstaller windowed builds (console=False) attach no stderr stream.
    stderr = sys.stderr or getattr(sys, "__stderr__", None)
    if stderr is not None:
        logger.add(
            stderr,
            level="INFO",
            format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}",
        )
    if log_dir is None:
        log_dir = Path.home() / ".mdforge" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "mdforge_{time:YYYY-MM-DD}.log"
    logger.add(
        log_file,
        rotation="10 MB",
        retention="14 days",
        encoding="utf-8",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
    )
    return log_dir
