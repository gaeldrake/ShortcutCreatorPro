"""Onglet Gestion des raccourcis existants."""

import os
import shutil
from pathlib import Path
from typing import Optional, Dict, List

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                               QComboBox, QLineEdit, QPushButton, QListWidget,
                               QTextEdit, QFileDialog, QMessageBox, QProgressBar,
                               QDialog)  
from PySide6.QtCore import Signal

from src.utils import make_btn, safe_startfile, safe_startfile_uri
from src.shortcut_reader import ShortcutReader
from src.shortcut_writer import ShortcutWriter
from src.shortcut_scanner import ShortcutScanner
from src.widgets import ShortcutEditorDialog
from src.workers import ScanWorker


class ManageTab(QWidget):
    log = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self.sc_list: List[Dict] = []
        self._scan_worker: Optional[ScanWorker] = None
        self._build()

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(14, 14, 14, 14)

        g = QGroupBox("🔍 Scanner")
        gl = QHBoxLayout(g)
        self.scan_combo = QComboBox()
        self.scan_combo.addItems(["Bureau", "Menu Démarrer", "Démarrage auto", "Barre des tâches", "Personnalisé…"])
        self.scan_custom = QLineEdit()
        self.scan_custom.setPlaceholderText("Chemin…")
        self.scan_custom.setEnabled(False)
        self.scan_combo.currentIndexChanged.connect(lambda i: self.scan_custom.setEnabled(i == 4))
        scan_btn = make_btn("🔍 Scanner")
        scan_btn.clicked.connect(self._scan)
        gl.addWidget(self.scan_combo)
        gl.addWidget(self.scan_custom, 1)
        gl.addWidget(scan_btn)
        layout.addWidget(g)

        self.scan_progress = QProgressBar()
        self.scan_progress.setVisible(False)
        layout.addWidget(self.scan_progress)

        self.filter_input = QLineEdit()
        self.filter_input.setObjectName("search_input")
        self.filter_input.setPlaceholderText("🔎 Filtrer les raccourcis…")
        self.filter_input.textChanged.connect(self._filter)
        layout.addWidget(self.filter_input)

        self.list_widget = QListWidget()
        self.list_widget.currentRowChanged.connect(self._show_details)
        layout.addWidget(self.list_widget, 1)

        g2 = QGroupBox("📄 Détails")
        gl2 = QVBoxLayout(g2)
        self.details = QTextEdit()
        self.details.setReadOnly(True)
        self.details.setMaximumHeight(110)
        gl2.addWidget(self.details)
        layout.addWidget(g2)

        al = QHBoxLayout()
        b_target = make_btn("🎯 Ouvrir cible")
        b_target.clicked.connect(self._open_target)
        b_loc = make_btn("📂 Ouvrir emplacement", "secondary")
        b_loc.clicked.connect(self._open_location)
        b_edit = make_btn("✏️ Modifier", "warning")
        b_edit.clicked.connect(self._edit)
        b_dup = make_btn("📋 Dupliquer", "secondary")
        b_dup.clicked.connect(self._duplicate)
        b_del = make_btn("🗑️ Supprimer", "danger")
        b_del.clicked.connect(self._delete)
        al.addWidget(b_target)
        al.addWidget(b_loc)
        al.addWidget(b_edit)
        al.addWidget(b_dup)
        al.addStretch()
        al.addWidget(b_del)
        layout.addLayout(al)

    def _get_scan_path(self) -> str:
        loc_map = {0: "Desktop", 1: "StartMenu", 2: "Startup", 3: "TaskBar"}
        idx = self.scan_combo.currentIndex()
        if idx in loc_map:
            return ShortcutScanner.get_special_path(loc_map[idx])
        return self.scan_custom.text().strip()

    def _scan(self) -> None:
        if self._scan_worker and self._scan_worker.isRunning():
            QMessageBox.warning(self, "Scan en cours", "Veuillez patienter...")
            return
        folder = self._get_scan_path()
        if not folder or not os.path.isdir(folder):
            QMessageBox.warning(self, "Erreur", "Chemin invalide !")
            return
        self.list_widget.clear()
        self.sc_list.clear()
        self.details.clear()
        self.filter_input.clear()
        self.scan_progress.setVisible(True)
        self.scan_progress.setValue(0)
        self._scan_worker = ScanWorker(folder, recursive=True)
        self._scan_worker.progress.connect(self._on_scan_progress)
        self._scan_worker.finished.connect(self._on_scan_finished)
        self._scan_worker.start()

    def _on_scan_progress(self, current: int, total: int) -> None:
        self.scan_progress.setMaximum(total)
        self.scan_progress.setValue(current)

    def _on_scan_finished(self, results: List[Dict]) -> None:
        self.scan_progress.setVisible(False)
        self.sc_list = results
        for d in self.sc_list:
            name = Path(d.get("path", "?")).name
            broken = ShortcutReader.is_broken(d["path"]) if "path" in d else False
            prefix = "💔" if broken else "🔗"
            self.list_widget.addItem(f"{prefix} {name}")
        self.log.emit(f"🔍 {len(self.sc_list)} raccourci(s) trouvés")
        self._scan_worker = None

    def _filter(self, text: str) -> None:
        t = text.lower()
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            item.setHidden(t not in item.text().lower())

    def _current_data(self) -> Optional[Dict]:
        row = self.list_widget.currentRow()
        if 0 <= row < len(self.sc_list):
            return self.sc_list[row]
        return None

    def _show_details(self, row: int) -> None:
        d = self._current_data()
        if not d:
            self.details.clear()
            return
        labels = {"target": "🎯 Cible", "arguments": "📝 Args", "description": "📄 Desc",
                  "working_dir": "📁 Rép.", "icon": "🎨 Icône", "hotkey": "⌨️ Hotkey",
                  "run_style": "🪟 Style", "path": "📍 Chemin"}
        broken = ShortcutReader.is_broken(d.get("path", ""))
        lines = []
        if broken:
            lines.append("⚠️ RACCOURCI CASSÉ — la cible n'existe plus !\n")
        for k, v in d.items():
            lbl = labels.get(k, k)
            lines.append(f"{lbl}: {v}")
        self.details.setPlainText("\n".join(lines))

    def _open_target(self) -> None:
        d = self._current_data()
        if not d:
            return
        target = d.get("target", "")
        if not target:
            QMessageBox.warning(self, "Erreur", "Aucune cible définie.")
            return
        try:
            if ":" in target and not (len(target) > 1 and target[1] == ":"):
                safe_startfile_uri(target)
            else:
                safe_startfile(target)
        except (FileNotFoundError, PermissionError, ValueError) as e:
            QMessageBox.warning(self, "Erreur", str(e))

    def _open_location(self) -> None:
        d = self._current_data()
        if d and d.get("path"):
            try:
                safe_startfile(os.path.dirname(d["path"]))
            except Exception as e:
                QMessageBox.warning(self, "Erreur", str(e))

    def _edit(self) -> None:
        d = self._current_data()
        if not d or not d.get("path", "").lower().endswith(".lnk"):
            QMessageBox.warning(self, "Erreur", "Sélectionnez un raccourci .lnk à modifier.")
            return
        dlg = ShortcutEditorDialog(d, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            changes = dlg.get_changes()
            try:
                ShortcutWriter.update_lnk(d["path"], **changes)
                self.log.emit(f"✏️ Modifié : {Path(d['path']).name}")
                self._scan()
            except Exception as e:
                QMessageBox.critical(self, "Erreur", str(e))

    def _duplicate(self) -> None:
        d = self._current_data()
        if not d or not d.get("path"):
            return
        src = d["path"]
        stem = Path(src).stem
        ext = Path(src).suffix
        folder = os.path.dirname(src)
        i = 2
        while True:
            new_name = f"{stem} ({i}){ext}"
            new_path = os.path.join(folder, new_name)
            if not os.path.exists(new_path):
                break
            i += 1
            if i > 1000:
                QMessageBox.warning(self, "Erreur", "Trop de copies existantes.")
                return
        try:
            shutil.copy2(src, new_path)
            self.log.emit(f"📋 Dupliqué : {new_name}")
            self._scan()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))

    def _delete(self) -> None:
        d = self._current_data()
        if not d:
            return
        name = Path(d.get("path", "?")).name
        reply = QMessageBox.question(self, "Confirmer", f"Supprimer « {name} » ?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            if ShortcutWriter.delete(d["path"]):
                self.log.emit(f"🗑️ Supprimé : {name}")
                self._scan()
            else:
                QMessageBox.warning(self, "Erreur", "Échec de la suppression.")
