"""Constantes globales de l'application."""

import os


class Config:
    APP_NAME = "Shortcut Creator Pro"
    APP_VERSION = "3.0"
    WINDOW_TITLE = f"🔗 {APP_NAME} v{APP_VERSION}"

    MAX_HISTORY = 200
    LOG_PANEL_HEIGHT = 120
    BROKEN_LIST_HEIGHT = 150
    MIN_WINDOW_WIDTH = 870
    MIN_WINDOW_HEIGHT = 600
    DEFAULT_WINDOW_WIDTH = 870
    DEFAULT_WINDOW_HEIGHT = 700

    CONFIG_FILENAME = ".shortcut_creator_pro.json"
    CONFIG_PATH = os.path.join(os.path.expanduser("~"), CONFIG_FILENAME)

    USE_LONG_PATH_PREFIX = True

    DANGEROUS_EXTENSIONS = frozenset({
        '.bat', '.cmd', '.ps1', '.vbs', '.js',
        '.wsf', '.wsh', '.scr', '.pif', '.com',
    })

    ALLOWED_URL_SCHEMES = frozenset({
        'http', 'https', 'ftp', 'ftps', 'mailto',
    })

    WINDOWS_RESERVED_NAMES = frozenset({
        'CON', 'PRN', 'AUX', 'NUL',
        *(f'COM{i}' for i in range(1, 10)),
        *(f'LPT{i}' for i in range(1, 10)),
    })

    RUN_STYLES = {"Normal": 1, "Réduit": 7, "Agrandi": 3}
    RUN_STYLE_LIST = [1, 7, 3]
    RUN_STYLE_INDEX_MAP = {1: 0, 7: 1, 3: 2}

    SPECIAL_PATHS = {
        "Desktop": os.path.join(os.path.expanduser("~"), "Desktop"),
        "StartMenu": os.path.join(
            os.environ.get("APPDATA", ""),
            r"Microsoft\Windows\Start Menu\Programs"
        ),
        "Startup": os.path.join(
            os.environ.get("APPDATA", ""),
            r"Microsoft\Windows\Start Menu\Programs\Startup"
        ),
        "TaskBar": os.path.join(
            os.environ.get("APPDATA", ""),
            r"Microsoft\Internet Explorer\Quick Launch\User Pinned\TaskBar"
        ),
        "SendTo": os.path.join(
            os.environ.get("APPDATA", ""),
            r"Microsoft\Windows\SendTo"
        ),
    }

    SYSTEM_PATHS = {
        "AppData": os.environ.get("APPDATA", ""),
        "Temp": os.environ.get("TEMP", ""),
        "ProgramFiles": os.environ.get("PROGRAMFILES", ""),
    }

    PREDEFINED_TEMPLATES = [
        ("🖥️ CMD", "cmd.exe", "", "Invite de commandes"),
        ("💻 PowerShell", "powershell.exe", "", "PowerShell"),
        ("📝 Notepad", "notepad.exe", "", "Bloc-notes"),
        ("🧮 Calculatrice", "calc.exe", "", "Calculatrice"),
        ("🎨 Paint", "mspaint.exe", "", "Paint"),
        ("🌐 Edge", "msedge.exe", "", "Microsoft Edge"),
        ("📁 Explorateur", "explorer.exe", "", "Explorateur"),
        ("⚙️ Paramètres", "ms-settings:", "", "Paramètres Windows"),
        ("🔧 Regedit", "regedit.exe", "", "Éditeur du registre"),
        ("📊 Taskmgr", "taskmgr.exe", "", "Gestionnaire de tâches"),
        ("🧹 Nettoyage", "cleanmgr.exe", "", "Nettoyage de disque"),
        ("🌐 Chrome", "chrome.exe", "", "Google Chrome"),
    ]

    SYSTEM_TOOLS = [
        ("🔄 Rafraîchir icônes", "ie4uinit.exe", ["-show"]),
        ("⚙️ Paramètres", "ms-settings:", []),
        ("🖥️ Info système", "msinfo32", []),
        ("📊 Gestionnaire tâches", "taskmgr", []),
        ("🧹 Nettoyage disque", "cleanmgr", []),
    ]
