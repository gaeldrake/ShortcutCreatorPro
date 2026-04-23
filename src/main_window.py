"""Fenêtre principale de l'application."""

import os
from pathlib import Path
from datetime import datetime
from typing import Optional

from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QLabel, QTabWidget, QTextEdit, QGroupBox,
                               QMessageBox, QFileDialog, QSystemTrayIcon, QMenu,
                               QApplication)   # <--- AJOUT
from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QAction, QFont

from src.config import Config
from src.themes import DARK_THEME, LIGHT_THEME
from src.datastore import DataStore
from src.tabs.create_tab import CreateTab
from src.tabs.batch_tab import BatchTab
from src.tabs.manage_tab import ManageTab
from src.tabs.templates_tab import TemplatesTab
from src.tabs.history_tab import HistoryTab
from src.tabs.tools_tab import ToolsTab


class MainWindow(QMainWindow):
    def __init__(self, store: DataStore) -> None:
        super().__init__()
        self.store = store
        self.is_dark = self.store.get_setting("dark_theme", True)

        self.setWindowTitle(Config.WINDOW_TITLE)
        self.setMinimumSize(Config.MIN_WINDOW_WIDTH, Config.MIN_WINDOW_HEIGHT)
        self.resize(Config.DEFAULT_WINDOW_WIDTH, Config.DEFAULT_WINDOW_HEIGHT)

        self.tray: Optional[QSystemTrayIcon] = None

        self._build_ui()
        self._build_menu()
        self._build_tray()
        self._connect()
        self._update_status()

        # Remplacer app.aboutToQuit par QApplication.instance().aboutToQuit
        app = QApplication.instance()
        if app:
            app.aboutToQuit.connect(self._cleanup)

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        ml = QVBoxLayout(central)
        ml.setContentsMargins(6, 6, 6, 6)
        ml.setSpacing(4)

        # Header
        header = QLabel(f"🔗 {Config.APP_NAME}")
        header.setObjectName("header_label")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ml.addWidget(header)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)

        self.tab_create = CreateTab(self.store)
        self.tab_batch = BatchTab(self.store)
        self.tab_manage = ManageTab()
        self.tab_templates = TemplatesTab(self.store)
        self.tab_history = HistoryTab(self.store)
        self.tab_tools = ToolsTab()

        self.tabs.addTab(self.tab_create, "✨ Créer")
        self.tabs.addTab(self.tab_batch, "📦 Batch")
        self.tabs.addTab(self.tab_manage, "🔍 Gérer")
        self.tabs.addTab(self.tab_templates, "📋 Modèles")
        self.tabs.addTab(self.tab_history, "🕐 Historique")
        self.tabs.addTab(self.tab_tools, "🛠️ Outils")

        ml.addWidget(self.tabs)

        # Log console
        g = QGroupBox("📜 Journal")
        gl = QVBoxLayout(g)
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMaximumHeight(Config.LOG_PANEL_HEIGHT)
        gl.addWidget(self.log_output)
        ml.addWidget(g)

    def _build_menu(self) -> None:
        mb = self.menuBar()

        fm = mb.addMenu("📁 &Fichier")
        a_new = QAction("✨ Nouveau raccourci", self)
        a_new.setShortcut("Ctrl+N")
        a_new.triggered.connect(lambda: self.tabs.setCurrentIndex(0))
        fm.addAction(a_new)

        a_batch = QAction("📦 Batch", self)
        a_batch.setShortcut("Ctrl+B")
        a_batch.triggered.connect(lambda: self.tabs.setCurrentIndex(1))
        fm.addAction(a_batch)

        fm.addSeparator()
        a_export = QAction("📤 Exporter config…", self)
        a_export.triggered.connect(self._export)
        fm.addAction(a_export)

        a_import = QAction("📥 Importer config…", self)
        a_import.triggered.connect(self._import)
        fm.addAction(a_import)

        fm.addSeparator()
        a_quit = QAction("🚪 Quitter", self)
        a_quit.setShortcut("Ctrl+Q")
        a_quit.triggered.connect(self.close)
        fm.addAction(a_quit)

        vm = mb.addMenu("🎨 &Affichage")
        self.theme_action = QAction("☀️ Thème clair", self)
        self.theme_action.setCheckable(True)
        self.theme_action.setChecked(not self.is_dark)
        self.theme_action.triggered.connect(self._toggle_theme)
        vm.addAction(self.theme_action)

        hm = mb.addMenu("❓ &Aide")
        a_about = QAction("ℹ️ À propos", self)
        a_about.triggered.connect(self._about)
        hm.addAction(a_about)

    def _build_tray(self) -> None:
        self.tray = QSystemTrayIcon(self)
        self.tray.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_DesktopIcon))
        self.tray.setToolTip(Config.APP_NAME)

        menu = QMenu()
        a_show = QAction("Afficher", self)
        a_show.triggered.connect(self.showNormal)
        menu.addAction(a_show)
        a_quit = QAction("Quitter", self)
        a_quit.triggered.connect(self.close)
        menu.addAction(a_quit)

        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self._on_tray_click)
        self.tray.show()

    def _on_tray_click(self, reason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.showNormal()
            self.activateWindow()

    def _connect(self) -> None:
        all_tabs = (self.tab_create, self.tab_batch, self.tab_manage,
                    self.tab_templates, self.tab_history, self.tab_tools)
        for tab in all_tabs:
            tab.log.connect(self._log)

        self.tab_create.shortcut_created.connect(lambda _: self.tab_history.refresh())
        self.tab_create.shortcut_created.connect(lambda _: self._update_status())
        self.tab_create.request_template_refresh.connect(self.tab_templates.refresh)
        self.tab_templates.template_selected.connect(self._load_template)

    def _load_template(self, data: dict) -> None:
        self.tab_create.load_data(data)
        self.tabs.setCurrentIndex(0)
        self._log(f"📋 Modèle chargé : {data.get('name', '?')}")

    def _log(self, msg: str) -> None:
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_output.append(f"[{ts}] {msg}")
        self.statusBar().showMessage(msg, 5000)
        # Pas de logger externe pour éviter les erreurs

    def _update_status(self) -> None:
        total = len(self.store.data.get("history", []))
        parts = ["✅ Prêt"]
        try:
            from src.shortcut_writer import HAS_WIN32
            if HAS_WIN32:
                parts.append("Modules Windows OK")
            else:
                parts.append("⚠️ pywin32 manquant")
        except ImportError:
            parts.append("⚠️ pywin32 non vérifié")
        parts.append(f"{total} raccourci(s) créé(s) au total")
        self.statusBar().showMessage(" — ".join(parts))

    def _toggle_theme(self, checked: bool) -> None:
        self.is_dark = not checked
        self.store.set_setting("dark_theme", self.is_dark)
        app = QApplication.instance()
        if app:
            app.setStyleSheet(DARK_THEME if self.is_dark else LIGHT_THEME)
        self.theme_action.setText("☀️ Thème clair" if self.is_dark else "🌙 Thème sombre")

    def _export(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Exporter", "shortcut_creator_backup.json", "JSON (*.json)")
        if path:
            try:
                self.store.export_to(path)
                self._log(f"📤 Config exportée : {path}")
                QMessageBox.information(self, "Succès", "Configuration exportée !")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", str(e))

    def _import(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Importer", "", "JSON (*.json)")
        if path:
            try:
                self.store.import_from(path)
                self.tab_templates.refresh()
                self.tab_history.refresh()
                self._log(f"📥 Config importée : {path}")
                QMessageBox.information(self, "Succès", "Configuration importée !")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", str(e))

    def _about(self) -> None:
        QMessageBox.about(self, "À propos",
                          f"<h2>🔗 {Config.APP_NAME} v{Config.APP_VERSION}</h2>"
                          "<p>Créateur et gestionnaire complet de raccourcis Windows.</p>"
                          "<ul><li>Création multi-emplacements</li><li>Batch avec drag & drop (threaded)</li>"
                          "<li>Éditeur de raccourcis existants</li><li>Nettoyeur de raccourcis cassés</li>"
                          "<li>Modèles et historique persistants</li><li>Export / Import de configuration</li>"
                          "<li>Thème clair / sombre (Catppuccin)</li><li>System tray</li>"
                          "<li>Validation et sécurité renforcées</li></ul><p>PySide6 + pywin32</p>")

    def _cleanup(self) -> None:
        if self.tray:
            self.tray.hide()
            self.tray = None

    def closeEvent(self, event) -> None:
        if self.tab_create.has_unsaved():
            reply = QMessageBox.question(self, "Quitter ?",
                                         "Le formulaire contient des données non enregistrées.\nVoulez-vous vraiment quitter ?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.No:
                event.ignore()
                return
        self._cleanup()
        event.accept()