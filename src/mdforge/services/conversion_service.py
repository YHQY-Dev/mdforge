from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from loguru import logger

from mdforge.core.batch_paths import build_nested_flat_markdown_folder, ensure_output_dir
from mdforge.core.file_collector import BatchMode
from mdforge.core.settings import AppSettings, ParserType
from mdforge.models.conversion import (
    BatchConversionRequest,
    ConversionResult,
    SingleConversionRequest,
)
from mdforge.parsers.base import BaseParser, ParserError, ProgressCallback
from mdforge.parsers.factory import create_parser


class ConversionService:
    def __init__(self, settings: AppSettings) -> None:
        self._settings = settings
        self._markitdown_parser: BaseParser | None = None

    def _create_parser(self, *, reuse_markitdown: bool = False) -> BaseParser:
        if reuse_markitdown and self._settings.parser == ParserType.MARKITDOWN:
            if self._markitdown_parser is None:
                self._markitdown_parser = create_parser(self._settings)
            return self._markitdown_parser
        return create_parser(self._settings)

    def convert_single(
        self,
        request: SingleConversionRequest,
        on_progress: ProgressCallback | None = None,
    ) -> ConversionResult:
        parser = self._create_parser()
        pdf, out = request.input_path, request.output_path
        out.parent.mkdir(parents=True, exist_ok=True)
        try:
            parser.convert_pdf(pdf, out, on_progress)
            return ConversionResult(pdf, out, True, "成功")
        except (ParserError, Exception) as exc:
            logger.error("转换失败 {}: {}", pdf, exc)
            return ConversionResult(pdf, out, False, str(exc))

    def convert_batch(
        self,
        request: BatchConversionRequest,
        on_progress: ProgressCallback | None = None,
        on_file_done: Callable[[ConversionResult], None] | None = None,
        should_cancel: Callable[[], bool] | None = None,
    ) -> list[ConversionResult]:
        ensure_output_dir(request.output_dir)
        jobs = request.prepare()
        if not jobs:
            return []

        parser = self._create_parser(reuse_markitdown=True)
        if hasattr(parser, "convert_jobs"):
            if on_progress:
                on_progress(
                    f"{parser.name} 批量模式：共 {len(jobs)} 个文件",
                    0.0,
                )
            results = parser.convert_jobs(
                jobs,
                on_progress=on_progress,
                on_file_done=on_file_done,
                should_cancel=should_cancel,
            )
        else:
            results = self._convert_sequential(
                parser, jobs, on_progress, on_file_done, should_cancel
            )

        if not (should_cancel and should_cancel()):
            self._finalize_nested_batch(request, jobs, results, on_progress)
        elif on_progress:
            on_progress("批量转换已取消", 1.0)
        return results

    def _finalize_nested_batch(
        self,
        request: BatchConversionRequest,
        jobs: list,
        results: list[ConversionResult],
        on_progress: ProgressCallback | None,
    ) -> None:
        if request.mode != BatchMode.NESTED_FOLDERS:
            return
        summary = build_nested_flat_markdown_folder(
            request.output_dir, jobs, results
        )
        if summary is None:
            return
        flat_dir, count = summary
        logger.info("已汇总 {} 个 Markdown 至 {}", count, flat_dir)
        if on_progress:
            on_progress(
                f"已汇总 {count} 个 Markdown 至 {flat_dir.name}/ 文件夹",
                1.0,
            )

    def _convert_sequential(
        self,
        parser: BaseParser,
        jobs: list,
        on_progress: ProgressCallback | None,
        on_file_done: Callable[[ConversionResult], None] | None,
        should_cancel: Callable[[], bool] | None,
    ) -> list[ConversionResult]:
        results: list[ConversionResult] = []
        total = len(jobs)
        for idx, job in enumerate(jobs):
            if should_cancel and should_cancel():
                break
            if on_progress:
                on_progress(f"正在处理 ({idx + 1}/{total}): {job.pdf_path.name}", idx / total)

            def file_progress(msg: str, pct: float | None) -> None:
                if on_progress is None:
                    return
                if pct is not None:
                    on_progress(f"[{idx + 1}/{total}] {msg}", (idx + pct) / total)
                else:
                    on_progress(f"[{idx + 1}/{total}] {msg}", idx / total)

            job.output_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                parser.convert_pdf(job.pdf_path, job.output_path, file_progress)
                r = ConversionResult(job.pdf_path, job.output_path, True, "成功")
            except (ParserError, Exception) as exc:
                logger.error("批量转换失败 {}: {}", job.pdf_path, exc)
                r = ConversionResult(job.pdf_path, job.output_path, False, str(exc))
            results.append(r)
            if on_file_done:
                on_file_done(r)

        if on_progress:
            on_progress("批量任务结束", 1.0)
        return results
