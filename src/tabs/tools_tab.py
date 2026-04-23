"""Onglet Outils système et nettoyage."""

import os
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                               QFormLayout, QLineEdit, QComboBox, QListWidget,
                               QLabel, QGridLayout, QScrollArea, QMessageBox, QApplication)
from PySide6.QtCore import Qt, Signal

from src.config import Config
from src.utils import make_btn, safe_startfile, launch_system_tool
from src.shortcut_scanner import ShortcutScanner
from src.shortcut_writer import ShortcutWriter
from src.workers import EmptyBinWorker


class ToolsTab(QWidget):
    log = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self._broken_paths: list[str] = []
        self._empty_worker: Optional[EmptyBinWorker] = None
        self._build()

    def _build(self) -> None:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        inner = QWidget()
        layout = QVBoxLayout(inner)
        layout.setSpacing(10)
        layout.setContentsMargins(14, 14, 14, 14)

        # Chemins système
        g = QGroupBox("💻 Chemins système")
        gl = QFormLayout(g)

        all_paths = {}
        for key in Config.SPECIAL_PATHS:
            all_paths[key] = ShortcutScanner.get_special_path(key)
        all_paths.update(Config.SYSTEM_PATHS)

        friendly_names = {"Desktop": "Bureau", "StartMenu": "Menu Démarrer", "Startup": "Démarrage auto",
                          "TaskBar": "Barre des tâches", "SendTo": "Envoyer vers", "AppData": "AppData",
                          "Temp": "Temp", "ProgramFiles": "ProgramFiles"}

        for key, path in all_paths.items():
            row = QWidget()
            rl = QHBoxLayout(row)
            rl.setContentsMargins(0, 0, 0, 0)
            le = QLineEdit(path)
            le.setReadOnly(True)
            bo = make_btn("📂", "secondary", width=38)
            bo.clicked.connect(self._make_open_handler(path))
            bc = make_btn("📋", "secondary", width=38)
            bc.clicked.connect(self._make_copy_handler(path))
            rl.addWidget(le, 1)
            rl.addWidget(bo)
            rl.addWidget(bc)
            label = friendly_names.get(key, key)
            gl.addRow(f"📁 {label}:", row)
        layout.addWidget(g)

        # Nettoyeur de raccourcis cassés
        g2 = QGroupBox("🧹 Nettoyeur de raccourcis cassés")
        gl2 = QVBoxLayout(g2)
        info = QLabel("Scanne un dossier et détecte les raccourcis dont la cible n'existe plus.\nVous pouvez ensuite les supprimer en un clic.")
        info.setWordWrap(True)
        info.setStyleSheet("color: #a6adc8;")
        gl2.addWidget(info)

        clean_row = QHBoxLayout()
        self.clean_combo = QComboBox()
        self.clean_combo.addItems(["Bureau", "Menu Démarrer", "Démarrage auto"])
        clean_btn = make_btn("🔍 Détecter les cassés", "warning")
        clean_btn.clicked.connect(self._find_broken)
        clean_row.addWidget(self.clean_combo)
        clean_row.addWidget(clean_btn)
        gl2.addLayout(clean_row)

        self.broken_list = QListWidget()
        self.broken_list.setMaximumHeight(Config.BROKEN_LIST_HEIGHT)
        gl2.addWidget(self.broken_list)

        del_broken = make_btn("🗑️ Supprimer tous les cassés", "danger")
        del_broken.clicked.connect(self._delete_broken)
        gl2.addWidget(del_broken)
        layout.addWidget(g2)

        # Actions rapides
        g3 = QGroupBox("⚡ Actions rapides")
        gl3 = QGridLayout(g3)
        for i, (lbl, exe, args) in enumerate(Config.SYSTEM_TOOLS):
            btn = make_btn(lbl, "secondary")
            btn.clicked.connect(self._make_tool_handler(exe, args))
            gl3.addWidget(btn, i // 3, i % 3)
        b_bin = make_btn("🗑️ Vider corbeille", "secondary")
        b_bin.clicked.connect(self._empty_bin)
        gl3.addWidget(b_bin, len(Config.SYSTEM_TOOLS) // 3 + 1, 0)
        layout.addWidget(g3)

        layout.addStretch()
        scroll.setWidget(inner)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def _make_open_handler(self, path: str):
        def handler():
            if os.path.isdir(path):
                try:
                    safe_startfile(path)
                except Exception as e:
                    self.log.emit(f"❌ {e}")
            else:
                self.log.emit(f"⚠️ Dossier introuvable : {path}")
        return handler

    def _make_copy_handler(self, path: str):
        def handler():
            clipboard = QApplication.clipboard()
            if clipboard:
                clipboard.setText(path)
                self.log.emit(f"📋 Copié : {path}")
        return handler

    def _make_tool_handler(self, exe: str, args: list[str]):
        def handler():
            try:
                launch_system_tool(exe, args)
                self.log.emit(f"✅ Lancé : {exe}")
            except Exception as e:
                self.log.emit(f"❌ {exe}: {e}")
        return handler

    def _find_broken(self) -> None:
        self.broken_list.clear()
        self._broken_paths.clear()
        loc_map = {0: "Desktop", 1: "StartMenu", 2: "Startup"}
        folder = ShortcutScanner.get_special_path(loc_map[self.clean_combo.currentIndex()])
        broken = ShortcutScanner.find_broken(folder)
        for sc in broken:
            path = sc.get("path", "")
            if path:
                self._broken_paths.append(path)
                target = sc.get("target", "?")
                self.broken_list.addItem(f"💔 {Path(path).name}  →  {target}")
        count = len(self._broken_paths)
        self.log.emit(f"🧹 {count} raccourci(s) cassé(s) détecté(s)")
        if not self._broken_paths:
            QMessageBox.information(self, "Parfait", "Aucun raccourci cassé trouvé ! 🎉")

    def _delete_broken(self) -> None:
        if not self._broken_paths:
            return
        count = len(self._broken_paths)
        reply = QMessageBox.question(self, "Confirmer", f"Supprimer {count} raccourci(s) cassé(s) ?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            deleted = sum(1 for p in self._broken_paths if ShortcutWriter.delete(p))
            self.log.emit(f"🗑️ {deleted} raccourci(s) cassé(s) supprimé(s)")
            self.broken_list.clear()
            self._broken_paths.clear()

    def _empty_bin(self) -> None:
        if self._empty_worker and self._empty_worker.isRunning():
            return
        reply = QMessageBox.question(self, "Confirmer", "Vider la corbeille ?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            return
        self._empty_worker = EmptyBinWorker()
        self._empty_worker.finished.connect(self._on_empty_finished)
        self._empty_worker.start()
        self.log.emit("🗑️ Vidage de la corbeille en cours...")

    def _on_empty_finished(self, success: bool, message: str) -> None:
        if success:
            self.log.emit(f"✅ {message}")
        else:
            self.log.emit(f"❌ {message}")
        self._empty_worker = None