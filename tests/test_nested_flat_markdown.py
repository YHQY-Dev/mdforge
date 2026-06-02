from pathlib import Path

import pytest

from mdforge.core.batch_paths import (
    NESTED_FLAT_MD_DIR_NAME,
    build_nested_flat_markdown_folder,
    ensure_output_dir,
)
from mdforge.core.file_collector import BatchMode, PdfJob, collect_pdfs_detailed
from mdforge.models.conversion import ConversionResult

ROOT = Path(__file__).resolve().parents[1]
NESTED = ROOT / "examples" / "files"


def test_build_nested_flat_markdown_folder(tmp_path: Path):
    out = tmp_path / "out"
    ensure_output_dir(out)
    sub = out / "paper_a"
    sub.mkdir()
    md = sub / "doc.md"
    md.write_text("# hello", encoding="utf-8")
    pdf = tmp_path / "My Article.pdf"
    pdf.write_bytes(b"%PDF-1.4")
    job = PdfJob.create(pdf_path=pdf, output_path=md)
    results = [ConversionResult(pdf, md, True, "成功")]

    summary = build_nested_flat_markdown_folder(out, [job], results)
    assert summary is not None
    flat_dir, count = summary
    assert flat_dir.name == NESTED_FLAT_MD_DIR_NAME
    assert count == 1
    assert (flat_dir / "My Article.md").read_text(encoding="utf-8") == "# hello"


@pytest.mark.skipif(not NESTED.is_dir(), reason="examples/files not available")
def test_nested_collect_output_under_subdirs(tmp_path: Path):
    out = tmp_path / "files-md"
    result = collect_pdfs_detailed(
        BatchMode.NESTED_FOLDERS,
        folder_path=NESTED,
        output_dir=out,
    )
    assert result.jobs
    for job in result.jobs:
        assert job.output_path.parent != out
        assert job.output_path.suffix == ".md"
