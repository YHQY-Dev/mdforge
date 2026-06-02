from __future__ import annotations

from PySide6.QtWidgets import QFrame, QLabel, QSizePolicy, QTextEdit, QVBoxLayout, QWidget


class PageHeader(QWidget):
    def __init__(self, title: str, subtitle: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        t = QLabel(title)
        t.setObjectName("cardTitle")
        t.setWordWrap(True)
        s = QLabel(subtitle)
        s.setObjectName("cardSubtitle")
        s.setWordWrap(True)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        layout.addWidget(t)
        layout.addWidget(s)


class SectionFrame(QFrame):
    def __init__(self, title: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("sectionFrame")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)
        self._title = QLabel(title)
        self._title.setObjectName("sectionTitle")
        layout.addWidget(self._title)
        self.body = QVBoxLayout()
        self.body.setSpacing(10)
        layout.addLayout(self.body)

    def add_widget(self, widget: QWidget) -> None:
        self.body.addWidget(widget)


class LogPanel(QTextEdit):
    def __init__(self, placeholder: str = "日志…", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setReadOnly(True)
        self.setObjectName("logPanel")
        self.setPlaceholderText(placeholder)
        self.setMinimumHeight(100)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def append_line(self, text: str) -> None:
        self.append(text)
