from __future__ import annotations

import shutil
from pathlib import Path

from mdforge.core.file_collector import BatchMode, PdfJob
from mdforge.models.conversion import ConversionResult

# Flat folder of .md only, created under output_dir after nested batch conversion.
NESTED_FLAT_MD_DIR_NAME = "markdown"


def default_batch_output_dir(
    mode: BatchMode,
    *,
    folder_path: Path | None = None,
    file_paths: list[Path] | None = None,
) -> Path | None:
    """Suggest output directory; for folder modes use sibling ``{name}-md``."""
    if mode in (BatchMode.FLAT_FOLDER, BatchMode.NESTED_FOLDERS) and folder_path:
        return folder_path.parent / f"{folder_path.name}-md"
    if mode == BatchMode.FILES and file_paths:
        parent = file_paths[0].parent
        return parent / f"{parent.name}-md"
    return None


def ensure_output_dir(path: Path) -> Path:
    """Create output directory only when conversion starts."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def _flat_md_name(job: PdfJob) -> str:
    """Use source PDF file name (stem) for the flat copy."""
    return f"{job.pdf_path.stem}.md"


def build_nested_flat_markdown_folder(
    output_dir: Path,
    jobs: list[PdfJob],
    results: list[ConversionResult],
) -> tuple[Path, int] | None:
    """
    Copy successful nested-mode Markdown files into ``output_dir/markdown/``.

    Each file is named after its source PDF (e.g. ``1274/report.pdf`` → ``markdown/report.md``).
    """
    ok_by_pdf = {r.pdf_path: r for r in results if r.success}
    if not ok_by_pdf:
        return None

    flat_dir = output_dir / NESTED_FLAT_MD_DIR_NAME
    flat_dir.mkdir(parents=True, exist_ok=True)
    used_names: dict[str, int] = {}
    copied = 0

    for job in jobs:
        result = ok_by_pdf.get(job.pdf_path)
        if not result or not result.output_path.is_file():
            continue
        base = _flat_md_name(job)
        stem = Path(base).stem
        count = used_names.get(stem, 0)
        used_names[stem] = count + 1
        name = base if count == 0 else f"{stem}_{count + 1}.md"
        shutil.copy2(result.output_path, flat_dir / name)
        copied += 1

    if copied == 0:
        return None
    return flat_dir, copied
