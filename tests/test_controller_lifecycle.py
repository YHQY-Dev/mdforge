"""Regression: controller must remain alive (QObject parent or window.controllers)."""

import gc
import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from mdforge.controllers.single_controller import SingleController
from mdforge.core.settings import AppSettings, ParserType
from mdforge.services.conversion_service import ConversionService
from mdforge.views.main_window import MainWindow


def test_convert_with_qobject_parent_works(qtbot):
    """Controller parented to MainWindow must handle clicks (no Python ref required)."""
    app = QApplication.instance() or QApplication(sys.argv)
    settings = AppSettings()
    settings.parser = ParserType.MARKITDOWN
    svc = ConversionService(settings)
    w = MainWindow()
    SingleController(w, settings, svc)
    gc.collect()
    pdfs = list(Path("examples").glob("*.pdf"))
    assert pdfs
    w.single_page.input_picker.set_path(str(pdfs[0]))
    w.single_page.output_picker.set_path(str(pdfs[0].with_suffix(".md")))
    QTest.mouseClick(w.single_page.convert_btn, Qt.MouseButton.LeftButton)
    qtbot.waitUntil(lambda: "开始转换" in w.single_page.log.toPlainText(), timeout=2000)


def test_convert_with_window_controllers_list(qtbot):
    app = QApplication.instance() or QApplication(sys.argv)
    settings = AppSettings()
    settings.parser = ParserType.MARKITDOWN
    svc = ConversionService(settings)
    w = MainWindow()
    w.controllers = [SingleController(w, settings, svc)]
    pdfs = list(Path("examples").glob("*.pdf"))
    assert pdfs
    w.single_page.input_picker.set_path(str(pdfs[0]))
    w.single_page.output_picker.set_path(str(pdfs[0].with_suffix(".md")))
    QTest.mouseClick(w.single_page.convert_btn, Qt.MouseButton.LeftButton)
    qtbot.waitUntil(lambda: "开始转换" in w.single_page.log.toPlainText(), timeout=2000)
