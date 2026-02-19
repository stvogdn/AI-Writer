"""Dark theme stylesheet for AI Writer."""

DARK_THEME = """
QMainWindow { background-color: #1e1e1e; }
QWidget { font-family: 'Segoe UI', 'Roboto', 'Helvetica', sans-serif; color: #e0e0e0; }

QToolBar {
    background-color: #2c2c2c;
    border-bottom: 1px solid #3a3a3a;
    padding: 8px;
    spacing: 10px;
}
QToolBar QPushButton {
    background-color: transparent;
    border: 1px solid #444;
    border-radius: 6px;
    padding: 8px 15px;
    font-weight: 500;
    color: #e0e0e0;
}
QToolBar QPushButton:hover { background-color: #3a3a3a; }
QToolBar QPushButton:disabled { color: #555; border-color: #333; }

QToolBar QPushButton#generate-btn {
    background-color: #0a84ff;
    color: white;
    border: none;
    font-weight: 600;
}
QToolBar QPushButton#generate-btn:hover { background-color: #409cff; }

QTextEdit#editor {
    background-color: #252526;
    border: none;
    border-radius: 0px;
    padding: 40px;
    font-size: 16px;
    line-height: 1.6;
    font-family: 'Georgia', 'Times New Roman', serif;
    color: #d4d4d4;
}
QTextEdit#editor:focus { outline: none; }

QFrame#sidebar {
    background-color: #2c2c2c;
    border-left: 1px solid #3a3a3a;
    padding: 20px;
}

QComboBox, QSpinBox {
    background-color: #3a3a3a;
    border: 1px solid #444;
    border-radius: 6px;
    padding: 8px;
    font-size: 13px;
    color: #fff;
}
QComboBox:focus, QSpinBox:focus { border: 1px solid #0a84ff; }

QSlider::groove:horizontal {
    border: 1px solid #444;
    height: 6px;
    background: #3a3a3a;
    border-radius: 3px;
}
QSlider::handle:horizontal {
    background: #0a84ff;
    border: 1px solid #0056b3;
    width: 16px;
    margin: -5px 0;
    border-radius: 8px;
}
QSlider::handle:horizontal:hover { background: #409cff; }

QLabel#sidebar-title { font-size: 14px; font-weight: 600; color: #aaa; margin: 10px 0; }

QStatusBar { background-color: #2c2c2c; border-top: 1px solid #3a3a3a; color: #888; }

QPushButton#save-btn {
    background-color: #34c759;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 15px;
    font-weight: 500;
    margin: 5px 0;
}
QPushButton#save-btn:hover { background-color: #28a745; }
QPushButton#save-btn:disabled { background-color: #555; }
"""
