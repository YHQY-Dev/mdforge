from __future__ import annotations

import os
from enum import StrEnum
from pathlib import Path

from dotenv import load_dotenv
from PySide6.QtCore import QSettings

ORG = "MdForge"
APP = "MdForge"


class ParserType(StrEnum):
    MARKITDOWN = "markitdown"
    MINERU = "mineru"
    PADDLEOCR = "paddleocr"


class AppSettings:
    """Persistent settings via QSettings."""

    def __init__(self) -> None:
        self._qs = QSettings(ORG, APP)
        self._load_env_defaults()

    def _load_env_defaults(self) -> None:
        env_path = Path.cwd() / ".env"
        if env_path.exists():
            load_dotenv(env_path)
        if not self.mineru_token and os.getenv("MinerU_TOKEN"):
            self.mineru_token = os.getenv("MinerU_TOKEN", "").strip().strip('"')
        if not self.paddleocr_token and os.getenv("PaddleOCR_TOKEN"):
            self.paddleocr_token = os.getenv("PaddleOCR_TOKEN", "").strip().strip('"')

    def _get(self, key: str, default: str = "") -> str:
        v = self._qs.value(key, default)
        return str(v) if v is not None else default

    def _set(self, key: str, value: str) -> None:
        self._qs.setValue(key, value)

    @property
    def parser(self) -> ParserType:
        raw = self._get("parser", ParserType.MARKITDOWN)
        try:
            return ParserType(raw)
        except ValueError:
            return ParserType.MARKITDOWN

    @parser.setter
    def parser(self, value: ParserType | str) -> None:
        self._set("parser", str(value))

    @property
    def mineru_token(self) -> str:
        return self._get("mineru_token")

    @mineru_token.setter
    def mineru_token(self, value: str) -> None:
        self._set("mineru_token", value)

    @property
    def mineru_base_url(self) -> str:
        return self._get("mineru_base_url", "https://mineru.net") or "https://mineru.net"

    @mineru_base_url.setter
    def mineru_base_url(self, value: str) -> None:
        self._set("mineru_base_url", value.rstrip("/"))

    @property
    def mineru_model_version(self) -> str:
        return self._get("mineru_model_version", "vlm") or "vlm"

    @mineru_model_version.setter
    def mineru_model_version(self, value: str) -> None:
        self._set("mineru_model_version", value)

    @property
    def paddleocr_token(self) -> str:
        return self._get("paddleocr_token")

    @paddleocr_token.setter
    def paddleocr_token(self, value: str) -> None:
        self._set("paddleocr_token", value)

    @property
    def paddleocr_job_url(self) -> str:
        return (
            self._get("paddleocr_job_url", "https://paddleocr.aistudio-app.com/api/v2/ocr/jobs")
            or "https://paddleocr.aistudio-app.com/api/v2/ocr/jobs"
        )

    @paddleocr_job_url.setter
    def paddleocr_job_url(self, value: str) -> None:
        self._set("paddleocr_job_url", value.rstrip("/"))

    @property
    def paddleocr_model(self) -> str:
        return self._get("paddleocr_model", "PaddleOCR-VL-1.6") or "PaddleOCR-VL-1.6"

    @paddleocr_model.setter
    def paddleocr_model(self, value: str) -> None:
        self._set("paddleocr_model", value)

    @property
    def last_input_dir(self) -> str:
        return self._get("last_input_dir")

    @last_input_dir.setter
    def last_input_dir(self, value: str) -> None:
        self._set("last_input_dir", value)

    @property
    def last_output_dir(self) -> str:
        return self._get("last_output_dir")

    @last_output_dir.setter
    def last_output_dir(self, value: str) -> None:
        self._set("last_output_dir", value)

    def sync(self) -> None:
        self._qs.sync()
