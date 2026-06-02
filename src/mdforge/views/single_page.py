from __future__ import annotations

from PySide6.QtWidgets import (
    QLabel,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from mdforge.views.components import LogPanel, PageHeader, SectionFrame
from mdforge.views.layout_utils import tune_button
from mdforge.views.widgets import PathPicker


class SinglePage(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        root = QVBoxLayout(self)
        root.setSpacing(18)
        root.setContentsMargins(0, 0, 0, 0)

        root.addWidget(
            PageHeader(
                "单文件转换",
                "选择 PDF 与输出 Markdown 路径；解析器在「设置」中切换。",
            )
        )
        self.parser_badge = QLabel()
        self.parser_badge.setObjectName("activeParserBadge")
        root.addWidget(self.parser_badge)

        paths = SectionFrame("文件路径")
        self.input_picker = PathPicker("输入 PDF")
        self.output_picker = PathPicker(
            "输出 Markdown", save_file=True, file_filter="Markdown (*.md)"
        )
        paths.add_widget(self.input_picker)
        paths.add_widget(self.output_picker)
        root.addWidget(paths)

        self.convert_btn = QPushButton("开始转换")
        self.convert_btn.setObjectName("primaryBtn")
        tune_button(self.convert_btn)
        self.convert_btn.setMinimumHeight(44)
        self.convert_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        root.addWidget(self.convert_btn)

        self.progress = QProgressBar()
        self.progress.setObjectName("mainProgress")
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.hide()
        root.addWidget(self.progress)

        log_section = SectionFrame("运行日志")
        self.log = LogPanel("转换日志…")
        log_section.add_widget(self.log)
        root.addWidget(log_section, 1)

    def set_active_parser(self, label: str) -> None:
        self.parser_badge.setText(f"  当前解析器 · {label}  ")

    def append_log(self, text: str) -> None:
        self.log.append_line(text)

    def set_progress(self, value: int) -> None:
        self.progress.setValue(max(0, min(100, value)))

    def set_busy(self, busy: bool) -> None:
        self.convert_btn.setEnabled(not busy)
        self.input_picker.set_busy(busy)
        self.output_picker.set_busy(busy)
        if busy:
            self.progress.setRange(0, 100)
            self.progress.setValue(0)
            self.progress.show()
        else:
            self.progress.hide()
