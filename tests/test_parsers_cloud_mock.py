from pathlib import Path
from unittest.mock import MagicMock

import pytest

from mdforge.core.file_collector import PdfJob
from mdforge.parsers.mineru_parser import MinerUParser
from mdforge.parsers.paddleocr_parser import PaddleOCRParser


def test_mineru_request_batch_upload_parses_response():
    parser = MinerUParser("token", "https://mineru.test", "vlm")
    job = PdfJob.create(Path("a.pdf"), Path("out/a.md"))
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = {
        "code": 0,
        "data": {"batch_id": "b1", "file_urls": ["https://upload/1"]},
    }
    client = MagicMock()
    client.post.return_value = mock_resp

    batch_id, urls = parser._request_batch_upload(client, [job])
    assert batch_id == "b1"
    assert urls == ["https://upload/1"]
    client.post.assert_called_once()


def test_paddleocr_submit_job_parses_job_id(tmp_path: Path):
    parser = PaddleOCRParser("tok", "https://paddle.test/jobs", "model-x")
    pdf = tmp_path / "doc.pdf"
    pdf.write_bytes(b"%PDF-1.4")
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"data": {"jobId": "job-42"}}
    client = MagicMock()
    client.post.return_value = mock_resp
    job_id = parser._submit_job(client, pdf)
    assert job_id == "job-42"


def test_paddleocr_poll_job_done_returns_json_url():
    parser = PaddleOCRParser("tok", "https://paddle.test/jobs", "model-x")
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = {
        "data": {
            "state": "done",
            "resultUrl": {"jsonUrl": "https://result/out.jsonl"},
        }
    }
    client = MagicMock()
    client.get.return_value = mock_resp
    url = parser._poll_job(client, "job-42", None)
    assert url == "https://result/out.jsonl"


def test_paddleocr_poll_job_failed_raises():
    parser = PaddleOCRParser("tok", "https://paddle.test/jobs", "model-x")
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = {
        "data": {"state": "failed", "errorMsg": "boom"},
    }
    client = MagicMock()
    client.get.return_value = mock_resp
    from mdforge.parsers.base import ParserError

    with pytest.raises(ParserError, match="boom"):
        parser._poll_job(client, "job-42", None)
