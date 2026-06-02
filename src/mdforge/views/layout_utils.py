from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QWidget,
)

# Minimum touch-friendly sizes (logical pixels).
MIN_INPUT_HEIGHT = 36
MIN_BUTTON_WIDTH = 88
MIN_COMBO_WIDTH = 160
MIN_PAGE_WIDTH = 480


def tune_input(widget: QLineEdit | QComboBox) -> None:
    widget.setMinimumHeight(MIN_INPUT_HEIGHT)
    if isinstance(widget, QComboBox):
        widget.setMinimumWidth(MIN_COMBO_WIDTH)
        widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)


def tune_button(btn: QPushButton, *, fixed_width: int | None = None) -> None:
    btn.setMinimumHeight(MIN_INPUT_HEIGHT)
    if fixed_width is not None:
        btn.setFixedWidth(fixed_width)
        btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
    else:
        btn.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)


def wrap_scroll_page(page: QWidget) -> QScrollArea:
    """Scroll when the window is small instead of squashing child widgets."""
    page.setMinimumWidth(MIN_PAGE_WIDTH)
    scroll = QScrollArea()
    scroll.setObjectName("pageScroll")
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QScrollArea.Shape.NoFrame)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
    scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
    scroll.setWidget(page)
    scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    return scroll
