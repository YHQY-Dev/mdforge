from __future__ import annotations

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QMessageBox, QWidget


class BaseController(QObject):
    """QObject-based controller; parent keeps the instance alive with the window."""

    def __init__(self, window: QWidget) -> None:
        super().__init__(window)
        self._window = window

    def _warn(self, page: QWidget, title: str, text: str) -> None:
        if hasattr(page, "append_log"):
            page.append_log(f"[提示] {text}")
        QMessageBox.warning(page, title, text)

    def _info(self, page: QWidget, title: str, text: str) -> None:
        if hasattr(page, "append_log"):
            page.append_log(f"[完成] {text}")
        QMessageBox.information(page, title, text)

    def _error(self, page: QWidget, title: str, text: str) -> None:
        if hasattr(page, "append_log"):
            page.append_log(f"[错误] {text}")
        QMessageBox.critical(page, title, text)
