"""Onglet Création batch de raccourcis."""

import os
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                               QListWidget, QPushButton, QComboBox, QLineEdit,
                               QProgressBar, QFileDialog, QMessageBox,
                               QAbstractItemView)
from PySide6.QtCore import Signal

from src.utils import make_btn
from src.shortcut_scanner import ShortcutScanner
from src.workers import BatchWorker

try:
    import win32com.client
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False

from src.widgets import DropFrame


class BatchTab(QWidget):
    log = Signal(str)

    def __init__(self, store) -> None:
        super().__init__()
        self.store = store
        self._worker: Optional[BatchWorker] = None
        self._running = False
        self._build()

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(14, 14, 14, 14)

        drop = DropFrame()
        drop.files_dropped.connect(self._add_paths)
        layout.addWidget(drop)

        g = QGroupBox("📂 Fichiers à raccourcir")
        gl = QVBoxLayout(g)
        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.file_list.setMinimumHeight(180)
        gl.addWidget(self.file_list)

        btns = QHBoxLayout()
        b1 = make_btn("➕ Fichiers", "secondary")
        b1.clicked.connect(self._add_files)
        b2 = make_btn("📁 Dossier", "secondary")
        b2.clicked.connect(self._add_folder)
        b3 = make_btn("🗑️ Retirer", "danger")
        b3.clicked.connect(self._remove_sel)
        b4 = make_btn("💨 Tout vider", "warning")
        b4.clicked.connect(self.file_list.clear)
        btns.addWidget(b1)
        btns.addWidget(b2)
        btns.addWidget(b3)
        btns.addWidget(b4)
        btns.addStretch()
        gl.addLayout(btns)
        layout.addWidget(g)

        g2 = QGroupBox("📍 Destination")
        gl2 = QHBoxLayout(g2)
        self.dest_combo = QComboBox()
        self.dest_combo.addItems(["Bureau", "Menu Démarrer", "Démarrage auto", "Personnalisé…"])
        self.dest_custom = QLineEdit()
        self.dest_custom.setPlaceholderText("Chemin…")
        self.dest_custom.setEnabled(False)
        self.dest_combo.currentIndexChanged.connect(lambda i: self.dest_custom.setEnabled(i == 3))
        db = make_btn("📂", "secondary", width=50)
        db.clicked.connect(self._browse_dest)
        gl2.addWidget(self.dest_combo)
        gl2.addWidget(self.dest_custom, 1)
        gl2.addWidget(db)
        layout.addWidget(g2)

        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        self.go_btn = make_btn("🚀 Créer tous les raccourcis", "success", height=44)
        self.go_btn.clicked.connect(self._batch_create)
        layout.addWidget(self.go_btn)
        layout.addStretch()

    def _browse_dest(self) -> None:
        p = QFileDialog.getExistingDirectory(self, "Destination")
        if p:
            self.dest_custom.setText(p)

    def _add_paths(self, paths: list[str]) -> None:
        existing = {self.file_list.item(i).text() for i in range(self.file_list.count())}
        for p in paths:
            if os.path.isdir(p):
                try:
                    for f in os.listdir(p):
                        fp = os.path.join(p, f)
                        if os.path.isfile(fp) and fp not in existing:
                            self.file_list.addItem(fp)
                            existing.add(fp)
                except OSError as e:
                    self.log.emit(f"❌ Impossible de lister {p}: {e}")
            elif os.path.isfile(p) and p not in existing:
                self.file_list.addItem(p)
                existing.add(p)

    def _add_files(self) -> None:
        files, _ = QFileDialog.getOpenFileNames(self, "Fichiers")
        if files:
            self._add_paths(files)

    def _add_folder(self) -> None:
        d = QFileDialog.getExistingDirectory(self, "Dossier")
        if d:
            self._add_paths([d])

    def _remove_sel(self) -> None:
        for item in reversed(self.file_list.selectedItems()):
            self.file_list.takeItem(self.file_list.row(item))

    def _get_dest(self) -> Optional[str]:
        idx = self.dest_combo.currentIndex()
        loc_map = {0: "Desktop", 1: "StartMenu", 2: "Startup"}
        if idx in loc_map:
            return ShortcutScanner.get_special_path(loc_map[idx])
        dest = self.dest_custom.text().strip()
        if dest and os.path.isdir(dest):
            return dest
        return None

    def _batch_create(self) -> None:
        if self._running:
            QMessageBox.warning(self, "En cours", "Une création batch est déjà en cours.")
            return
        n = self.file_list.count()
        if n == 0:
            QMessageBox.warning(self, "Vide", "Aucun fichier !")
            return
        if not HAS_WIN32:
            QMessageBox.critical(self, "Erreur", "pywin32 requis.")
            return

        dest = self._get_dest()
        if not dest:
            QMessageBox.warning(self, "Erreur", "Chemin de destination invalide !")
            return

        items = [self.file_list.item(i).text() for i in range(n)]
        self.progress.setVisible(True)
        self.progress.setMaximum(n)
        self.progress.setValue(0)
        self.go_btn.setEnabled(False)
        self._running = True

        self._worker = BatchWorker(items, dest, parent=self)
        self._worker.progress.connect(self._on_batch_progress)
        self._worker.item_done.connect(self._on_batch_item)
        self._worker.finished_all.connect(self._on_batch_finished)
        self._worker.start()

    def _on_batch_progress(self, current: int, total: int) -> None:
        self.progress.setValue(current)

    def _on_batch_item(self, msg: str, success: bool) -> None:
        self.log.emit(msg)

    def _on_batch_finished(self, ok: int, err: int) -> None:
        self.progress.setVisible(False)
        self.go_btn.setEnabled(True)
        self._running = False
        self._worker = None
        QMessageBox.information(self, "Terminé", f"✅ {ok} créés — ❌ {err} erreurs")
