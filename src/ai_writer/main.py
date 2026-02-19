"""Main entry point for the AI Writer application."""

import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from ai_writer.ui import MainWindow, SplashManager


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
    app.setApplicationVersion("0.2.0")
    app.setOrganizationName("Laszlobeer")

    # Show splash screen
    splash_manager = SplashManager()
    splash_manager.show_splash()

    # Create main window (but don't show it yet)
    window = MainWindow()

    # Simulate startup process with splash screen
    def show_main_window():
        window.show()
        
    splash_manager.simulate_startup_progress(show_main_window)

    # Start event loop
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
