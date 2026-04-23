"""Widgets réutilisables : zone de drop, éditeur de raccourci."""

import os
from pathlib import Path
from PySide6.QtWidgets import (QFrame, QVBoxLayout, QLabel, QDialog, QFormLayout,
                               QLineEdit, QSpinBox, QComboBox, QCheckBox, QDialogButtonBox)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent

from src.config import Config
from src.shortcut_writer import ShortcutWriter


class DropFrame(QFrame):
    files_dropped = Signal(list)

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("drop_zone")
        self.setAcceptDrops(True)
        layout = QVBoxLayout(self)
        self._label = QLabel("📥 Glissez-déposez des fichiers ici")
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label.setStyleSheet("color: #89b4fa; font-size: 14px; background: transparent;")
        layout.addWidget(self._label)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self._label.setText("📥 Relâchez pour ajouter !")

    def dragLeaveEvent(self, event) -> None:
        self._label.setText("📥 Glissez-déposez des fichiers ici")

    def dropEvent(self, event: QDropEvent) -> None:
        urls = event.mimeData().urls()
        paths = [u.toLocalFile() for u in urls if u.isLocalFile()]
        if paths:
            self.files_dropped.emit(paths)
        self._label.setText("📥 Glissez-déposez des fichiers ici")
        event.acceptProposedAction()


class ShortcutEditorDialog(QDialog):
    def __init__(self, shortcut_data: dict, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("✏️ Modifier le raccourci")
        self.setMinimumWidth(550)
        self.sc_data = shortcut_data
        self._build()

    def _build(self) -> None:
        layout = QFormLayout(self)
        layout.setSpacing(10)

        self.target_edit = QLineEdit(self.sc_data.get("target", ""))
        self.args_edit = QLineEdit(self.sc_data.get("arguments", ""))
        self.desc_edit = QLineEdit(self.sc_data.get("description", ""))
        self.workdir_edit = QLineEdit(self.sc_data.get("working_dir", ""))
        self.hotkey_edit = QLineEdit(self.sc_data.get("hotkey", ""))

        icon_str = self.sc_data.get("icon", "")
        icon_parts = icon_str.split(",") if icon_str else ["", "0"]
        self.icon_edit = QLineEdit(icon_parts[0].strip())
        self.icon_idx = QSpinBox()
        self.icon_idx.setRange(0, 999)
        try:
            self.icon_idx.setValue(int(icon_parts[-1].strip()))
        except (IndexError, ValueError):
            pass

        self.run_combo = QComboBox()
        self.run_combo.addItems(["Normal", "Réduit", "Agrandi"])
        style_val = self.sc_data.get("run_style", 1)
        self.run_combo.setCurrentIndex(Config.RUN_STYLE_INDEX_MAP.get(style_val, 0))
        self.admin_check = QCheckBox("Exécuter en administrateur")

        layout.addRow("🎯 Cible :", self.target_edit)
        layout.addRow("📝 Arguments :", self.args_edit)
        layout.addRow("📄 Description :", self.desc_edit)
        layout.addRow("📁 Répertoire :", self.workdir_edit)
        layout.addRow("⌨️ Raccourci clavier :", self.hotkey_edit)
        layout.addRow("🎨 Icône :", self.icon_edit)
        layout.addRow("Index icône :", self.icon_idx)
        layout.addRow("🪟 Fenêtre :", self.run_combo)
        layout.addRow("", self.admin_check)

        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addRow(btns)

    def get_changes(self) -> dict:
        return {
            "target": self.target_edit.text().strip(),
            "arguments": self.args_edit.text().strip(),
            "description": self.desc_edit.text().strip(),
            "working_dir": self.workdir_edit.text().strip(),
            "hotkey": self.hotkey_edit.text().strip(),
            "icon_path": self.icon_edit.text().strip(),
            "icon_index": self.icon_idx.value(),
            "run_style": Config.RUN_STYLE_LIST[self.run_combo.currentIndex()],
            "run_as_admin": self.admin_check.isChecked(),
        }
