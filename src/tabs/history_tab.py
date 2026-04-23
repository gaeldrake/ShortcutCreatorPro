"""Onglet Historique des créations."""

from pathlib import Path
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                               QLineEdit, QListWidget, QPushButton, QMessageBox)
from PySide6.QtCore import Signal

from src.utils import make_btn


class HistoryTab(QWidget):
    log = Signal(str)

    def __init__(self, store) -> None:
        super().__init__()
        self.store = store
        self._build()
        self.refresh()

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(14, 14, 14, 14)

        self.filter_input = QLineEdit()
        self.filter_input.setObjectName("search_input")
        self.filter_input.setPlaceholderText("🔎 Filtrer l'historique…")
        self.filter_input.textChanged.connect(self._filter)
        layout.addWidget(self.filter_input)

        self.h_list = QListWidget()
        layout.addWidget(self.h_list, 1)

        btns = QHBoxLayout()
        br = make_btn("🔄 Rafraîchir", "secondary")
        br.clicked.connect(self.refresh)
        bc = make_btn("🗑️ Vider", "danger")
        bc.clicked.connect(self._clear)
        btns.addWidget(br)
        btns.addStretch()
        btns.addWidget(bc)
        layout.addLayout(btns)

    def refresh(self) -> None:
        self.h_list.clear()
        self.filter_input.clear()
        for e in self.store.data.get("history", []):
            ts = e.get("timestamp", "?")[:19].replace("T", " ")
            name = e.get("name", "?")
            target = e.get("target", "?")
            paths = e.get("created_paths", [])
            locs = ", ".join(Path(p).parent.name for p in paths)
            self.h_list.addItem(f"🕐 [{ts}]  {name}  →  {target}  ({locs})")

    def _filter(self, text: str) -> None:
        t = text.lower()
        for i in range(self.h_list.count()):
            item = self.h_list.item(i)
            item.setHidden(t not in item.text().lower())

    def _clear(self) -> None:
        if QMessageBox.question(self, "Confirmer", "Vider tout l'historique ?",
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            self.store.clear_history()
            self.refresh()
            self.log.emit("🗑️ Historique vidé")
