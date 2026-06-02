from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from mdforge.core.bootstrap import configure_warnings, setup_app_font
from mdforge.controllers.batch_controller import BatchController
from mdforge.controllers.settings_controller import SettingsController
from mdforge.controllers.single_controller import SingleController
from mdforge.core.logging_config import setup_logging
from mdforge.core.settings import AppSettings
from mdforge.services.conversion_service import ConversionService
from mdforge.views.main_window import MainWindow


def run() -> int:
    configure_warnings()
    setup_logging()
    app = QApplication(sys.argv)
    setup_app_font(app)
    from mdforge.views.styles import APP_STYLESHEET

    app.setStyleSheet(APP_STYLESHEET)
    app.setApplicationName("MdForge")
    app.setOrganizationName("MdForge")

    settings = AppSettings()
    service = ConversionService(settings)
    window = MainWindow()
    # Controllers must stay alive; QObject parent=window also pins them in the Qt tree.
    window.controllers = [
        SettingsController(window, settings),
        SingleController(window, settings, service),
        BatchController(window, settings, service),
    ]
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(run())
