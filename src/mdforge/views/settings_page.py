from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QFrame,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from mdforge.core.settings import ParserType
from mdforge.views.components import LogPanel, PageHeader, SectionFrame
from mdforge.views.layout_utils import tune_input

PARSER_META: dict[ParserType, tuple[str, str, str]] = {
    ParserType.MARKITDOWN: (
        "MarkItDown",
        "本地 · 免费",
        "无需网络与 Token，适合纯文本 PDF，速度最快。",
    ),
    ParserType.MINERU: (
        "MinerU",
        "云端 · 高精度",
        "表格、公式、复杂版式效果好，需填写 API Token。",
    ),
    ParserType.PADDLEOCR: (
        "PaddleOCR",
        "云端 · OCR",
        "上传 PDF 云端识别，需填写 API Token。",
    ),
}


class _ParserCard(QFrame):
    activated = Signal()

    def __init__(
        self,
        parser: ParserType,
        title: str,
        badge: str,
        description: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.parser = parser
        self.setObjectName("parserCard")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.setMinimumHeight(96)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(8)
        name = QLabel(title)
        name.setObjectName("parserCardTitle")
        name.setWordWrap(True)
        tag = QLabel(badge)
        tag.setObjectName("parserCardBadge")
        tag.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(name)
        layout.addWidget(tag)
        desc = QLabel(description)
        desc.setObjectName("parserCardDesc")
        desc.setWordWrap(True)
        layout.addWidget(desc)

    def set_selected(self, selected: bool) -> None:
        self.setProperty("selected", selected)
        self.style().unpolish(self)
        self.style().polish(self)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.activated.emit()
        super().mouseReleaseEvent(event)


class SettingsPage(QWidget):
    parser_changed = Signal(object)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        root = QVBoxLayout(self)
        root.setSpacing(16)
        root.setContentsMargins(0, 0, 0, 0)

        root.addWidget(
            PageHeader(
                "设置",
                "解析引擎：点击卡片立即生效。"
                "Token / API / 模型：输入框失焦或下拉变更后自动保存到本地。",
            )
        )

        engine_section = SectionFrame("解析引擎")
        cards_col = QVBoxLayout()
        cards_col.setSpacing(10)
        self._parser_cards: dict[ParserType, _ParserCard] = {}
        for ptype in (ParserType.MARKITDOWN, ParserType.MINERU, ParserType.PADDLEOCR):
            t, badge, desc = PARSER_META[ptype]
            card = _ParserCard(ptype, t, badge, desc)
            self._parser_cards[ptype] = card
            cards_col.addWidget(card)
            card.activated.connect(
                lambda _checked=False, p=ptype: self.set_parser(p, emit_signal=True)
            )
        cards_wrap = QWidget()
        cards_wrap.setLayout(cards_col)
        cards_wrap.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        engine_section.add_widget(cards_wrap)

        self.status_label = QLabel()
        self.status_label.setObjectName("parserStatus")
        self.status_label.setWordWrap(True)
        engine_section.add_widget(self.status_label)
        root.addWidget(engine_section)

        config_section = SectionFrame("解析器配置")
        self.stack = QStackedWidget()
        self.stack.setObjectName("settingsStack")
        self.stack.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        markitdown_page = QFrame()
        markitdown_page.setObjectName("settingsPanel")
        mk_layout = QVBoxLayout(markitdown_page)
        mk_layout.setContentsMargins(16, 14, 16, 14)
        mk_info = QLabel(
            "✓ 本地 MarkItDown 已就绪\n"
            "无需配置 Token，选择 PDF 后即可在「单文件」或「批量」页开始转换。"
        )
        mk_info.setObjectName("panelHint")
        mk_info.setWordWrap(True)
        mk_layout.addWidget(mk_info)
        mk_layout.addStretch()
        self.stack.addWidget(markitdown_page)

        mineru_page = QWidget()
        mineru_form = QFormLayout(mineru_page)
        mineru_form.setContentsMargins(16, 14, 16, 14)
        mineru_form.setSpacing(14)
        mineru_form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        mineru_form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        mineru_form.setFormAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.mineru_token = QLineEdit()
        self.mineru_token.setEchoMode(QLineEdit.EchoMode.Password)
        self.mineru_token.setPlaceholderText("在 mineru.net 申请的 Bearer Token")
        tune_input(self.mineru_token)
        mineru_form.addRow("API Token", self.mineru_token)
        self.mineru_url = QLineEdit()
        self.mineru_url.setPlaceholderText("https://mineru.net")
        tune_input(self.mineru_url)
        mineru_form.addRow("API 地址", self.mineru_url)
        self.mineru_model = QComboBox()
        self.mineru_model.addItems(["vlm", "pipeline", "MinerU-HTML"])
        tune_input(self.mineru_model)
        mineru_form.addRow("模型版本", self.mineru_model)
        mineru_hint = QLabel(
            "一次 PUT 上传整份 PDF，解析完成后解压 zip，包含 full.md 与 images 等资源。"
        )
        mineru_hint.setObjectName("panelHint")
        mineru_hint.setWordWrap(True)
        mineru_form.addRow(mineru_hint)
        self.stack.addWidget(mineru_page)

        paddle_page = QWidget()
        paddle_form = QFormLayout(paddle_page)
        paddle_form.setContentsMargins(16, 14, 16, 14)
        paddle_form.setSpacing(14)
        paddle_form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        paddle_form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        paddle_form.setFormAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.paddle_token = QLineEdit()
        self.paddle_token.setEchoMode(QLineEdit.EchoMode.Password)
        self.paddle_token.setPlaceholderText("AI Studio 申请的 Token")
        tune_input(self.paddle_token)
        paddle_form.addRow("API Token", self.paddle_token)
        self.paddle_url = QLineEdit()
        self.paddle_url.setPlaceholderText("https://paddleocr.aistudio-app.com/api/v2/ocr/jobs")
        tune_input(self.paddle_url)
        paddle_form.addRow("任务 API", self.paddle_url)
        self.paddle_model = QLineEdit()
        self.paddle_model.setPlaceholderText("PaddleOCR-VL-1.6")
        tune_input(self.paddle_model)
        paddle_form.addRow("模型名称", self.paddle_model)
        paddle_hint = QLabel(
            "异步任务接口：一次 multipart 上传整份 PDF。日志里「x/y 页」仅为云端处理进度，"
            "不会在本地拆页或多次上传。图片保存到输出 .md 同目录。"
        )
        paddle_hint.setObjectName("panelHint")
        paddle_hint.setWordWrap(True)
        paddle_form.addRow(paddle_hint)
        self.stack.addWidget(paddle_page)

        config_section.add_widget(self.stack)
        root.addWidget(config_section, 1)

        save_policy = QLabel(
            "解析器切换后立即用于转换；云端配置在编辑完成时自动写入，无需额外点击保存。"
        )
        save_policy.setObjectName("savePolicyHint")
        save_policy.setWordWrap(True)
        root.addWidget(save_policy)

        log_section = SectionFrame("操作记录")
        self.log = LogPanel("保存与切换记录…")
        log_section.add_widget(self.log)
        root.addWidget(log_section, 1)

        self._current_parser = ParserType.MARKITDOWN
        self._stack_index = {
            ParserType.MARKITDOWN: 0,
            ParserType.MINERU: 1,
            ParserType.PADDLEOCR: 2,
        }

    def append_log(self, text: str) -> None:
        self.log.append_line(text)

    def selected_parser(self) -> ParserType:
        return self._current_parser

    def set_parser(self, p: ParserType, *, emit_signal: bool = False) -> None:
        self._current_parser = p
        for ptype, card in self._parser_cards.items():
            card.set_selected(ptype == p)
        self.stack.setCurrentIndex(self._stack_index[p])
        title, badge, desc = PARSER_META[p]
        if p == ParserType.MINERU:
            token_hint = "已配置 Token" if self.mineru_token.text().strip() else "未配置 Token"
        elif p == ParserType.PADDLEOCR:
            token_hint = "已配置 Token" if self.paddle_token.text().strip() else "未配置 Token"
        else:
            token_hint = "无需 Token"
        self.status_label.setText(
            f"当前解析器：{title}（{badge}）— {token_hint}\n{desc}"
        )
        if emit_signal:
            self.parser_changed.emit(p)
