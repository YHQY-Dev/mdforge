from __future__ import annotations

import pytest


class FakeQSettings:
    def __init__(self) -> None:
        self._data: dict[str, object] = {}

    def value(self, key: str, default=None):
        if key in self._data:
            return self._data[key]
        return default

    def setValue(self, key: str, value) -> None:
        self._data[key] = value

    def sync(self) -> None:
        pass


@pytest.fixture
def app_settings(monkeypatch):
    monkeypatch.setattr(
        "mdforge.core.settings.QSettings",
        lambda *_args, **_kwargs: FakeQSettings(),
    )
    from mdforge.core.settings import AppSettings

    return AppSettings()
