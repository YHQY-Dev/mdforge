from pathlib import Path
from unittest.mock import MagicMock

import pytest

from mdforge.core.file_collector import BatchMode, PdfJob
from mdforge.core.settings import ParserType
from mdforge.models.conversion import BatchConversionRequest, ConversionResult
from mdforge.parsers.markitdown_parser import MarkItDownParser
from mdforge.services.conversion_service import ConversionService


def test_markitdown_parser_reused_in_batch(app_settings):
    app_settings.parser = ParserType.MARKITDOWN
    service = ConversionService(app_settings)
    first = service._create_parser(reuse_markitdown=True)
    second = service._create_parser(reuse_markitdown=True)
    assert first is second
    assert isinstance(first, MarkItDownParser)


def test_markitdown_parser_not_reused_for_single(app_settings):
    app_settings.parser = ParserType.MARKITDOWN
    service = ConversionService(app_settings)
    service._markitdown_parser = MarkItDownParser()
    other = service._create_parser(reuse_markitdown=False)
    assert other is not service._markitdown_parser


def test_batch_skips_nested_flat_folder_on_cancel(app_settings, tmp_path: Path):
    app_settings.parser = ParserType.MARKITDOWN
    service = ConversionService(app_settings)
    out = tmp_path / "out"
    pdf = tmp_path / "sub" / "a.pdf"
    pdf.parent.mkdir(parents=True)
    pdf.write_bytes(b"%PDF-1.4")
    md = out / "sub" / "a.md"
    job = PdfJob.create(pdf_path=pdf, output_path=md)
    request = BatchConversionRequest(
        mode=BatchMode.NESTED_FOLDERS,
        output_dir=out,
        jobs=[job],
    )

    class StubParser:
        name = "Stub"

        def convert_pdf(self, *_args, **_kwargs) -> None:
            md.parent.mkdir(parents=True, exist_ok=True)
            md.write_text("# ok", encoding="utf-8")

    service._create_parser = MagicMock(return_value=StubParser())  # type: ignore[method-assign]
    results = service.convert_batch(request, should_cancel=lambda: True)
    assert len(results) == 0
    assert not (out / "markdown").exists()
