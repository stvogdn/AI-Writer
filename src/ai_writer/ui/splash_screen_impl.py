"""Splash screen functionality for AI Writer."""

import time
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QPixmap, QFont, QPainter, QColor, QLinearGradient
from PyQt5.QtWidgets import QSplashScreen, QApplication, QProgressBar, QVBoxLayout, QLabel, QWidget


class SplashScreen(QSplashScreen):
    """Custom splash screen for AI Writer."""
    
    def __init__(self):
        """Initialize the splash screen."""
        # Create a simple pixmap for the splash screen
        pixmap = QPixmap(400, 300)
        pixmap.fill(QColor(45, 45, 48))  # Dark background
        
        # Paint the splash screen content
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Create gradient background
        gradient = QLinearGradient(0, 0, 0, 300)
        gradient.setColorAt(0, QColor(45, 45, 48))
        gradient.setColorAt(1, QColor(30, 30, 32))
        painter.fillRect(pixmap.rect(), gradient)
        
        # Draw app title
        painter.setPen(QColor(255, 255, 255))
        title_font = QFont("Arial", 24, QFont.Bold)
        painter.setFont(title_font)
        painter.drawText(pixmap.rect(), Qt.AlignCenter | Qt.AlignTop, "AI Writer")
        
        # Draw version
        painter.setPen(QColor(180, 180, 180))
        version_font = QFont("Arial", 12)
        painter.setFont(version_font)
        painter.drawText(pixmap.rect().adjusted(0, 40, 0, 0), Qt.AlignCenter | Qt.AlignTop, "Version 0.2.0")
        
        # Draw emoji/icon
        emoji_font = QFont("Arial", 48)
        painter.setFont(emoji_font)
        painter.setPen(QColor(100, 150, 255))
        painter.drawText(pixmap.rect().adjusted(0, -50, 0, 0), Qt.AlignCenter, "✍️")
        
        # Draw loading text area
        painter.setPen(QColor(200, 200, 200))
        status_font = QFont("Arial", 10)
        painter.setFont(status_font)
        painter.drawText(pixmap.rect().adjusted(0, 0, 0, -30), Qt.AlignCenter | Qt.AlignBottom, "Loading...")
        
        painter.end()
        
        super().__init__(pixmap, Qt.WindowStaysOnTopHint)
        
        # Set up progress tracking
        self.progress_steps = [
            "Initializing application...",
            "Loading configuration...",
            "Setting up UI components...",
            "Initializing prompt templates...",
            "Connecting to services...",
            "Ready!"
        ]
        self.current_step = 0
    
    def show_message(self, message: str):
        """Show a status message on the splash screen.
        
        Args:
            message: Status message to display
        """
        self.showMessage(
            message, 
            Qt.AlignCenter | Qt.AlignBottom,
            QColor(200, 200, 200)
        )
        QApplication.processEvents()


class SplashManager:
    """Manager for handling splash screen lifecycle."""
    
    def __init__(self):
        """Initialize the splash manager."""
        self.splash = None
        self.timer = None
        self.step_delay = 500  # milliseconds between steps
        
    def show_splash(self):
        """Show the splash screen."""
        self.splash = SplashScreen()
        self.splash.show()
        self.splash.show_message("Initializing AI Writer...")
        QApplication.processEvents()
    
    def simulate_startup_progress(self, completion_callback):
        """Simulate startup progress with the splash screen.
        
        Args:
            completion_callback: Function to call when startup is complete
        """
        if not self.splash:
            completion_callback()
            return
        
        self.completion_callback = completion_callback
        self.current_step = 0
        
        # Start the progress simulation
        self.timer = QTimer()
        self.timer.timeout.connect(self._next_step)
        self.timer.start(self.step_delay)
    
    def _next_step(self):
        """Process the next startup step."""
        if not self.splash:
            return
            
        steps = [
            "Initializing application...",
            "Loading configuration...",
            "Setting up UI components...", 
            "Initializing prompt templates...",
            "Checking spell check availability...",
            "Connecting to services...",
            "Ready!"
        ]
        
        if self.current_step < len(steps):
            self.splash.show_message(steps[self.current_step])
            self.current_step += 1
        else:
            # Startup complete
            self.timer.stop()
            self.timer = None
            
            # Hide splash screen and show main window
            if self.splash:
                self.splash.close()
                self.splash = None
            
            # Call completion callback
            if self.completion_callback:
                self.completion_callback()
    
    def close_splash(self):
        """Manually close the splash screen."""
        if self.timer:
            self.timer.stop()
            self.timer = None
            
        if self.splash:
            self.splash.close()
            self.splash = None