"""Onglet Modèles (prédéfinis et sauvegardés)."""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                               QListWidget, QGridLayout, QPushButton)
from PySide6.QtCore import Signal

from src.config import Config
from src.utils import make_btn


class TemplatesTab(QWidget):
    template_selected = Signal(dict)
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

        # Sauvegardés
        g = QGroupBox("📋 Modèles sauvegardés")
        gl = QVBoxLayout(g)
        self.tpl_list = QListWidget()
        gl.addWidget(self.tpl_list)
        btns = QHBoxLayout()
        b_use = make_btn("📌 Utiliser")
        b_use.clicked.connect(self._use)
        b_del = make_btn("🗑️ Supprimer", "danger")
        b_del.clicked.connect(self._delete)
        btns.addWidget(b_use)
        btns.addWidget(b_del)
        btns.addStretch()
        gl.addLayout(btns)
        layout.addWidget(g)

        # Prédéfinis
        g2 = QGroupBox("⚡ Modèles rapides")
        gl2 = QGridLayout(g2)
        for i, (lbl, target, args, desc) in enumerate(Config.PREDEFINED_TEMPLATES):
            btn = make_btn(lbl, "secondary")
            btn.setToolTip(desc)
            data = {"type": 3 if target.startswith("ms-") else 0, "target": target, "arguments": args,
                    "name": lbl.split(" ", 1)[1] if " " in lbl else lbl, "description": desc,
                    "icon_path": "", "icon_index": 0, "hotkey": "", "run_style": 1, "run_as_admin": False,
                    "working_dir": ""}
            btn.clicked.connect(lambda _, d=data: self.template_selected.emit(d))
            gl2.addWidget(btn, i // 4, i % 4)
        layout.addWidget(g2)
        layout.addStretch()

    def refresh(self) -> None:
        self.tpl_list.clear()
        for t in self.store.get_templates():
            self.tpl_list.addItem(f"📋 {t.get('name', '?')} → {t.get('target', '?')}")

    def _use(self) -> None:
        row = self.tpl_list.currentRow()
        tpls = self.store.get_templates()
        if 0 <= row < len(tpls):
            self.template_selected.emit(tpls[row])
            self.log.emit(f"📋 Modèle chargé : {tpls[row].get('name')}")

    def _delete(self) -> None:
        row = self.tpl_list.currentRow()
        if row >= 0:
            self.store.remove_template(row)
            self.refresh()
            self.log.emit("🗑️ Modèle supprimé")
