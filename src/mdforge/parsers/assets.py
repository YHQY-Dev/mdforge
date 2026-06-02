from __future__ import annotations

import base64
import io
import shutil
import tempfile
import zipfile
from pathlib import Path

import httpx

from mdforge.parsers.base import ParserError


def fetch_image_bytes(client: httpx.Client, src: str) -> bytes:
    """Download image from URL or decode base64 / data-URI."""
    if src.startswith(("http://", "https://")):
        resp = client.get(src, timeout=120.0)
        resp.raise_for_status()
        return resp.content
    if src.startswith("data:"):
        payload = src.split(",", 1)[-1]
        return base64.b64decode(payload)
    try:
        return base64.b64decode(src)
    except Exception as exc:
        raise ParserError(f"无法解析图片数据: {exc}") from exc


def save_markdown_images(
    images: dict[str, str],
    output_md: Path,
    client: httpx.Client,
) -> int:
    """Save markdown.images dict beside the .md file; return count saved."""
    if not images:
        return 0
    base_dir = output_md.parent
    count = 0
    for rel_path, src in images.items():
        if not rel_path or not src:
            continue
        dest = base_dir / rel_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(fetch_image_bytes(client, src))
        count += 1
    return count


def write_markdown_pages(
    parts: list[str],
    images_per_part: list[dict[str, str]],
    output_md: Path,
    client: httpx.Client,
    *,
    separator: str = "\n\n---\n\n",
) -> int:
    """Merge per-page markdown from API JSON, download images, write one .md file."""
    output_md.parent.mkdir(parents=True, exist_ok=True)
    total_images = 0
    for imgs in images_per_part:
        total_images += save_markdown_images(imgs, output_md, client)
    body = separator.join(p for p in parts if p and p.strip())
    if not body.strip():
        raise ParserError("无 Markdown 文本内容")
    output_md.write_text(body, encoding="utf-8")
    return total_images


def extract_mineru_zip_to_output(zip_bytes: bytes, output_md: Path) -> int:
    """Extract MinerU zip: write full.md and copy asset folders next to output_md."""
    output_md.parent.mkdir(parents=True, exist_ok=True)
    asset_count = 0
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
            zf.extractall(tmp_path)
        full_md = next(tmp_path.rglob("full.md"), None)
        if full_md is None:
            md_files = list(tmp_path.rglob("*.md"))
            if not md_files:
                raise ParserError("结果压缩包中未找到 Markdown 文件")
            full_md = md_files[0]
        md_text = full_md.read_text(encoding="utf-8")
        for item in full_md.parent.iterdir():
            if item.resolve() == full_md.resolve():
                continue
            dest = output_md.parent / item.name
            if item.is_dir():
                shutil.copytree(item, dest, dirs_exist_ok=True)
                asset_count += sum(1 for _ in dest.rglob("*") if _.is_file())
            else:
                shutil.copy2(item, dest)
                asset_count += 1
        output_md.write_text(md_text, encoding="utf-8")
    return asset_count
