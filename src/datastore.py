"""Stockage persistant de l'historique, des modèles et des réglages."""

import os
import json
import logging
from datetime import datetime
from typing import Any, Dict, List

logger = logging.getLogger("ShortcutCreatorPro")


class DataStore:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.data: Dict = {"history": [], "templates": [], "settings": {}}
        self._load()

    def _load(self) -> None:
        if not os.path.exists(self.filepath):
            return
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
            if isinstance(loaded, dict):
                self.data.update(loaded)
                logger.info("Configuration chargée depuis %s", self.filepath)
        except (json.JSONDecodeError, OSError) as e:
            logger.error("Erreur lecture config : %s", e)

    def save(self) -> None:
        tmp_path = self.filepath + ".tmp"
        try:
            with open(tmp_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_path, self.filepath)
        except Exception as e:
            logger.error("Échec sauvegarde : %s", e)
            raise RuntimeError(f"Échec sauvegarde configuration : {e}") from e

    def add_history(self, entry: Dict) -> None:
        entry_copy = dict(entry)
        entry_copy["timestamp"] = datetime.now().isoformat()
        self.data["history"].insert(0, entry_copy)
        self.data["history"] = self.data["history"][:200]  # MAX_HISTORY
        self.save()

    def clear_history(self) -> None:
        self.data["history"] = []
        self.save()

    def add_template(self, entry: Dict) -> None:
        self.data["templates"].append(dict(entry))
        self.save()

    def remove_template(self, idx: int) -> None:
        if 0 <= idx < len(self.data["templates"]):
            self.data["templates"].pop(idx)
            self.save()

    def get_templates(self) -> List[Dict]:
        return self.data.get("templates", [])

    def get_setting(self, key: str, default: Any = None) -> Any:
        return self.data.get("settings", {}).get(key, default)

    def set_setting(self, key: str, value: Any) -> None:
        self.data.setdefault("settings", {})[key] = value
        self.save()

    def export_to(self, path: str) -> None:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def import_from(self, path: str) -> None:
        with open(path, 'r', encoding='utf-8') as f:
            imported = json.load(f)
        if not isinstance(imported, dict):
            raise ValueError("Format d'import invalide")
        self.data["templates"].extend(imported.get("templates", []))
        self.data["history"].extend(imported.get("history", []))
        self.save()
