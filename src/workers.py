"""Threads pour les opérations longues (batch, scan, vidage corbeille)."""

import os
from pathlib import Path
from PySide6.QtCore import QThread, Signal
from src.shortcut_writer import ShortcutWriter
from src.shortcut_scanner import ShortcutScanner
from src.shortcut_reader import ShortcutReader

try:
    import winshell
    HAS_WINSHELL = True
except ImportError:
    HAS_WINSHELL = False


class BatchWorker(QThread):
    progress = Signal(int, int)
    item_done = Signal(str, bool)
    finished_all = Signal(int, int)

    def __init__(self, items: list[str], dest: str, parent=None) -> None:
        super().__init__(parent)
        self.items = list(items)
        self.dest = dest

    def run(self) -> None:
        ok = err = 0
        total = len(self.items)
        for i, fp in enumerate(self.items):
            name = Path(fp).stem
            try:
                ShortcutWriter.create_lnk(fp, name, self.dest)
                ok += 1
                self.item_done.emit(f"✅ {name}", True)
            except Exception as e:
                err += 1
                self.item_done.emit(f"❌ {name}: {e}", False)
            self.progress.emit(i + 1, total)
        self.finished_all.emit(ok, err)


class ScanWorker(QThread):
    progress = Signal(int, int)
    finished = Signal(list)

    def __init__(self, folder: str, recursive: bool = True):
        super().__init__()
        self.folder = folder
        self.recursive = recursive

    def run(self):
        results = ShortcutScanner.scan_folder(
            self.folder, self.recursive,
            lambda cur, tot: self.progress.emit(cur, tot)
        )
        self.finished.emit(results)


class EmptyBinWorker(QThread):
    finished = Signal(bool, str)

    def run(self):
        try:
            if HAS_WINSHELL:
                winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=False)
                self.finished.emit(True, "Corbeille vidée")
            else:
                self.finished.emit(False, "winshell requis pour vider la corbeille")
        except Exception as e:
            self.finished.emit(False, str(e))
