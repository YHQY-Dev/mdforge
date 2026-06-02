from __future__ import annotations

import warnings
from pathlib import Path

from loguru import logger

from mdforge.parsers.base import BaseParser, ParserError, ProgressCallback


class MarkItDownParser(BaseParser):
    """Local conversion via Microsoft MarkItDown."""

    def __init__(self) -> None:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            from markitdown import MarkItDown

            self._md = MarkItDown(enable_plugins=False)

    @property
    def name(self) -> str:
        return "MarkItDown"

    def convert_pdf(
        self,
        pdf_path: Path,
        output_path: Path,
        on_progress: ProgressCallback | None = None,
    ) -> None:
        if not pdf_path.is_file():
            raise ParserError(f"文件不存在: {pdf_path}")
        self._report(on_progress, "正在本地解析 PDF…", 0.2)
        try:
            result = self._md.convert(str(pdf_path))
        except Exception as exc:
            logger.exception("MarkItDown 转换失败: {}", pdf_path)
            raise ParserError(str(exc)) from exc
        text = result.text_content or ""
        if not text.strip():
            raise ParserError("MarkItDown 未提取到文本内容")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(text, encoding="utf-8")
        self._report(on_progress, "转换完成", 1.0)
        logger.info("MarkItDown 已保存: {}", output_path)
