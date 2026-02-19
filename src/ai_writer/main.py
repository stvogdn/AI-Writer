"""Main entry point for the AI Writer application."""

import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from ai_writer.ui import MainWindow


def main() -> int:
    """Main application entry point.

    Returns:
        Exit code
    """
    # Configure high DPI support
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("AI Writer")
    app.setApplicationVersion("0.1.0")
    app.setOrganizationName("Laszlobeer")

    # Create and show main window
    window = MainWindow()
    window.show()

    # Start event loop
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
