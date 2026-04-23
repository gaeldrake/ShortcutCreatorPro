#!/usr/bin/env python3
"""Point d'entrée de l'application Shortcut Creator Pro."""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont
from src.config import Config
from src.themes import DARK_THEME, LIGHT_THEME
from src.datastore import DataStore
from src.main_window import MainWindow


def main() -> None:
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setFont(QFont("Segoe UI", 10))

    store = DataStore(Config.CONFIG_PATH)
    is_dark = store.get_setting("dark_theme", True)
    app.setStyleSheet(DARK_THEME if is_dark else LIGHT_THEME)

    window = MainWindow(store)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
