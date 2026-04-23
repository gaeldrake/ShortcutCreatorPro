"""Lecture et analyse des raccourcis .lnk / .url."""

import os
import logging
from typing import Dict, Any

logger = logging.getLogger("ShortcutCreatorPro")

try:
    import win32com.client
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False


class ShortcutReader:
    @staticmethod
    def read_lnk(path: str) -> Dict[str, Any]:
        result = {"path": path}
        if not HAS_WIN32 or not path.lower().endswith('.lnk'):
            return result
        try:
            sh = win32com.client.Dispatch("WScript.Shell")
            sc = sh.CreateShortcut(path)
            result.update({
                "target": sc.TargetPath,
                "arguments": sc.Arguments,
                "description": sc.Description,
                "working_dir": sc.WorkingDirectory,
                "icon": sc.IconLocation,
                "hotkey": sc.Hotkey,
                "run_style": sc.WindowStyle,
            })
        except Exception as e:
            logger.warning("Échec lecture LNK %s : %s", path, e)
        return result

    @staticmethod
    def is_broken(path: str) -> bool:
        data = ShortcutReader.read_lnk(path)
        target = data.get("target", "")
        if not target:
            return True
        if target.startswith(('http://', 'https://', 'ftp://', 'mailto:', 'ms-settings:', 'ms-store:')):
            return False
        return not os.path.exists(target)
