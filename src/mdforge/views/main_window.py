from __future__ import annotations

from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from mdforge.views.batch_page import BatchPage
from mdforge.views.layout_utils import wrap_scroll_page
from mdforge.views.settings_page import SettingsPage
from mdforge.views.single_page import SinglePage


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("MdForge")
        self.resize(1080, 720)
        self.setMinimumSize(760, 520)

        central = QWidget()
        central.setObjectName("centralRoot")
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(200)
        sidebar.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        side_layout = QVBoxLayout(sidebar)
        side_layout.setContentsMargins(20, 28, 20, 28)
        side_layout.setSpacing(4)

        brand = QLabel("MdForge")
        brand.setObjectName("brandTitle")
        tagline = QLabel("PDF → Markdown")
        tagline.setObjectName("brandSubtitle")
        side_layout.addWidget(brand)
        side_layout.addWidget(tagline)

        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)

        self.stack = QStackedWidget()
        self.stack.setObjectName("pageStack")
        self.single_page = SinglePage()
        self.batch_page = BatchPage()
        self.settings_page = SettingsPage()
        for page in (self.single_page, self.batch_page, self.settings_page):
            card = QFrame()
            card.setObjectName("contentCard")
            wrap = QVBoxLayout(card)
            wrap.setContentsMargins(20, 16, 20, 16)
            wrap.addWidget(wrap_scroll_page(page), 1)
            self.stack.addWidget(card)

        nav_items = [
            ("  单文件转换", 0),
            ("  批量转换", 1),
            ("  设置", 2),
        ]
        for text, index in nav_items:
            btn = QPushButton(text)
            btn.setObjectName("navBtn")
            btn.setMinimumHeight(44)
            btn.setCheckable(True)
            btn.clicked.connect(lambda _c=False, idx=index: self._go(idx))
            self.nav_group.addButton(btn)
            side_layout.addWidget(btn)
        side_layout.addStretch()
        layout.addWidget(sidebar)
        layout.addWidget(self.stack, 1)
        self._go(0)

    def closeEvent(self, event: QCloseEvent) -> None:
        for ctrl in getattr(self, "controllers", []):
            if hasattr(ctrl, "is_busy") and ctrl.is_busy():
                from PySide6.QtWidgets import QMessageBox

                QMessageBox.warning(
                    self,
                    "转换进行中",
                    "请等待当前转换任务完成后再关闭窗口。",
                )
                event.ignore()
                return
        super().closeEvent(event)

    def _go(self, index: int) -> None:
        self.stack.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_group.buttons()):
            btn.setChecked(i == index)
