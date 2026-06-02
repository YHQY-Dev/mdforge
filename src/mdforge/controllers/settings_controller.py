from __future__ import annotations



from PySide6.QtCore import Slot

from PySide6.QtWidgets import QComboBox, QLineEdit



from mdforge.controllers.base import BaseController

from mdforge.core.settings import AppSettings, ParserType

from mdforge.views.main_window import MainWindow





class SettingsController(BaseController):

    def __init__(self, window: MainWindow, settings: AppSettings) -> None:

        super().__init__(window)

        self._settings = settings

        self._page = window.settings_page

        self._page.parser_changed.connect(self._on_parser_changed)

        self._wire_auto_save()

        self.load()



    def _wire_auto_save(self) -> None:

        for widget in (

            self._page.mineru_token,

            self._page.mineru_url,

            self._page.paddle_token,

            self._page.paddle_url,

            self._page.paddle_model,

        ):

            widget.editingFinished.connect(self._persist_cloud_settings)

        self._page.mineru_model.currentTextChanged.connect(self._persist_cloud_settings)



    def load(self) -> None:

        self._page.mineru_token.setText(self._settings.mineru_token)

        self._page.mineru_url.setText(self._settings.mineru_base_url)

        idx = self._page.mineru_model.findText(self._settings.mineru_model_version)

        if idx >= 0:

            self._page.mineru_model.setCurrentIndex(idx)

        self._page.paddle_token.setText(self._settings.paddleocr_token)

        self._page.paddle_url.setText(self._settings.paddleocr_job_url)

        self._page.paddle_model.setText(self._settings.paddleocr_model)

        self._apply_parser_ui(self._settings.parser, log_load=True)



    def _apply_parser_ui(self, parser: ParserType, *, log_load: bool = False) -> None:

        label = self._parser_label(parser)

        self._page.set_parser(parser, emit_signal=False)

        self._window.single_page.set_active_parser(label)

        self._window.batch_page.set_active_parser(label)

        if log_load:

            self._page.append_log(f"已加载配置，当前解析器：{label}")



    @Slot(object)

    def _on_parser_changed(self, parser: ParserType) -> None:

        self._settings.parser = parser

        self._settings.sync()

        label = self._parser_label(parser)

        self._page.append_log(f"已切换解析器（立即生效）：{label}")

        self._apply_parser_ui(parser)



    @Slot()

    def _persist_cloud_settings(self) -> None:

        sender = self.sender()

        if isinstance(sender, (QLineEdit, QComboBox)) and not sender.isEnabled():

            return

        self._settings.mineru_token = self._page.mineru_token.text().strip()

        self._settings.mineru_base_url = self._page.mineru_url.text().strip() or "https://mineru.net"

        self._settings.mineru_model_version = self._page.mineru_model.currentText()

        self._settings.paddleocr_token = self._page.paddle_token.text().strip()

        self._settings.paddleocr_job_url = (

            self._page.paddle_url.text().strip()

            or "https://paddleocr.aistudio-app.com/api/v2/ocr/jobs"

        )

        self._settings.paddleocr_model = (

            self._page.paddle_model.text().strip() or "PaddleOCR-VL-1.6"

        )

        self._settings.sync()

        self._apply_parser_ui(self._page.selected_parser())

        self._page.append_log("[已自动保存] Token、API 地址与模型。")



    @staticmethod

    def _parser_label(parser: ParserType) -> str:

        labels = {

            ParserType.MARKITDOWN: "MarkItDown（本地）",

            ParserType.MINERU: "MinerU（云端）",

            ParserType.PADDLEOCR: "PaddleOCR（云端）",

        }

        return labels.get(parser, str(parser))


