"""Onglet Création de raccourcis."""

import os
from pathlib import Path
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QLineEdit, QPushButton, QComboBox, QFileDialog,
                               QGroupBox, QGridLayout, QCheckBox, QScrollArea,
                               QMessageBox, QSpinBox)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap   # <--- AJOUT

from src.config import Config
from src.utils import make_btn, extract_icon_from_exe, safe_startfile
from src.shortcut_writer import ShortcutWriter
from src.shortcut_scanner import ShortcutScanner
from src.datastore import DataStore

try:
    import win32com.client
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False


class CreateTab(QWidget):
    shortcut_created = Signal(dict)
    log = Signal(str)
    request_template_refresh = Signal()

    def __init__(self, store: DataStore) -> None:
        super().__init__()
        self.store = store
        self._build()

    def _build(self) -> None:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        inner = QWidget()
        layout = QVBoxLayout(inner)
        layout.setSpacing(10)
        layout.setContentsMargins(14, 14, 14, 14)

        # Type
        g_type = QGroupBox("📌 Type de raccourci")
        gl = QHBoxLayout(g_type)
        self.type_combo = QComboBox()
        self.type_combo.addItems(["🖥️ Application / Fichier", "📁 Dossier", "🌐 URL / Site Web", "⚡ Commande système"])
        self.type_combo.currentIndexChanged.connect(self._on_type_changed)
        gl.addWidget(QLabel("Type :"))
        gl.addWidget(self.type_combo, 1)
        layout.addWidget(g_type)

        # Cible
        g_target = QGroupBox("🎯 Cible")
        gt = QGridLayout(g_target)
        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("Chemin vers le fichier, dossier ou URL…")
        self.browse_btn = make_btn("📂 Parcourir", "secondary", width=130)
        self.browse_btn.clicked.connect(self._browse_target)
        gt.addWidget(QLabel("Cible :"), 0, 0)
        gt.addWidget(self.target_input, 0, 1)
        gt.addWidget(self.browse_btn, 0, 2)

        self.args_input = QLineEdit()
        self.args_input.setPlaceholderText("Arguments ligne de commande (optionnel)")
        gt.addWidget(QLabel("Arguments :"), 1, 0)
        gt.addWidget(self.args_input, 1, 1, 1, 2)

        self.workdir_input = QLineEdit()
        self.workdir_input.setPlaceholderText("Répertoire de travail (optionnel)")
        wd_btn = make_btn("📂", "secondary", width=50)
        wd_btn.clicked.connect(self._browse_workdir)
        gt.addWidget(QLabel("Répertoire :"), 2, 0)
        gt.addWidget(self.workdir_input, 2, 1)
        gt.addWidget(wd_btn, 2, 2)
        layout.addWidget(g_target)

        # Propriétés
        g_props = QGroupBox("⚙️ Propriétés")
        gp = QGridLayout(g_props)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nom du raccourci")
        gp.addWidget(QLabel("Nom :"), 0, 0)
        gp.addWidget(self.name_input, 0, 1, 1, 4)

        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Description / info-bulle")
        gp.addWidget(QLabel("Description :"), 1, 0)
        gp.addWidget(self.desc_input, 1, 1, 1, 4)

        self.icon_input = QLineEdit()
        self.icon_input.setPlaceholderText("Icône (.ico, .exe, .dll)")
        self.icon_input.textChanged.connect(self._update_icon_preview)
        ic_btn = make_btn("🎨", "secondary", width=50)
        ic_btn.clicked.connect(self._browse_icon)
        self.icon_index = QSpinBox()
        self.icon_index.setRange(0, 999)
        self.icon_index.setPrefix("Idx: ")
        self.icon_index.setFixedWidth(90)
        self.icon_index.valueChanged.connect(lambda: self._update_icon_preview(self.icon_input.text()))
        self.icon_preview = QLabel()
        self.icon_preview.setObjectName("icon_preview")
        self.icon_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_preview.setFixedSize(48, 48)
        gp.addWidget(QLabel("Icône :"), 2, 0)
        gp.addWidget(self.icon_input, 2, 1)
        gp.addWidget(ic_btn, 2, 2)
        gp.addWidget(self.icon_index, 2, 3)
        gp.addWidget(self.icon_preview, 2, 4)

        self.hotkey_input = QLineEdit()
        self.hotkey_input.setPlaceholderText("Ex: Ctrl+Alt+N")
        self.run_combo = QComboBox()
        self.run_combo.addItems(["Normal", "Réduit", "Agrandi"])
        gp.addWidget(QLabel("Hotkey :"), 3, 0)
        gp.addWidget(self.hotkey_input, 3, 1, 1, 2)
        gp.addWidget(QLabel("Fenêtre :"), 3, 3)
        gp.addWidget(self.run_combo, 3, 4)
        layout.addWidget(g_props)

        # Emplacements
        g_loc = QGroupBox("📍 Emplacement(s)")
        gl2 = QGridLayout(g_loc)
        self.loc_checks = {}
        locs = [("desktop", "🖥️ Bureau", True), ("taskbar", "📌 Barre des tâches", False),
                ("startmenu", "🏁 Menu Démarrer", False), ("startup", "🚀 Démarrage auto", False),
                ("sendto", "📨 Envoyer vers", False), ("custom", "📁 Personnalisé", False)]
        for i, (key, lbl, default) in enumerate(locs):
            cb = QCheckBox(lbl)
            cb.setChecked(default)
            self.loc_checks[key] = cb
            gl2.addWidget(cb, i // 3, i % 3)

        self.loc_checks["custom"].toggled.connect(self._on_custom_toggled)
        self.custom_path = QLineEdit()
        self.custom_path.setPlaceholderText("Chemin du dossier…")
        self.custom_path.setEnabled(False)
        self.custom_browse = make_btn("📂", "secondary", width=50)
        self.custom_browse.setEnabled(False)
        self.custom_browse.clicked.connect(self._browse_custom)
        gl2.addWidget(self.custom_path, 2, 0, 1, 2)
        gl2.addWidget(self.custom_browse, 2, 2)
        layout.addWidget(g_loc)

        # Options
        opts = QHBoxLayout()
        self.admin_check = QCheckBox("🛡️ Exécuter en administrateur")
        self.open_after = QCheckBox("📂 Ouvrir l'emplacement après")
        opts.addWidget(self.admin_check)
        opts.addWidget(self.open_after)
        opts.addStretch()
        layout.addLayout(opts)

        # Boutons
        btns = QHBoxLayout()
        save_tpl = make_btn("💾 Sauver modèle", "secondary")
        save_tpl.clicked.connect(self._save_template)
        clear = make_btn("🗑️ Effacer", "warning")
        clear.clicked.connect(self._clear)
        create = make_btn("✨ Créer le raccourci", "success", height=44)
        create.clicked.connect(self._create)
        btns.addWidget(save_tpl)
        btns.addWidget(clear)
        btns.addStretch()
        btns.addWidget(create)
        layout.addLayout(btns)
        layout.addStretch()
        scroll.setWidget(inner)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    # --- Slots ---
    def _on_type_changed(self, idx: int) -> None:
        is_url = idx == 2
        is_cmd = idx == 3
        self.browse_btn.setEnabled(not is_url and not is_cmd)
        placeholders = {0: "Chemin vers le fichier…", 1: "Chemin vers le dossier…",
                        2: "https://www.example.com", 3: "cmd.exe, powershell.exe, …"}
        self.target_input.setPlaceholderText(placeholders.get(idx, ""))

    def _on_custom_toggled(self, checked: bool) -> None:
        self.custom_path.setEnabled(checked)
        self.custom_browse.setEnabled(checked)

    def _browse_target(self) -> None:
        idx = self.type_combo.currentIndex()
        if idx == 1:
            p = QFileDialog.getExistingDirectory(self, "Sélectionner un dossier")
        else:
            p, _ = QFileDialog.getOpenFileName(self, "Sélectionner un fichier", "",
                                               "Tous (*);;Exécutables (*.exe);;Scripts (*.bat *.cmd *.ps1 *.py)")
        if p:
            self.target_input.setText(p)
            if not self.name_input.text():
                self.name_input.setText(Path(p).stem)

    def _browse_workdir(self) -> None:
        p = QFileDialog.getExistingDirectory(self, "Répertoire de travail")
        if p:
            self.workdir_input.setText(p)

    def _browse_icon(self) -> None:
        p, _ = QFileDialog.getOpenFileName(self, "Icône", "",
                                           "Icônes (*.ico);;Exécutables (*.exe);;DLL (*.dll);;Tous (*)")
        if p:
            self.icon_input.setText(p)

    def _browse_custom(self) -> None:
        p = QFileDialog.getExistingDirectory(self, "Destination")
        if p:
            self.custom_path.setText(p)

    def _update_icon_preview(self, path: str) -> None:
        path = path.strip()
        if not path:
            self.icon_preview.clear()
            self.icon_preview.setText("?")
            return
        if os.path.isfile(path) and path.lower().endswith('.ico'):
            pix = QPixmap(path)
            if not pix.isNull():
                self.icon_preview.setPixmap(pix.scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio,
                                                       Qt.TransformationMode.SmoothTransformation))
                return
        if HAS_WIN32 and os.path.isfile(path) and path.lower().endswith(('.exe', '.dll')):
            pix = extract_icon_from_exe(path, self.icon_index.value(), 40)
            if pix:
                self.icon_preview.setPixmap(pix)
                return
        self.icon_preview.clear()
        self.icon_preview.setText("?")

    def _clear(self) -> None:
        for w in (self.target_input, self.name_input, self.desc_input, self.args_input,
                  self.workdir_input, self.icon_input, self.hotkey_input, self.custom_path):
            w.clear()
        self.icon_index.setValue(0)
        self.run_combo.setCurrentIndex(0)
        self.admin_check.setChecked(False)
        self.icon_preview.clear()
        self.log.emit("Formulaire effacé")

    def _get_data(self) -> dict:
        return {
            "type": self.type_combo.currentIndex(),
            "target": self.target_input.text().strip(),
            "name": self.name_input.text().strip(),
            "description": self.desc_input.text().strip(),
            "arguments": self.args_input.text().strip(),
            "working_dir": self.workdir_input.text().strip(),
            "icon_path": self.icon_input.text().strip(),
            "icon_index": self.icon_index.value(),
            "hotkey": self.hotkey_input.text().strip(),
            "run_style": Config.RUN_STYLE_LIST[self.run_combo.currentIndex()],
            "run_as_admin": self.admin_check.isChecked(),
        }

    def load_data(self, d: dict) -> None:
        self.type_combo.setCurrentIndex(d.get("type", 0))
        self.target_input.setText(d.get("target", ""))
        self.name_input.setText(d.get("name", ""))
        self.desc_input.setText(d.get("description", ""))
        self.args_input.setText(d.get("arguments", ""))
        self.workdir_input.setText(d.get("working_dir", ""))
        self.icon_input.setText(d.get("icon_path", ""))
        self.icon_index.setValue(d.get("icon_index", 0))
        self.hotkey_input.setText(d.get("hotkey", ""))
        self.admin_check.setChecked(d.get("run_as_admin", False))
        self.run_combo.setCurrentIndex(Config.RUN_STYLE_INDEX_MAP.get(d.get("run_style", 1), 0))

    def has_unsaved(self) -> bool:
        return bool(self.target_input.text().strip() or self.name_input.text().strip())

    def _save_template(self) -> None:
        d = self._get_data()
        if not d.get("name"):
            QMessageBox.warning(self, "Attention", "Donnez un nom au modèle.")
            return
        self.store.add_template(d)
        self.log.emit(f"✅ Modèle « {d['name']} » sauvegardé")
        self.request_template_refresh.emit()
        QMessageBox.information(self, "Succès", f"Modèle « {d['name']} » enregistré !")

    def _create(self) -> None:
        d = self._get_data()
        if not d.get("target"):
            QMessageBox.warning(self, "Erreur", "Spécifiez une cible !")
            return
        if not d.get("name"):
            QMessageBox.warning(self, "Erreur", "Spécifiez un nom !")
            return
        if not HAS_WIN32:
            QMessageBox.critical(self, "Erreur", "pywin32 est requis. Installez : pip install pywin32")
            return

        loc_map = {"desktop": "Desktop", "taskbar": "TaskBar", "startmenu": "StartMenu",
                   "startup": "Startup", "sendto": "SendTo"}
        created = []
        errors = []
        for key, folder_key in loc_map.items():
            if not self.loc_checks[key].isChecked():
                continue
            try:
                folder = ShortcutScanner.get_special_path(folder_key)
                path = self._create_one(d, folder)
                created.append(path)
                self.log.emit(f"✅ Créé : {path}")
            except Exception as e:
                errors.append(f"{folder_key}: {e}")
                self.log.emit(f"❌ {folder_key}: {e}")

        if self.loc_checks["custom"].isChecked():
            cp = self.custom_path.text().strip()
            if cp:
                try:
                    path = self._create_one(d, cp)
                    created.append(path)
                    self.log.emit(f"✅ Créé : {path}")
                except Exception as e:
                    errors.append(f"Custom: {e}")
                    self.log.emit(f"❌ Custom: {e}")

        if created:
            d_with_paths = dict(d)
            d_with_paths["created_paths"] = created
            self.store.add_history(d_with_paths)
            self.shortcut_created.emit(d_with_paths)
            if self.open_after.isChecked():
                try:
                    safe_startfile(os.path.dirname(created[0]))
                except Exception as e:
                    self.log.emit(f"⚠️ Impossible d'ouvrir le dossier : {e}")

        if created and not errors:
            QMessageBox.information(self, "Succès", f"✨ {len(created)} raccourci(s) créé(s) !")
        elif errors:
            QMessageBox.warning(self, "Attention", f"Créés : {len(created)}, Erreurs : {len(errors)}\n\n" + "\n".join(errors))

    def _create_one(self, d: dict, folder: str) -> str:
        if d.get("type") == 2:
            return ShortcutWriter.create_url(d["target"], d["name"], folder, d.get("icon_path", ""))
        return ShortcutWriter.create_lnk(
            target=d["target"], name=d["name"], folder=folder,
            description=d.get("description", ""), icon_path=d.get("icon_path", ""),
            icon_index=d.get("icon_index", 0), arguments=d.get("arguments", ""),
            working_dir=d.get("working_dir", ""), run_style=d.get("run_style", 1),
            hotkey=d.get("hotkey", ""), run_as_admin=d.get("run_as_admin", False)
        )
