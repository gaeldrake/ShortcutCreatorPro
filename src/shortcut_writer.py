"""Création, modification et suppression de raccourcis .lnk / .url."""

import os
import logging
from pathlib import Path

from src.config import Config
from src.utils import to_long_path, sanitize_filename, validate_hotkey, validate_url

logger = logging.getLogger("ShortcutCreatorPro")

try:
    import win32com.client
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False


class ShortcutWriter:
    @staticmethod
    def _require_win32() -> None:
        if not HAS_WIN32:
            raise RuntimeError("pywin32 est requis. Installez : pip install pywin32")

    @staticmethod
    def create_lnk(target: str, name: str, folder: str, description: str = "",
                   icon_path: str = "", icon_index: int = 0, arguments: str = "",
                   working_dir: str = "", run_style: int = 1, hotkey: str = "",
                   run_as_admin: bool = False) -> str:
        ShortcutWriter._require_win32()
        name = sanitize_filename(name)
        if not name.lower().endswith(".lnk"):
            name += ".lnk"
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, name)
        long_path = to_long_path(path)

        sh = win32com.client.Dispatch("WScript.Shell")
        sc = sh.CreateShortcut(long_path)
        sc.TargetPath = target
        sc.Description = description or f"Raccourci vers {Path(target).name}"
        sc.WorkingDirectory = working_dir or str(Path(target).parent)
        sc.Arguments = arguments
        sc.WindowStyle = run_style
        sc.IconLocation = f"{icon_path},{icon_index}" if icon_path else f"{target},0"
        if hotkey and validate_hotkey(hotkey):
            sc.Hotkey = hotkey
        sc.Save()

        if run_as_admin:
            ShortcutWriter._set_admin_flag(path)
        logger.info("Raccourci créé : %s", path)
        return path

    @staticmethod
    def create_url(url: str, name: str, folder: str, icon_path: str = "") -> str:
        if not validate_url(url):
            raise ValueError(f"URL invalide ou schéma non autorisé : {url}")
        name = sanitize_filename(name)
        if not name.lower().endswith(".url"):
            name += ".url"
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, name)
        long_path = to_long_path(path)
        with open(long_path, 'w', encoding='utf-8') as f:
            f.write("[InternetShortcut]\n")
            f.write(f"URL={url}\n")
            if icon_path and os.path.isfile(icon_path):
                f.write(f"IconFile={icon_path}\nIconIndex=0\n")
        logger.info("Raccourci URL créé : %s", path)
        return path

    @staticmethod
    def update_lnk(path: str, **kwargs) -> str:
        ShortcutWriter._require_win32()
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Raccourci introuvable : {path}")
        sh = win32com.client.Dispatch("WScript.Shell")
        sc = sh.CreateShortcut(to_long_path(path))

        field_map = {
            "target": "TargetPath",
            "arguments": "Arguments",
            "description": "Description",
            "working_dir": "WorkingDirectory",
            "hotkey": "Hotkey",
        }
        for key, attr in field_map.items():
            if key in kwargs and kwargs[key] is not None:
                setattr(sc, attr, kwargs[key])

        if "run_style" in kwargs:
            sc.WindowStyle = kwargs["run_style"]
        if "icon_path" in kwargs:
            idx = kwargs.get("icon_index", 0)
            sc.IconLocation = f"{kwargs['icon_path']},{idx}"
        if "hotkey" in kwargs and kwargs["hotkey"] and validate_hotkey(kwargs["hotkey"]):
            sc.Hotkey = kwargs["hotkey"]
        sc.Save()
        if kwargs.get("run_as_admin"):
            ShortcutWriter._set_admin_flag(path)
        logger.info("Raccourci modifié : %s", path)
        return path

    @staticmethod
    def delete(path: str) -> bool:
        try:
            os.remove(to_long_path(path))
            logger.info("Raccourci supprimé : %s", path)
            return True
        except OSError as e:
            logger.error("Échec suppression %s : %s", path, e)
            return False

    @staticmethod
    def _set_admin_flag(lnk_path: str) -> None:
        if not HAS_WIN32:
            return
        try:
            with open(lnk_path, 'r+b') as f:
                if f.read(4) != b'\x4C\x00\x00\x00':
                    raise ValueError("Signature LNK invalide")
                f.seek(0x14)
                flags = int.from_bytes(f.read(2), 'little')
                flags |= 0x20
                f.seek(0x14)
                f.write(flags.to_bytes(2, 'little'))
            logger.info("Flag admin activé : %s", lnk_path)
        except Exception as e:
            logger.error("Échec flag admin %s : %s", lnk_path, e)
            raise RuntimeError(f"Impossible d'activer le flag admin : {e}") from e
