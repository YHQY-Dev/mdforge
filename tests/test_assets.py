import base64
from pathlib import Path
from unittest.mock import MagicMock

import httpx
import pytest

from mdforge.parsers.assets import (
    extract_mineru_zip_to_output,
    fetch_image_bytes,
    save_markdown_images,
    write_markdown_pages,
)
from mdforge.parsers.base import ParserError


def test_fetch_image_bytes_data_uri():
    raw = b"hello"
    b64 = base64.b64encode(raw).decode()
    data = f"data:image/png;base64,{b64}"
    assert fetch_image_bytes(MagicMock(), data) == raw


def test_fetch_image_bytes_plain_base64():
    raw = b"png-bytes"
    b64 = base64.b64encode(raw).decode()
    assert fetch_image_bytes(MagicMock(), b64) == raw


def test_fetch_image_bytes_http():
    client = MagicMock()
    response = MagicMock()
    response.content = b"from-url"
    response.raise_for_status = MagicMock()
    client.get.return_value = response
    assert fetch_image_bytes(client, "https://example.com/a.png") == b"from-url"
    client.get.assert_called_once()


def test_write_markdown_pages_merges_and_writes(tmp_path: Path):
    out = tmp_path / "out.md"
    client = MagicMock()
    count = write_markdown_pages(
        ["# A", "# B"],
        [{}, {}],
        out,
        client,
        separator="\n---\n",
    )
    assert count == 0
    text = out.read_text(encoding="utf-8")
    assert "# A" in text and "# B" in text


def test_write_markdown_pages_empty_raises(tmp_path: Path):
    with pytest.raises(ParserError, match="无 Markdown"):
        write_markdown_pages([], [], tmp_path / "x.md", MagicMock())


def test_save_markdown_images_skips_empty(tmp_path: Path):
    out = tmp_path / "doc.md"
    out.write_text("x", encoding="utf-8")
    client = MagicMock()
    assert save_markdown_images({}, out, client) == 0
    client.get.assert_not_called()


def test_extract_mineru_zip_to_output(tmp_path: Path):
    import io
    import zipfile

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("pkg/full.md", "# from zip\n")
        zf.writestr("pkg/images/a.png", b"img")
    out_md = tmp_path / "out" / "result.md"
    n = extract_mineru_zip_to_output(buf.getvalue(), out_md)
    assert out_md.read_text(encoding="utf-8") == "# from zip\n"
    assert (out_md.parent / "images" / "a.png").exists()
    assert n >= 1
