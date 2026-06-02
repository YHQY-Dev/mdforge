from __future__ import annotations

import warnings

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication


def configure_warnings() -> None:
    """Suppress noisy optional-dependency warnings we do not use (e.g. pydub/ffmpeg)."""
    warnings.filterwarnings(
        "ignore",
        message=".*ffmpeg.*",
        category=RuntimeWarning,
        module=r"pydub(\..*)?",
    )


def setup_app_font(app: QApplication) -> None:
    """Set a valid default point size so QSS does not leave QFont at -1."""
    font = QFont()
    font.setFamilies(["Segoe UI", "Microsoft YaHei UI", "sans-serif"])
    font.setPointSize(10)
    app.setFont(font)
