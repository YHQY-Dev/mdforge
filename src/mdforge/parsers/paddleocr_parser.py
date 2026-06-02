from __future__ import annotations

import json
import time
from pathlib import Path

import httpx
from loguru import logger

from mdforge.parsers.assets import write_markdown_pages
from mdforge.parsers.base import BaseParser, ParserError, ProgressCallback

POLL_INTERVAL = 2.0
MAX_WAIT = 3600.0

DEFAULT_OPTIONAL = {
    "useDocOrientationClassify": False,
    "useDocUnwarping": False,
    "useChartRecognition": False,
}


class PaddleOCRParser(BaseParser):
    """PaddleOCR async job API — submits the whole PDF in one request."""

    def __init__(self, token: str, job_url: str, model: str) -> None:
        if not token.strip():
            raise ParserError("请在设置中填写 PaddleOCR Token")
        self._token = token.strip()
        self._job_url = job_url.rstrip("/")
        self._model = model

    @property
    def name(self) -> str:
        return "PaddleOCR"

    def _auth_headers(self, json_mode: bool = False) -> dict[str, str]:
        h = {"Authorization": f"bearer {self._token}"}
        if json_mode:
            h["Content-Type"] = "application/json"
        return h

    def convert_pdf(
        self,
        pdf_path: Path,
        output_path: Path,
        on_progress: ProgressCallback | None = None,
    ) -> None:
        if not pdf_path.is_file():
            raise ParserError(f"文件不存在: {pdf_path}")
        timeout = httpx.Timeout(600.0, connect=60.0)
        with httpx.Client(timeout=timeout) as client:
            self._report(
                on_progress,
                f"提交整份 PDF（{pdf_path.name}），服务端异步解析…",
                0.12,
            )
            job_id = self._submit_job(client, pdf_path)
            self._report(on_progress, "等待 PaddleOCR 云端处理…", 0.25)
            json_url = self._poll_job(client, job_id, on_progress)
            self._report(on_progress, "下载 Markdown 并保存图片…", 0.82)
            img_count = self._fetch_and_save(client, json_url, output_path)
        self._report(on_progress, "转换完成", 1.0)
        logger.info("PaddleOCR 已保存: {}（{} 张图片）", output_path, img_count)

    def _submit_job(self, client: httpx.Client, pdf_path: Path) -> str:
        data = {
            "model": self._model,
            "optionalPayload": json.dumps(DEFAULT_OPTIONAL),
        }
        with pdf_path.open("rb") as f:
            files = {"file": (pdf_path.name, f, "application/pdf")}
            resp = client.post(self._job_url, headers=self._auth_headers(), data=data, files=files)
        if resp.status_code != 200:
            raise ParserError(f"提交任务失败: {resp.text[:500]}")
        body = resp.json()
        try:
            return body["data"]["jobId"]
        except (KeyError, TypeError) as exc:
            raise ParserError(f"提交任务响应异常: {body}") from exc

    def _poll_job(
        self,
        client: httpx.Client,
        job_id: str,
        on_progress: ProgressCallback | None,
    ) -> str:
        url = f"{self._job_url}/{job_id}"
        deadline = time.monotonic() + MAX_WAIT
        last_extracted = -1
        last_state = ""
        while time.monotonic() < deadline:
            resp = client.get(url, headers=self._auth_headers())
            resp.raise_for_status()
            payload = resp.json()
            data = payload.get("data") or {}
            state = data.get("state", "")
            if state == "done":
                try:
                    return data["resultUrl"]["jsonUrl"]
                except (KeyError, TypeError) as exc:
                    raise ParserError(f"任务完成但缺少结果地址: {payload}") from exc
            if state == "failed":
                raise ParserError(data.get("errorMsg") or "PaddleOCR 任务失败")
            prog = data.get("extractProgress") or {}
            total = prog.get("totalPages") or 0
            extracted = prog.get("extractedPages") or 0
            if state != last_state or extracted != last_extracted:
                last_state = state
                last_extracted = extracted
                if total:
                    pct = 0.25 + 0.55 * (extracted / total)
                    self._report(
                        on_progress,
                        f"云端处理中 {extracted}/{total} 页（非本地拆页，整份 PDF 一次提交）…",
                        pct,
                    )
                else:
                    self._report(on_progress, f"任务状态: {state}…", None)
            time.sleep(POLL_INTERVAL)
        raise ParserError("PaddleOCR 解析超时")

    def _fetch_and_save(self, client: httpx.Client, json_url: str, output_path: Path) -> int:
        resp = client.get(json_url)
        resp.raise_for_status()
        parts: list[str] = []
        images_per_part: list[dict[str, str]] = []
        for line in resp.text.strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ParserError(f"结果 JSON 行解析失败: {line[:120]}") from exc
            for res in row.get("result", {}).get("layoutParsingResults", []):
                md = res.get("markdown") or {}
                text = md.get("text", "")
                images = md.get("images") or {}
                if text or images:
                    parts.append(text)
                    images_per_part.append(images)
        if not parts:
            raise ParserError("PaddleOCR 结果中无 Markdown 内容")
        return write_markdown_pages(parts, images_per_part, output_path, client)
