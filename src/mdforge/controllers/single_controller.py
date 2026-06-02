from __future__ import annotations

from pathlib import Path

from loguru import logger
from PySide6.QtCore import Qt, Slot

from mdforge.controllers.base import BaseController
from mdforge.core.paths import to_path
from mdforge.core.settings import AppSettings
from mdforge.models.conversion import SingleConversionRequest
from mdforge.services.conversion_service import ConversionService
from mdforge.views.main_window import MainWindow
from mdforge.workers.conversion_worker import SingleConversionThread


def _count_sibling_assets(output_md: Path) -> int:
    parent = output_md.parent
    count = 0
    for p in parent.iterdir():
        if p.resolve() == output_md.resolve():
            continue
        if p.is_dir():
            count += sum(1 for _ in p.rglob("*") if _.is_file())
        else:
            count += 1
    return count


class SingleController(BaseController):
    def __init__(
        self,
        window: MainWindow,
        settings: AppSettings,
        service: ConversionService,
    ) -> None:
        super().__init__(window)
        self._settings = settings
        self._service = service
        self._page = window.single_page
        self._thread: SingleConversionThread | None = None
        self._page.convert_btn.clicked.connect(self.start)
        self._page.input_picker.path_changed.connect(self._on_input_changed)
        if settings.last_input_dir:
            self._page.input_picker.set_dialog_start_dir(settings.last_input_dir)
        if settings.last_output_dir:
            self._page.output_picker.set_dialog_start_dir(settings.last_output_dir)

    def is_busy(self) -> bool:
        return self._thread is not None and self._thread.isRunning()

    def _on_input_changed(self, path: str) -> None:
        p = to_path(path)
        if p.suffix.lower() == ".pdf" and p.is_file():
            self._page.output_picker.set_path(str(p.with_suffix(".md")))

    @Slot()
    def start(self) -> None:
        if self.is_busy():
            self._warn(self._page, "提示", "转换正在进行中，请稍候。")
            return

        inp = self._page.input_picker.path()
        out = self._page.output_picker.path()
        if not inp or not out:
            self._warn(self._page, "提示", "请填写输入与输出路径。")
            return

        input_path = to_path(inp)
        if not input_path.is_file():
            self._warn(self._page, "提示", f"输入文件不存在：\n{input_path}")
            return
        if input_path.suffix.lower() != ".pdf":
            self._warn(self._page, "提示", "输入文件必须是 PDF。")
            return

        output_path = to_path(out)
        if output_path.suffix.lower() != ".md":
            output_path = output_path.with_suffix(".md")
            self._page.output_picker.set_path(str(output_path))

        self._settings.last_input_dir = str(input_path.parent)
        self._settings.last_output_dir = str(output_path.parent)
        self._settings.sync()

        request = SingleConversionRequest(input_path=input_path, output_path=output_path)
        thread = SingleConversionThread(self._service, request, parent=self._window)
        thread.progress.connect(self._on_progress, Qt.ConnectionType.QueuedConnection)
        thread.finished_result.connect(self._on_done)
        thread.failed.connect(self._on_error)
        thread.finished.connect(thread.deleteLater)
        self._thread = thread

        self._page.set_busy(True)
        self._page.log.clear()
        self._page.append_log("开始转换…")
        logger.info("开始单文件转换: {} -> {}", input_path, output_path)
        thread.start()

    @Slot(str, float)
    def _on_progress(self, msg: str, pct: float) -> None:
        self._page.append_log(msg)
        if pct >= 0:
            self._page.set_progress(int(pct * 100))

    @Slot(object)
    def _on_done(self, result) -> None:
        self._thread = None
        self._page.set_busy(False)
        if result.success:
            asset_n = _count_sibling_assets(result.output_path)
            extra = f"\n（同目录资源 {asset_n} 个）" if asset_n else ""
            self._page.append_log(f"完成：{result.output_path}{extra}")
            self._info(self._page, "成功", f"已保存到\n{result.output_path}{extra}")
        else:
            self._page.append_log(f"失败：{result.message}")
            self._error(self._page, "失败", result.message)

    @Slot(str)
    def _on_error(self, msg: str) -> None:
        self._thread = None
        self._page.set_busy(False)
        self._page.append_log(f"错误：{msg}")
        self._error(self._page, "错误", msg)
