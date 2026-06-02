from __future__ import annotations

from PySide6.QtCore import QThread, Signal

from mdforge.models.conversion import BatchConversionRequest, ConversionResult, SingleConversionRequest
from mdforge.services.conversion_service import ConversionService


class SingleConversionThread(QThread):
    """Run single-file conversion in a background thread."""

    progress = Signal(str, float)
    finished_result = Signal(object)
    failed = Signal(str)

    def __init__(
        self,
        service: ConversionService,
        request: SingleConversionRequest,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._service = service
        self._request = request

    def run(self) -> None:
        try:

            def on_progress(msg: str, pct: float | None) -> None:
                self.progress.emit(msg, -1.0 if pct is None else pct)

            result = self._service.convert_single(self._request, on_progress)
            self.finished_result.emit(result)
        except Exception as exc:
            self.failed.emit(str(exc))


class BatchConversionThread(QThread):
    progress = Signal(str, float)
    file_done = Signal(object)
    finished_results = Signal(list)
    failed = Signal(str)

    def __init__(
        self,
        service: ConversionService,
        request: BatchConversionRequest,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._service = service
        self._request = request
        self._cancel = False

    def cancel(self) -> None:
        self._cancel = True

    def run(self) -> None:
        try:

            def on_progress(msg: str, pct: float | None) -> None:
                self.progress.emit(msg, -1.0 if pct is None else pct)

            def on_file_done(r: ConversionResult) -> None:
                self.file_done.emit(r)

            results = self._service.convert_batch(
                self._request,
                on_progress=on_progress,
                on_file_done=on_file_done,
                should_cancel=lambda: self._cancel,
            )
            self.finished_results.emit(results)
        except Exception as exc:
            self.failed.emit(str(exc))
