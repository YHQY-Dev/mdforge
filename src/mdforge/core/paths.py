from __future__ import annotations

import hashlib
from pathlib import Path


def normalize_path(text: str) -> str:
    return text.strip().strip('"')


def to_path(text: str) -> Path:
    return Path(normalize_path(text))


def unique_data_id(pdf_path: Path) -> str:
    """Stable unique id for cloud APIs (path hash + stem)."""
    digest = hashlib.sha256(str(pdf_path.resolve()).encode("utf-8")).hexdigest()[:12]
    stem = pdf_path.stem[:80] or "pdf"
    return f"{stem}_{digest}"
