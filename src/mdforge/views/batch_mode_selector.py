from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from mdforge.core.file_collector import BatchMode

MODE_META: dict[BatchMode, tuple[str, str, str]] = {
    BatchMode.FILES: (
        "多选 PDF 文件",
        "适合零散文件",
        "一次选择一个或多个 PDF，全部输出到同一目录。",
    ),
    BatchMode.FLAT_FOLDER: (
        "文件夹内全部 PDF",
        "单层目录",
        "选定文件夹中所有 .pdf 平铺输出，不含子目录。",
    ),
    BatchMode.NESTED_FOLDERS: (
        "子文件夹各含一个 PDF",
        "examples/files 结构",
        "每个子文件夹一个 PDF；转换后按子目录保存，并在 markdown/ 汇总 .md（以 PDF 文件名命名）。",
    ),
}


class _ModeCard(QFrame):
    activated = Signal()

    def __init__(
        self,
        mode: BatchMode,
        title: str,
        badge: str,
        description: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.mode = mode
        self.setObjectName("modeCard")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumHeight(100)
        self.setMinimumWidth(140)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(6)
        title_lbl = QLabel(title)
        title_lbl.setObjectName("modeCardTitle")
        title_lbl.setWordWrap(True)
        badge_lbl = QLabel(badge)
        badge_lbl.setObjectName("modeCardBadge")
        desc_lbl = QLabel(description)
        desc_lbl.setObjectName("modeCardDesc")
        desc_lbl.setWordWrap(True)
        layout.addWidget(title_lbl)
        layout.addWidget(badge_lbl)
        layout.addWidget(desc_lbl)

    def set_selected(self, selected: bool) -> None:
        self.setProperty("selected", selected)
        self.style().unpolish(self)
        self.style().polish(self)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.activated.emit()
        super().mouseReleaseEvent(event)


class BatchModeSelector(QWidget):
    mode_changed = Signal(object)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        self._cards: dict[BatchMode, _ModeCard] = {}
        self._current = BatchMode.FILES
        for mode in (BatchMode.FILES, BatchMode.FLAT_FOLDER, BatchMode.NESTED_FOLDERS):
            title, badge, desc = MODE_META[mode]
            card = _ModeCard(mode, title, badge, desc)
            self._cards[mode] = card
            card.activated.connect(lambda m=mode: self.set_mode(m, emit=True))
            layout.addWidget(card, 1)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.set_mode(BatchMode.FILES, emit=False)

    def selected_mode(self) -> BatchMode:
        return self._current

    def set_mode(self, mode: BatchMode, *, emit: bool = False) -> None:
        self._current = mode
        for m, card in self._cards.items():
            card.set_selected(m == mode)
        if emit:
            self.mode_changed.emit(mode)
