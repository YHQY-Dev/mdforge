from __future__ import annotations

from mdforge.core.settings import AppSettings, ParserType
from mdforge.parsers.base import BaseParser, ParserError


def create_parser(settings: AppSettings) -> BaseParser:
    ptype = settings.parser
    if ptype == ParserType.MARKITDOWN:
        from mdforge.parsers.markitdown_parser import MarkItDownParser

        return MarkItDownParser()
    if ptype == ParserType.MINERU:
        from mdforge.parsers.mineru_parser import MinerUParser

        return MinerUParser(
            token=settings.mineru_token,
            base_url=settings.mineru_base_url,
            model_version=settings.mineru_model_version,
        )
    if ptype == ParserType.PADDLEOCR:
        from mdforge.parsers.paddleocr_parser import PaddleOCRParser

        return PaddleOCRParser(
            token=settings.paddleocr_token,
            job_url=settings.paddleocr_job_url,
            model=settings.paddleocr_model,
        )
    raise ParserError(f"未知解析器: {ptype}")
