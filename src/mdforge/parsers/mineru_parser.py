from __future__ import annotations

import time
from collections.abc import Callable
from pathlib import Path

import httpx
from loguru import logger

from mdforge.core.file_collector import PdfJob
from mdforge.models.conversion import ConversionResult
from mdforge.parsers.assets import extract_mineru_zip_to_output
from mdforge.parsers.base import BaseParser, ParserError, ProgressCallback

POLL_INTERVAL = 3.0
MAX_WAIT = 3600.0
BATCH_CHUNK = 50


class MinerUParser(BaseParser):
    """MinerU: batch upload PDFs → poll → extract zip with images."""

    def __init__(self, token: str, base_url: str, model_version: str) -> None:
        if not token.strip():
            raise ParserError("请在设置中填写 MinerU Token")
        self._token = token.strip()
        self._base = base_url.rstrip("/")
        self._model = model_version

    @property
    def name(self) -> str:
        return "MinerU"

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
        }

    def convert_pdf(
        self,
        pdf_path: Path,
        output_path: Path,
        on_progress: ProgressCallback | None = None,
    ) -> None:
        if not pdf_path.is_file():
            raise ParserError(f"文件不存在: {pdf_path}")
        job = PdfJob.create(pdf_path=pdf_path, output_path=output_path)
        results = self.convert_jobs([job], on_progress=on_progress)
        if not results[0].success:
            raise ParserError(results[0].message)

    def convert_jobs(
        self,
        jobs: list[PdfJob],
        on_progress: ProgressCallback | None = None,
        on_file_done: Callable[[ConversionResult], None] | None = None,
        should_cancel: Callable[[], bool] | None = None,
    ) -> list[ConversionResult]:
        if not jobs:
            return []
        timeout = httpx.Timeout(600.0, connect=60.0)
        results: list[ConversionResult] = []
        total = len(jobs)
        with httpx.Client(timeout=timeout) as client:
            for chunk_idx in range(0, total, BATCH_CHUNK):
                if should_cancel and should_cancel():
                    break
                chunk = jobs[chunk_idx : chunk_idx + BATCH_CHUNK]
                chunk_no = chunk_idx // BATCH_CHUNK + 1
                chunk_total = (total + BATCH_CHUNK - 1) // BATCH_CHUNK
                self._report(
                    on_progress,
                    f"MinerU 批量上传 {len(chunk)} 个 PDF（批次 {chunk_no}/{chunk_total}）…",
                    chunk_idx / total,
                )
                batch_id, upload_urls = self._request_batch_upload(client, chunk)
                for i, job in enumerate(chunk):
                    self._upload_file(client, upload_urls[i], job.pdf_path)
                self._report(on_progress, "等待 MinerU 云端批量解析…", chunk_idx / total + 0.05)
                chunk_results = self._poll_batch_chunk(
                    client,
                    batch_id,
                    chunk,
                    on_progress,
                    chunk_idx,
                    total,
                )
                for r in chunk_results:
                    results.append(r)
                    if on_file_done:
                        on_file_done(r)
        return results

    def _request_batch_upload(
        self, client: httpx.Client, jobs: list[PdfJob]
    ) -> tuple[str, list[str]]:
        url = f"{self._base}/api/v4/file-urls/batch"
        payload = {
            "files": [
                {"name": j.pdf_path.name, "data_id": j.data_id[:128]} for j in jobs
            ],
            "model_version": self._model,
        }
        resp = client.post(url, headers=self._headers(), json=payload)
        resp.raise_for_status()
        body = resp.json()
        if body.get("code") != 0:
            raise ParserError(body.get("msg", "申请上传链接失败"))
        data = body["data"]
        urls = data["file_urls"]
        if len(urls) != len(jobs):
            raise ParserError("上传链接数量与文件不一致")
        return data["batch_id"], urls

    def _upload_file(self, client: httpx.Client, upload_url: str, pdf_path: Path) -> None:
        with pdf_path.open("rb") as f:
            resp = client.put(upload_url, content=f.read())
        if resp.status_code != 200:
            raise ParserError(f"{pdf_path.name} 上传失败: HTTP {resp.status_code}")

    def _poll_batch_chunk(
        self,
        client: httpx.Client,
        batch_id: str,
        jobs: list[PdfJob],
        on_progress: ProgressCallback | None,
        done_offset: int,
        total_jobs: int,
    ) -> list[ConversionResult]:
        url = f"{self._base}/api/v4/extract-results/batch/{batch_id}"
        deadline = time.monotonic() + MAX_WAIT
        id_to_job = {j.data_id: j for j in jobs}
        name_to_job = {j.pdf_path.name: j for j in jobs}
        finished: dict[str, ConversionResult] = {}
        last_sig = ""

        def resolve_job(item: dict) -> PdfJob | None:
            did = item.get("data_id")
            if did and did in id_to_job:
                return id_to_job[did]
            fname = item.get("file_name", "")
            return name_to_job.get(fname)

        while time.monotonic() < deadline:
            resp = client.get(url, headers=self._headers())
            try:
                resp.raise_for_status()
            except httpx.HTTPStatusError as exc:
                raise ParserError(f"查询任务失败: HTTP {exc.response.status_code}") from exc
            body = resp.json()
            if body.get("code") != 0:
                raise ParserError(body.get("msg", "查询任务失败"))
            items = body.get("data", {}).get("extract_result", [])
            if isinstance(items, dict):
                items = [items]

            done_count = len(finished)
            running_msg = ""
            for item in items:
                job = resolve_job(item)
                if not job:
                    continue
                key = job.data_id
                if key in finished:
                    continue
                state = item.get("state", "")
                if state == "done":
                    try:
                        zip_url = item.get("full_zip_url")
                        if not zip_url:
                            raise ParserError("未返回下载地址")
                        job.output_path.parent.mkdir(parents=True, exist_ok=True)
                        asset_n = self._download_and_extract(client, zip_url, job.output_path)
                        finished[key] = ConversionResult(job.pdf_path, job.output_path, True, "成功")
                        logger.info("MinerU 已保存: {}（{} 资源）", job.output_path, asset_n)
                    except Exception as exc:
                        finished[key] = ConversionResult(
                            job.pdf_path, job.output_path, False, str(exc)
                        )
                elif state == "failed":
                    finished[key] = ConversionResult(
                        job.pdf_path,
                        job.output_path,
                        False,
                        item.get("err_msg") or "解析失败",
                    )
                elif state == "running":
                    prog = item.get("extract_progress") or {}
                    t = prog.get("total_pages") or 0
                    d = prog.get("extracted_pages") or 0
                    if t:
                        running_msg = (
                            f"{job.pdf_path.name}：云端处理 {d}/{t} 页（整份 PDF 已上传）"
                        )

            done_count = len(finished)
            sig = f"{done_count}|{running_msg}"
            if sig != last_sig:
                last_sig = sig
                pct = (done_offset + done_count) / total_jobs
                msg = f"批次进度 {done_offset + done_count}/{total_jobs}"
                if running_msg:
                    msg += f"（{running_msg}）"
                self._report(on_progress, msg, pct)

            if done_count >= len(jobs):
                break
            time.sleep(POLL_INTERVAL)

        results: list[ConversionResult] = []
        for job in jobs:
            if job.data_id in finished:
                results.append(finished[job.data_id])
            else:
                results.append(
                    ConversionResult(job.pdf_path, job.output_path, False, "MinerU 解析超时")
                )
        return results

    def _download_and_extract(
        self, client: httpx.Client, zip_url: str, output_path: Path
    ) -> int:
        resp = client.get(zip_url)
        resp.raise_for_status()
        return extract_mineru_zip_to_output(resp.content, output_path)
