"""Scan de dossiers et détection de raccourcis cassés."""

import os
import logging
from typing import List, Dict, Any, Callable, Optional

from src.config import Config
from src.shortcut_reader import ShortcutReader

logger = logging.getLogger("ShortcutCreatorPro")

try:
    import winshell
    HAS_WINSHELL = True
except ImportError:
    HAS_WINSHELL = False


class ShortcutScanner:
    @staticmethod
    def get_special_path(key: str) -> str:
        if HAS_WINSHELL:
            winshell_map = {
                "Desktop": winshell.desktop,
                "StartMenu": winshell.start_menu,
                "Startup": winshell.startup,
            }
            if key in winshell_map:
                try:
                    return winshell_map[key]()
                except Exception as e:
                    logger.warning("winshell fallback pour %s : %s", key, e)
        return Config.SPECIAL_PATHS.get(key, "")

    @staticmethod
    def scan_folder(folder: str, recursive: bool = True,
                    progress_callback: Optional[Callable[[int, int], None]] = None) -> List[Dict[str, Any]]:
        results = []
        if not os.path.isdir(folder):
            logger.warning("Dossier inexistant pour scan : %s", folder)
            return results

        if recursive:
            walker = os.walk(folder)
        else:
            try:
                entries = os.listdir(folder)
            except OSError as e:
                logger.error("Impossible de lister %s : %s", folder, e)
                return results
            walker = [(folder, [], entries)]

        total_files = 0
        for root, _dirs, files in walker:
            for f in files:
                if f.lower().endswith(('.lnk', '.url')):
                    total_files += 1

        processed = 0
        for root, _dirs, files in walker:
            for f in files:
                if f.lower().endswith(('.lnk', '.url')):
                    full = os.path.join(root, f)
                    try:
                        data = ShortcutReader.read_lnk(full)
                        results.append(data)
                    except Exception as e:
                        logger.warning("Erreur lecture %s : %s", full, e)
                    processed += 1
                    if progress_callback:
                        progress_callback(processed, total_files)
        return results

    @staticmethod
    def find_broken(folder: str) -> List[Dict[str, Any]]:
        shortcuts = ShortcutScanner.scan_folder(folder, recursive=True)
        broken = []
        for sc in shortcuts:
            path = sc.get("path", "")
            if path and ShortcutReader.is_broken(path):
                broken.append(sc)
        return broken
