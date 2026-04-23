"""Fonctions utilitaires diverses."""

import os
import re
import sys
import tempfile

import subprocess
import logging
logger = logging.getLogger("ShortcutCreatorPro")

from pathlib import Path
from urllib.parse import urlparse
from typing import Optional

from PySide6.QtGui import QPixmap

from src.config import Config

# Tentative d'import de win32 pour l'extraction d'icônes
try:
    import win32com.client
    import win32gui
    import win32ui
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False


def to_long_path(path: str) -> str:
    """Convertit un chemin en chemin long Windows (\\?\") si nécessaire."""
    if not Config.USE_LONG_PATH_PREFIX:
        return path
    if sys.platform != "win32":
        return path
    path = os.path.abspath(path)
    if path.startswith("\\\\?\\"):
        return path
    if path.startswith("\\\\"):
        return "\\\\?\\UNC\\" + path[2:]
    return "\\\\?\\" + path


def sanitize_filename(name: str) -> str:
    """Nettoie un nom de fichier pour Windows."""
    sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', name)
    sanitized = sanitized.strip('. ')
    if not sanitized:
        sanitized = "shortcut"
    stem = sanitized.split('.')[0].upper()
    if stem in Config.WINDOWS_RESERVED_NAMES:
        sanitized = f"_{sanitized}"
    return sanitized


def validate_url(url: str) -> bool:
    """Valide qu'une URL utilise un schéma autorisé."""
    try:
        parsed = urlparse(url)
        return parsed.scheme in Config.ALLOWED_URL_SCHEMES and bool(parsed.netloc or parsed.path)
    except Exception:
        return False


def validate_hotkey(hotkey: str) -> bool:
    """Valide une hotkey (format Windows)."""
    if not hotkey:
        return True
    pattern = r'^(Ctrl|Alt|Shift)(\+((Ctrl|Alt|Shift)|[A-Z0-9]))*$'
    return bool(re.match(pattern, hotkey, re.IGNORECASE))


def safe_startfile(path: str, allow_executables: bool = False) -> None:
    """Ouvre un fichier/dossier avec validation de sécurité."""
    path = os.path.normpath(os.path.abspath(path))
    if not os.path.exists(path):
        raise FileNotFoundError(f"Chemin introuvable : {path}")

    ext = Path(path).suffix.lower()
    if ext in Config.DANGEROUS_EXTENSIONS and not allow_executables:
        raise PermissionError(
            f"Refus d'exécuter un fichier potentiellement dangereux : {path}"
        )

    long_path = to_long_path(path)
    os.startfile(long_path)


def safe_startfile_uri(uri: str) -> None:
    """Ouvre un URI système (ms-settings:, etc.)."""
    allowed_prefixes = ('ms-settings:', 'ms-store:', 'mailto:')
    if any(uri.startswith(p) for p in allowed_prefixes):
        os.startfile(uri)
    else:
        raise ValueError(f"URI non autorisé : {uri}")


def launch_system_tool(executable: str, args: Optional[list[str]] = None) -> None:
    """Lance un outil système de façon sécurisée."""
    if executable.startswith("ms-"):
        safe_startfile_uri(executable)
        return
    cmd = [executable] + (args or [])
    try:
        subprocess.Popen(
            cmd,
            creationflags=getattr(subprocess, 'DETACHED_PROCESS', 0),
            close_fds=True,
        )
        logger.info("Lancé : %s", executable)
    except FileNotFoundError:
        logger.warning("Introuvable : %s", executable)
        raise
    except OSError as e:
        logger.error("Erreur lancement %s : %s", executable, e)
        raise


def extract_icon_from_exe(exe_path: str, index: int = 0, size: int = 32) -> Optional[QPixmap]:
    """Extrait une icône d'un fichier .exe ou .dll et retourne un QPixmap."""
    if not HAS_WIN32:
        return None
    try:
        hicon = win32gui.ExtractIcon(0, exe_path, index)
        if hicon == 0:
            return None
        info = win32gui.GetIconInfo(hicon)
        hbm = info[1]
        if hbm:
            dc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
            hdc = dc.GetSafeHdc()
            bmp = win32ui.CreateBitmap()
            bmp.CreateCompatibleBitmap(dc, size, size)
            hdc_mem = win32ui.CreateDCFromHandle(win32gui.CreateCompatibleDC(hdc))
            old_bmp = hdc_mem.SelectObject(bmp)
            win32gui.DrawIconEx(hdc_mem.GetSafeHdc(), 0, 0, hicon, size, size, 0, None, 0x0003)
            hdc_mem.SelectObject(old_bmp)
            temp_path = os.path.join(tempfile.gettempdir(), "temp_icon.bmp")
            bmp.SaveBitmapFile(hdc_mem, temp_path)
            pix = QPixmap(temp_path)
            os.remove(temp_path)
            win32gui.DestroyIcon(hicon)
            return pix
        else:
            win32gui.DestroyIcon(hicon)
            return None
    except Exception as e:
        logger.debug(f"Extraction icône échouée: {e}")
        return None


def make_btn(text: str, style: str = "", tooltip: str = "", width: int = 0, height: int = 0):
    """Crée un QPushButton stylisé."""
    from PySide6.QtWidgets import QPushButton
    btn = QPushButton(text)
    if style:
        btn.setObjectName(f"btn_{style}")
    if tooltip:
        btn.setToolTip(tooltip)
    if width:
        btn.setFixedWidth(width)
    if height:
        btn.setMinimumHeight(height)
    return btn
