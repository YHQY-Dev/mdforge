from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Callable

ProgressCallback = Callable[[str, float | None], None]


class ParserError(Exception):
    """Raised when PDF parsing fails."""


class BaseParser(ABC):
    """Abstract PDF → Markdown parser."""

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def convert_pdf(
        self,
        pdf_path: Path,
        output_path: Path,
        on_progress: ProgressCallback | None = None,
    ) -> None:
        """Convert one PDF file to Markdown at output_path."""

    def _report(self, on_progress: ProgressCallback | None, msg: str, pct: float | None = None) -> None:
        if on_progress:
            on_progress(msg, pct)
