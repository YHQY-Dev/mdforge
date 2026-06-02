from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from mdforge.views.layout_utils import MIN_BUTTON_WIDTH, tune_button, tune_input


class PathPicker(QWidget):
    path_changed = Signal(str)

    def __init__(
        self,
        label: str,
        *,
        is_directory: bool = False,
        save_file: bool = False,
        file_filter: str = "PDF 文件 (*.pdf)",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._is_directory = is_directory
        self._save_file = save_file
        self._file_filter = file_filter
        self._dialog_start_dir = ""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(QLabel(label))
        row = QHBoxLayout()
        self._edit = QLineEdit()
        self._edit.setPlaceholderText("点击浏览选择路径…")
        tune_input(self._edit)
        self._edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._edit.textChanged.connect(self.path_changed.emit)
        browse = QPushButton("浏览…")
        browse.setObjectName("secondaryBtn")
        tune_button(browse, fixed_width=MIN_BUTTON_WIDTH)
        browse.clicked.connect(self._browse)
        row.addWidget(self._edit, 1)
        row.addWidget(browse, 0)
        layout.addLayout(row)

    def path(self) -> str:
        from mdforge.core.paths import normalize_path

        return normalize_path(self._edit.text())

    def set_path(self, value: str) -> None:
        self._edit.setText(value)

    def set_dialog_start_dir(self, directory: str) -> None:
        """Default folder for the file dialog only (does not fill the text field)."""
        self._dialog_start_dir = directory

    def set_busy(self, busy: bool) -> None:
        """Disable only the line edit and browse button; never disable the whole page."""
        self._edit.setEnabled(not busy)
        for child in self.findChildren(QPushButton):
            child.setEnabled(not busy)

    def _browse(self) -> None:
        start = self._edit.text() or self._dialog_start_dir or ""
        if self._is_directory:
            path = QFileDialog.getExistingDirectory(self, "选择文件夹", start)
        elif self._save_file:
            path, _ = QFileDialog.getSaveFileName(self, "保存为", start, self._file_filter)
        else:
            path, _ = QFileDialog.getOpenFileName(self, "选择文件", start, self._file_filter)
        if path:
            self._edit.setText(path)
