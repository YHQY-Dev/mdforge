from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from mdforge.core.file_collector import BatchMode, PdfJob, collect_pdfs_detailed


@dataclass
class SingleConversionRequest:
    input_path: Path
    output_path: Path


@dataclass
class BatchConversionRequest:
    mode: BatchMode
    output_dir: Path
    file_paths: list[Path] = field(default_factory=list)
    folder_path: Path | None = None
    jobs: list[PdfJob] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def prepare(self) -> list[PdfJob]:
        """Build job list once; reuse for validation and conversion."""
        if not self.jobs:
            result = collect_pdfs_detailed(
                self.mode,
                file_paths=self.file_paths,
                folder_path=self.folder_path,
                output_dir=self.output_dir,
            )
            self.jobs = result.jobs
            self.warnings = result.warnings
        return self.jobs


@dataclass
class ConversionResult:
    pdf_path: Path
    output_path: Path
    success: bool
    message: str = ""
