from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path

from mdforge.core.paths import unique_data_id


class BatchMode(StrEnum):
    FILES = "files"
    FLAT_FOLDER = "flat_folder"
    NESTED_FOLDERS = "nested_folders"


@dataclass(frozen=True)
class PdfJob:
    """One PDF and its intended output Markdown path."""

    pdf_path: Path
    output_path: Path
    data_id: str

    @classmethod
    def create(cls, pdf_path: Path, output_path: Path) -> PdfJob:
        return cls(pdf_path=pdf_path, output_path=output_path, data_id=unique_data_id(pdf_path))


@dataclass
class CollectResult:
    jobs: list[PdfJob]
    warnings: list[str] = field(default_factory=list)


def _unique_md_path(output_dir: Path, stem: str, used: dict[str, int]) -> Path:
    count = used.get(stem, 0)
    used[stem] = count + 1
    if count == 0:
        return output_dir / f"{stem}.md"
    return output_dir / f"{stem}_{count + 1}.md"


def collect_pdfs(
    mode: BatchMode,
    *,
    file_paths: list[Path] | None = None,
    folder_path: Path | None = None,
    output_dir: Path,
) -> list[PdfJob]:
    return collect_pdfs_detailed(
        mode,
        file_paths=file_paths,
        folder_path=folder_path,
        output_dir=output_dir,
    ).jobs


def collect_pdfs_detailed(
    mode: BatchMode,
    *,
    file_paths: list[Path] | None = None,
    folder_path: Path | None = None,
    output_dir: Path,
) -> CollectResult:
    """Collect PDF jobs and return warnings for skipped inputs."""
    jobs: list[PdfJob] = []
    warnings: list[str] = []
    used_stems: dict[str, int] = {}

    if mode == BatchMode.FILES:
        if not file_paths:
            return CollectResult(jobs, warnings)
        for pdf in file_paths:
            pdf = Path(pdf)
            if pdf.suffix.lower() != ".pdf":
                warnings.append(f"已跳过非 PDF：{pdf}")
                continue
            if not pdf.is_file():
                warnings.append(f"已跳过不存在文件：{pdf}")
                continue
            out = _unique_md_path(output_dir, pdf.stem, used_stems)
            if used_stems[pdf.stem] > 1:
                warnings.append(f"重名 PDF，输出为：{out.name}（{pdf.name}）")
            jobs.append(PdfJob.create(pdf_path=pdf, output_path=out))

    elif mode == BatchMode.FLAT_FOLDER:
        if not folder_path or not folder_path.is_dir():
            return CollectResult(jobs, warnings)
        pdfs = sorted(p for p in folder_path.glob("*.pdf") if p.is_file())
        if not pdfs:
            warnings.append(f"文件夹内无 PDF：{folder_path}")
        for pdf in pdfs:
            out = _unique_md_path(output_dir, pdf.stem, used_stems)
            jobs.append(PdfJob.create(pdf_path=pdf, output_path=out))

    elif mode == BatchMode.NESTED_FOLDERS:
        if not folder_path or not folder_path.is_dir():
            return CollectResult(jobs, warnings)
        for sub in sorted(folder_path.iterdir()):
            if not sub.is_dir():
                continue
            pdfs = [p for p in sub.glob("*.pdf") if p.is_file()]
            if len(pdfs) == 0:
                warnings.append(f"已跳过（无 PDF）：{sub.name}/")
                continue
            if len(pdfs) > 1:
                warnings.append(f"已跳过（多个 PDF）：{sub.name}/")
                continue
            pdf = pdfs[0]
            rel = Path(sub.name) / f"{pdf.stem}.md"
            jobs.append(PdfJob.create(pdf_path=pdf, output_path=output_dir / rel))

    return CollectResult(jobs, warnings)
