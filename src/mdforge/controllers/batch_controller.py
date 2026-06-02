from __future__ import annotations



from pathlib import Path



from loguru import logger

from PySide6.QtCore import Qt, Slot



from mdforge.controllers.base import BaseController

from mdforge.core.file_collector import BatchMode

from mdforge.core.batch_paths import NESTED_FLAT_MD_DIR_NAME, ensure_output_dir

from mdforge.core.paths import to_path

from mdforge.core.settings import AppSettings

from mdforge.models.conversion import BatchConversionRequest

from mdforge.services.conversion_service import ConversionService

from mdforge.views.main_window import MainWindow

from mdforge.workers.conversion_worker import BatchConversionThread





class BatchController(BaseController):

    def __init__(

        self,

        window: MainWindow,

        settings: AppSettings,

        service: ConversionService,

    ) -> None:

        super().__init__(window)

        self._settings = settings

        self._service = service

        self._page = window.batch_page

        self._thread: BatchConversionThread | None = None

        self._cancel_requested = False

        self._page.convert_btn.clicked.connect(self.start)

        self._page.cancel_btn.clicked.connect(self.cancel)

        if settings.last_output_dir:

            self._page.output_picker.set_dialog_start_dir(settings.last_output_dir)



    def is_busy(self) -> bool:

        return self._thread is not None and self._thread.isRunning()



    @Slot()

    def start(self) -> None:

        if self.is_busy():

            self._warn(self._page, "提示", "批量转换正在进行中，请稍候。")

            return



        out_dir = to_path(self._page.output_picker.path())

        if not out_dir:

            self._warn(self._page, "提示", "请选择输出目录。")

            return

        mode = self._page.selected_mode()

        file_paths = [to_path(p) for p in self._page.file_paths()]

        folder = self._page.folder_path()

        folder_path = to_path(folder) if folder else None



        if mode == BatchMode.FILES and not file_paths:

            self._warn(self._page, "提示", "请先选择 PDF 文件。")

            return

        if mode != BatchMode.FILES and (not folder_path or not folder_path.is_dir()):

            self._warn(self._page, "提示", "请先选择有效的文件夹。")

            return



        request = BatchConversionRequest(

            mode=mode,

            output_dir=out_dir,

            file_paths=file_paths,

            folder_path=folder_path,

        )

        jobs = request.prepare()

        if not jobs:

            self._warn(self._page, "提示", "未找到可转换的 PDF 文件。")

            return



        ensure_output_dir(out_dir)

        self._settings.last_output_dir = str(out_dir)

        self._settings.sync()



        thread = BatchConversionThread(self._service, request, parent=self._window)

        thread.progress.connect(self._on_progress, Qt.ConnectionType.QueuedConnection)

        thread.file_done.connect(self._on_file_done, Qt.ConnectionType.QueuedConnection)

        thread.finished_results.connect(self._on_done)

        thread.failed.connect(self._on_error)

        thread.finished.connect(thread.deleteLater)

        self._thread = thread

        self._cancel_requested = False



        self._page.set_busy(True)

        self._page.set_progress(0)

        self._page.log.clear()

        self._page.append_log(f"共 {len(jobs)} 个文件待转换…")

        for w in request.warnings:

            self._page.append_log(f"[提示] {w}")

        logger.info("开始批量转换: {} 个文件", len(jobs))

        thread.start()



    @Slot()

    def cancel(self) -> None:

        if not self.is_busy() or self._thread is None:

            return

        self._cancel_requested = True

        self._thread.cancel()

        self._page.append_log("已请求取消，等待当前步骤结束…")



    @Slot(str, float)

    def _on_progress(self, msg: str, pct: float) -> None:

        self._page.append_log(msg)

        if pct >= 0:

            self._page.set_progress(int(pct * 100))



    @Slot(object)

    def _on_file_done(self, result) -> None:

        status = "成功" if result.success else f"失败: {result.message}"

        self._page.append_log(f"{result.pdf_path.name} → {status}")



    @Slot(list)

    def _on_done(self, results) -> None:

        cancelled = self._cancel_requested

        self._cancel_requested = False

        self._thread = None

        self._page.set_busy(False)

        self._page.set_progress(100)

        ok = sum(1 for r in results if r.success)

        total = len(results)

        if cancelled:

            msg = f"已取消，已完成 {ok}/{total} 个文件。"

            self._page.append_log(msg)

            self._warn(self._page, "已取消", msg)

            return



        msg = f"完成 {ok}/{total} 个文件。"

        if (

            self._page.selected_mode() == BatchMode.NESTED_FOLDERS

            and ok > 0

        ):

            out = to_path(self._page.output_picker.path())

            if out:

                flat = out / NESTED_FLAT_MD_DIR_NAME

                msg += f"\nMarkdown 汇总：{flat}"

        if ok == total:

            self._info(self._page, "批量完成", msg)

        elif ok == 0:

            self._error(self._page, "批量失败", msg)

        else:

            self._warn(self._page, "部分完成", msg)



    @Slot(str)

    def _on_error(self, msg: str) -> None:

        self._cancel_requested = False

        self._thread = None

        self._page.set_busy(False)

        self._page.append_log(f"错误：{msg}")

        self._error(self._page, "错误", msg)


