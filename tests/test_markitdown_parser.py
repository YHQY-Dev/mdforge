from pathlib import Path

import pytest

from mdforge.parsers.markitdown_parser import MarkItDownParser

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"


@pytest.mark.skipif(not EXAMPLES.is_dir(), reason="examples not available")
def test_markitdown_convert_example_pdf():
    pdfs = list(EXAMPLES.glob("*.pdf"))
    if not pdfs:
        pytest.skip("no pdf in examples")
    pdf = pdfs[0]
    out = ROOT / "tests" / "_tmp_single.md"
    parser = MarkItDownParser()
    parser.convert_pdf(pdf, out)
    assert out.is_file()
    assert len(out.read_text(encoding="utf-8")) > 50
