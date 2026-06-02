import pytest

from mdforge.core.settings import ParserType
from mdforge.parsers.base import ParserError
from mdforge.parsers.factory import create_parser
from mdforge.parsers.markitdown_parser import MarkItDownParser
from mdforge.parsers.mineru_parser import MinerUParser
from mdforge.parsers.paddleocr_parser import PaddleOCRParser


def test_create_markitdown_parser(app_settings):
    app_settings.parser = ParserType.MARKITDOWN
    parser = create_parser(app_settings)
    assert isinstance(parser, MarkItDownParser)
    assert parser.name == "MarkItDown"


def test_create_mineru_parser(app_settings):
    app_settings.parser = ParserType.MINERU
    app_settings.mineru_token = "test-token"
    parser = create_parser(app_settings)
    assert isinstance(parser, MinerUParser)


def test_create_paddleocr_parser(app_settings):
    app_settings.parser = ParserType.PADDLEOCR
    app_settings.paddleocr_token = "test-token"
    parser = create_parser(app_settings)
    assert isinstance(parser, PaddleOCRParser)


def test_mineru_requires_token(app_settings):
    app_settings.parser = ParserType.MINERU
    app_settings.mineru_token = ""
    with pytest.raises(ParserError, match="MinerU"):
        create_parser(app_settings)


def test_paddleocr_requires_token(app_settings):
    app_settings.parser = ParserType.PADDLEOCR
    app_settings.paddleocr_token = ""
    with pytest.raises(ParserError, match="PaddleOCR"):
        create_parser(app_settings)
