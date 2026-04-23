"""Thèmes Catppuccin (clair et sombre)."""

DARK_THEME = """
* {
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 13px;
}

QMainWindow, QDialog {
    background-color: #1e1e2e;
}

QWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
}

QScrollArea {
    border: none;
    background-color: transparent;
}
QScrollArea > QWidget > QWidget {
    background-color: transparent;
}

QTabWidget::pane {
    border: 1px solid #45475a;
    border-radius: 8px;
    background-color: #181825;
    margin-top: -1px;
}
QTabBar::tab {
    background-color: #313244;
    color: #cdd6f4;
    padding: 10px 22px;
    margin-right: 2px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    min-width: 100px;
}
QTabBar::tab:selected {
    background-color: #89b4fa;
    color: #1e1e2e;
    font-weight: bold;
}
QTabBar::tab:hover:!selected {
    background-color: #45475a;
}

QGroupBox {
    border: 1px solid #45475a;
    border-radius: 10px;
    margin-top: 14px;
    padding: 20px 12px 12px 12px;
    font-weight: bold;
    color: #89b4fa;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 15px;
    padding: 0 8px;
}

QLineEdit, QComboBox, QSpinBox {
    background-color: #313244;
    border: 2px solid #45475a;
    border-radius: 8px;
    padding: 8px 12px;
    color: #cdd6f4;
    selection-background-color: #89b4fa;
    min-height: 18px;
}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
    border-color: #89b4fa;
}
QLineEdit:read-only {
    background-color: #272736;
    color: #a6adc8;
}

QPushButton {
    background-color: #89b4fa;
    color: #1e1e2e;
    border: none;
    border-radius: 8px;
    padding: 9px 18px;
    font-weight: bold;
    min-height: 18px;
}
QPushButton:hover { background-color: #b4d0fb; }
QPushButton:pressed { background-color: #74c7ec; }
QPushButton:disabled { background-color: #45475a; color: #6c7086; }

QPushButton#btn_danger    { background-color: #f38ba8; color: #1e1e2e; }
QPushButton#btn_danger:hover { background-color: #f5a0b8; }

QPushButton#btn_success   { background-color: #a6e3a1; color: #1e1e2e; }
QPushButton#btn_success:hover { background-color: #b8ebb4; }

QPushButton#btn_warning   { background-color: #fab387; color: #1e1e2e; }
QPushButton#btn_warning:hover { background-color: #fcc5a0; }

QPushButton#btn_secondary { background-color: #585b70; color: #cdd6f4; }
QPushButton#btn_secondary:hover { background-color: #6c7086; }

QListWidget {
    background-color: #181825;
    border: 2px solid #45475a;
    border-radius: 10px;
    padding: 5px;
    outline: none;
}
QListWidget::item {
    padding: 8px 10px;
    border-radius: 6px;
    margin: 2px 4px;
}
QListWidget::item:selected {
    background-color: #89b4fa;
    color: #1e1e2e;
}
QListWidget::item:hover:!selected {
    background-color: #313244;
}

QTextEdit {
    background-color: #181825;
    border: 2px solid #45475a;
    border-radius: 10px;
    padding: 10px;
    color: #cdd6f4;
    font-family: 'Cascadia Code', 'Consolas', monospace;
    font-size: 12px;
}

QCheckBox { spacing: 8px; }
QCheckBox::indicator {
    width: 20px; height: 20px;
    border-radius: 4px;
    border: 2px solid #45475a;
    background-color: #313244;
}
QCheckBox::indicator:checked {
    background-color: #89b4fa;
    border-color: #89b4fa;
}

QStatusBar {
    background-color: #181825;
    color: #6c7086;
    border-top: 1px solid #45475a;
    padding: 4px 8px;
}

QComboBox::drop-down { border: none; padding-right: 10px; }
QComboBox QAbstractItemView {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 8px;
    selection-background-color: #89b4fa;
    selection-color: #1e1e2e;
}

QProgressBar {
    border: 2px solid #45475a;
    border-radius: 8px;
    text-align: center;
    background-color: #313244;
    color: #cdd6f4;
    min-height: 22px;
}
QProgressBar::chunk {
    background-color: #89b4fa;
    border-radius: 6px;
}

QToolTip {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #89b4fa;
    border-radius: 6px;
    padding: 6px;
}

QScrollBar:vertical {
    background-color: #181825;
    width: 10px;
    border-radius: 5px;
}
QScrollBar::handle:vertical {
    background-color: #45475a;
    border-radius: 5px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover { background-color: #585b70; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

QScrollBar:horizontal {
    background-color: #181825;
    height: 10px;
    border-radius: 5px;
}
QScrollBar::handle:horizontal {
    background-color: #45475a;
    border-radius: 5px;
    min-width: 30px;
}

QMenuBar {
    background-color: #181825;
    color: #cdd6f4;
    border-bottom: 1px solid #45475a;
    padding: 2px;
}
QMenuBar::item:selected { background-color: #313244; border-radius: 4px; }
QMenu {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 8px;
    padding: 4px;
}
QMenu::item { padding: 6px 30px 6px 20px; border-radius: 4px; }
QMenu::item:selected { background-color: #89b4fa; color: #1e1e2e; }
QMenu::separator { height: 1px; background-color: #45475a; margin: 4px 10px; }

QLabel#header_label {
    font-size: 24px;
    font-weight: bold;
    color: #89b4fa;
    padding: 10px;
    background-color: #181825;
    border-radius: 12px;
}

QLabel#icon_preview {
    background-color: #313244;
    border: 2px dashed #45475a;
    border-radius: 8px;
    min-width: 48px;
    min-height: 48px;
    max-width: 48px;
    max-height: 48px;
}

QLineEdit#search_input {
    background-color: #313244;
    border: 2px solid #585b70;
    border-radius: 20px;
    padding: 8px 16px;
}
QLineEdit#search_input:focus {
    border-color: #89b4fa;
}

QFrame#drop_zone {
    background-color: #1e1e3a;
    border: 3px dashed #89b4fa;
    border-radius: 16px;
    min-height: 80px;
}
QFrame#drop_zone:hover {
    background-color: #252545;
    border-color: #b4d0fb;
}
"""

LIGHT_THEME = """
* {
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 13px;
}

QMainWindow, QDialog { background-color: #eff1f5; }
QWidget { background-color: #eff1f5; color: #4c4f69; }
QScrollArea { border: none; background-color: transparent; }
QScrollArea > QWidget > QWidget { background-color: transparent; }

QTabWidget::pane {
    border: 1px solid #ccd0da; border-radius: 8px;
    background-color: #e6e9ef; margin-top: -1px;
}
QTabBar::tab {
    background-color: #ccd0da; color: #4c4f69;
    padding: 10px 22px; margin-right: 2px;
    border-top-left-radius: 8px; border-top-right-radius: 8px;
    min-width: 100px;
}
QTabBar::tab:selected { background-color: #1e66f5; color: #fff; font-weight: bold; }
QTabBar::tab:hover:!selected { background-color: #bcc0cc; }

QGroupBox {
    border: 1px solid #ccd0da; border-radius: 10px;
    margin-top: 14px; padding: 20px 12px 12px 12px;
    font-weight: bold; color: #1e66f5;
}
QGroupBox::title { subcontrol-origin: margin; left: 15px; padding: 0 8px; }

QLineEdit, QComboBox, QSpinBox {
    background-color: #fff; border: 2px solid #ccd0da; border-radius: 8px;
    padding: 8px 12px; color: #4c4f69; min-height: 18px;
}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus { border-color: #1e66f5; }
QLineEdit:read-only { background-color: #e6e9ef; color: #6c6f85; }

QPushButton {
    background-color: #1e66f5; color: #fff; border: none; border-radius: 8px;
    padding: 9px 18px; font-weight: bold; min-height: 18px;
}
QPushButton:hover { background-color: #4880f7; }
QPushButton:pressed { background-color: #1654d4; }
QPushButton:disabled { background-color: #ccd0da; color: #9ca0b0; }

QPushButton#btn_danger { background-color: #d20f39; color: #fff; }
QPushButton#btn_danger:hover { background-color: #e03355; }
QPushButton#btn_success { background-color: #40a02b; color: #fff; }
QPushButton#btn_success:hover { background-color: #55b340; }
QPushButton#btn_warning { background-color: #df8e1d; color: #fff; }
QPushButton#btn_warning:hover { background-color: #e8a130; }
QPushButton#btn_secondary { background-color: #acb0be; color: #4c4f69; }
QPushButton#btn_secondary:hover { background-color: #bcc0cc; }

QListWidget {
    background-color: #fff; border: 2px solid #ccd0da; border-radius: 10px;
    padding: 5px; outline: none;
}
QListWidget::item { padding: 8px 10px; border-radius: 6px; margin: 2px 4px; }
QListWidget::item:selected { background-color: #1e66f5; color: #fff; }
QListWidget::item:hover:!selected { background-color: #e6e9ef; }

QTextEdit {
    background-color: #fff; border: 2px solid #ccd0da; border-radius: 10px;
    padding: 10px; color: #4c4f69;
    font-family: 'Cascadia Code', 'Consolas', monospace; font-size: 12px;
}

QCheckBox { spacing: 8px; }
QCheckBox::indicator {
    width: 20px; height: 20px; border-radius: 4px;
    border: 2px solid #ccd0da; background-color: #fff;
}
QCheckBox::indicator:checked { background-color: #1e66f5; border-color: #1e66f5; }

QStatusBar {
    background-color: #e6e9ef; color: #6c6f85;
    border-top: 1px solid #ccd0da; padding: 4px 8px;
}

QComboBox::drop-down { border: none; padding-right: 10px; }
QComboBox QAbstractItemView {
    background-color: #fff; border: 1px solid #ccd0da; border-radius: 8px;
    selection-background-color: #1e66f5; selection-color: #fff;
}

QProgressBar {
    border: 2px solid #ccd0da; border-radius: 8px;
    text-align: center; background-color: #fff; color: #4c4f69; min-height: 22px;
}
QProgressBar::chunk { background-color: #1e66f5; border-radius: 6px; }

QToolTip {
    background-color: #fff; color: #4c4f69;
    border: 1px solid #1e66f5; border-radius: 6px; padding: 6px;
}

QScrollBar:vertical {
    background-color: #e6e9ef; width: 10px; border-radius: 5px;
}
QScrollBar::handle:vertical {
    background-color: #ccd0da; border-radius: 5px; min-height: 30px;
}
QScrollBar::handle:vertical:hover { background-color: #acb0be; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

QMenuBar {
    background-color: #e6e9ef; color: #4c4f69;
    border-bottom: 1px solid #ccd0da; padding: 2px;
}
QMenuBar::item:selected { background-color: #ccd0da; border-radius: 4px; }
QMenu {
    background-color: #fff; color: #4c4f69;
    border: 1px solid #ccd0da; border-radius: 8px; padding: 4px;
}
QMenu::item { padding: 6px 30px 6px 20px; border-radius: 4px; }
QMenu::item:selected { background-color: #1e66f5; color: #fff; }

QLabel#header_label {
    font-size: 24px; font-weight: bold; color: #1e66f5;
    padding: 10px; background-color: #e6e9ef; border-radius: 12px;
}
QLabel#icon_preview {
    background-color: #fff; border: 2px dashed #ccd0da;
    border-radius: 8px; min-width: 48px; min-height: 48px;
    max-width: 48px; max-height: 48px;
}
QLineEdit#search_input {
    background-color: #fff; border: 2px solid #ccd0da;
    border-radius: 20px; padding: 8px 16px;
}
QLineEdit#search_input:focus { border-color: #1e66f5; }
QFrame#drop_zone {
    background-color: #dce0e8; border: 3px dashed #1e66f5;
    border-radius: 16px; min-height: 80px;
}
QFrame#drop_zone:hover { background-color: #ccd0da; border-color: #4880f7; }
"""
