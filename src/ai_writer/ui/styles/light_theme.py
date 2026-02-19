"""Light theme stylesheet for AI Writer."""

LIGHT_THEME = """
QMainWindow { background-color: #f5f5f7; }
QWidget { font-family: 'Segoe UI', 'Roboto', 'Helvetica', sans-serif; color: #333; }

QToolBar {
    background-color: #ffffff;
    border-bottom: 1px solid #e0e0e0;
    padding: 8px;
    spacing: 10px;
}
QToolBar QPushButton {
    background-color: transparent;
    border: 1px solid #ddd;
    border-radius: 6px;
    padding: 8px 15px;
    font-weight: 500;
    color: #333;
}
QToolBar QPushButton:hover { background-color: #e5e5ea; }
QToolBar QPushButton:disabled { color: #ccc; border-color: #eee; }

QToolBar QPushButton#generate-btn {
    background-color: #007aff;
    color: white;
    border: none;
    font-weight: 600;
}
QToolBar QPushButton#generate-btn:hover { background-color: #0056b3; }

QTextEdit#editor {
    background-color: #ffffff;
    border: none;
    border-radius: 0px;
    padding: 40px;
    font-size: 16px;
    line-height: 1.6;
    font-family: 'Georgia', 'Times New Roman', serif;
}
QTextEdit#editor:focus { outline: none; }

QFrame#sidebar {
    background-color: #ffffff;
    border-left: 1px solid #e0e0e0;
    padding: 20px;
}

QComboBox, QSpinBox {
    background-color: #f9f9f9;
    border: 1px solid #ddd;
    border-radius: 6px;
    padding: 8px;
    font-size: 13px;
}
QComboBox:focus, QSpinBox:focus { border: 1px solid #007aff; }

QSlider::groove:horizontal {
    border: 1px solid #ddd;
    height: 6px;
    background: #e0e0e0;
    border-radius: 3px;
}
QSlider::handle:horizontal {
    background: #007aff;
    border: 1px solid #0056b3;
    width: 16px;
    margin: -5px 0;
    border-radius: 8px;
}
QSlider::handle:horizontal:hover { background: #0056b3; }

QLabel#sidebar-title { font-size: 14px; font-weight: 600; color: #555; margin: 10px 0; }

QStatusBar { background-color: #ffffff; border-top: 1px solid #e0e0e0; color: #888; }

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
QPushButton#save-btn:disabled { background-color: #ccc; }
"""
