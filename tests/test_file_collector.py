from pathlib import Path

import pytest

from mdforge.core.batch_paths import default_batch_output_dir, ensure_output_dir
from mdforge.core.file_collector import BatchMode, PdfJob, collect_pdfs_detailed
from mdforge.core.paths import unique_data_id

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"
NESTED = EXAMPLES / "files"


@pytest.fixture
def examples_dir():
    if not EXAMPLES.is_dir():
        pytest.skip("examples/ not available")
    return EXAMPLES


def test_default_output_folder_md(examples_dir):
    out = default_batch_output_dir(BatchMode.FLAT_FOLDER, folder_path=examples_dir)
    assert out == examples_dir.parent / f"{examples_dir.name}-md"


def test_duplicate_stem_gets_unique_output(examples_dir):
    pdfs = list(examples_dir.glob("*.pdf"))[:2]
    if len(pdfs) < 2:
        pytest.skip("need 2 pdfs")
    out = ROOT / "tests" / "_tmp_dup"
    ensure_output_dir(out)
    result = collect_pdfs_detailed(
        BatchMode.FILES,
        file_paths=[pdfs[0], pdfs[0]],
        output_dir=out,
    )
    assert len(result.jobs) == 2
    assert result.jobs[0].output_path != result.jobs[1].output_path


def test_pdf_job_unique_data_id(examples_dir):
    pdfs = list(examples_dir.glob("*.pdf"))
    if not pdfs:
        pytest.skip("need pdf")
    a = PdfJob.create(pdfs[0], Path("out/a.md"))
    b = PdfJob.create(pdfs[0], Path("out/b.md"))
    assert a.data_id == b.data_id


def test_collect_nested_reports_skips(examples_dir):
    if not NESTED.is_dir():
        pytest.skip("examples/files not available")
    out = ROOT / "tests" / "_tmp_nested"
    ensure_output_dir(out)
    result = collect_pdfs_detailed(
        BatchMode.NESTED_FOLDERS,
        folder_path=NESTED,
        output_dir=out,
    )
    assert len(result.jobs) >= 1


def test_collect_flat_folder(examples_dir):
    out = ROOT / "tests" / "_tmp_flat"
    ensure_output_dir(out)
    jobs = collect_pdfs_detailed(
        BatchMode.FLAT_FOLDER,
        folder_path=examples_dir,
        output_dir=out,
    ).jobs
    assert len(jobs) >= 1
