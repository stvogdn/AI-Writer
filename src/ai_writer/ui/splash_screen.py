"""Splash screen for the AI Writer application."""

from PyQt5.QtCore import QPropertyAnimation, QRect, Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QPainter, QPaintEvent
from PyQt5.QtWidgets import QLabel, QProgressBar, QSplashScreen, QVBoxLayout, QWidget


class SplashScreen(QSplashScreen):
    """Custom splash screen with progress indicator and fade effects."""
    
    progress_updated = pyqtSignal(str)  # Signal for progress updates
    
    def __init__(self):
        """Initialize the splash screen."""
        super().__init__()
        
        # Configure splash screen window
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(400, 300)
        
        # Center the splash screen
        self._center_on_screen()
        
        # Setup UI
        self._setup_ui()
        
        # Animation for fade in/out
        self.fade_animation = QPropertyAnimation(self)
        self.fade_animation.setTargetObject(self)
        self.fade_animation.setPropertyName(b"windowOpacity")
        
        # Progress tracking
        self.current_progress = 0
        self.max_progress = 100
        
    def _center_on_screen(self):
        """Center the splash screen on the primary screen."""
        from PyQt5.QtWidgets import QDesktopWidget
        
        desktop = QDesktopWidget()
        screen_geometry = desktop.screenGeometry()
        splash_geometry = self.geometry()
        
        x = (screen_geometry.width() - splash_geometry.width()) // 2
        y = (screen_geometry.height() - splash_geometry.height()) // 2
        
        self.move(x, y)
        
    def _setup_ui(self):
        """Setup the splash screen UI elements."""
        # Create main widget and layout
        widget = QWidget()
        widget.setStyleSheet("""
            QWidget {
                background-color: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 rgba(0, 122, 255, 200),
                    stop: 1 rgba(88, 86, 214, 200)
                );
                border-radius: 15px;
                border: 2px solid rgba(255, 255, 255, 100);
            }
        """)
        
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Application title
        title_label = QLabel("AI Writer")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 32px;
                font-weight: bold;
                background: transparent;
                border: none;
            }
        """)
        layout.addWidget(title_label)
        
        # Version label
        version_label = QLabel("Version 0.1.0")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 180);
                font-size: 14px;
                background: transparent;
                border: none;
            }
        """)
        layout.addWidget(version_label)
        
        # Description
        desc_label = QLabel("AI-Powered Writing Assistant")
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 160);
                font-size: 16px;
                font-style: italic;
                background: transparent;
                border: none;
            }
        """)
        layout.addWidget(desc_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid rgba(255, 255, 255, 100);
                border-radius: 8px;
                text-align: center;
                background-color: rgba(255, 255, 255, 50);
                color: white;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: rgba(255, 255, 255, 180);
                border-radius: 6px;
                margin: 1px;
            }
        """)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(self.max_progress)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Initializing...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 220);
                font-size: 12px;
                background: transparent;
                border: none;
            }
        """)
        layout.addWidget(self.status_label)
        
        # Set widget
        widget.setFixedSize(400, 300)
        self.setPixmap(widget.grab())
        
        # Connect progress signal
        self.progress_updated.connect(self._update_status)
        
    def show_with_fade(self):
        """Show the splash screen with fade-in animation."""
        self.setWindowOpacity(0.0)
        self.show()
        
        self.fade_animation.setDuration(500)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.start()
        
    def close_with_fade(self, callback=None):
        """Close the splash screen with fade-out animation."""
        self.fade_animation.setDuration(300)
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        
        if callback:
            self.fade_animation.finished.connect(callback)
            
        self.fade_animation.finished.connect(self.close)
        self.fade_animation.start()
        
    def update_progress(self, value: int, status: str = ""):
        """Update the progress bar and status message.
        
        Args:
            value: Progress value (0-100)
            status: Status message to display
        """
        self.current_progress = min(value, self.max_progress)
        self.progress_bar.setValue(self.current_progress)
        
        if status:
            self.status_label.setText(status)
            
        # Process events to update UI
        from PyQt5.QtWidgets import QApplication
        QApplication.processEvents()
        
    def _update_status(self, status: str):
        """Update status label text."""
        self.status_label.setText(status)


class SplashManager:
    """Manager for splash screen lifecycle and progress updates."""
    
    def __init__(self):
        """Initialize the splash manager.""" 
        self.splash = SplashScreen()
        self.startup_tasks = [
            ("Loading configuration...", 20),
            ("Initializing UI components...", 40),
            ("Connecting to Ollama...", 60),
            ("Scanning available models...", 80),
            ("Finalizing setup...", 100)
        ]
        self.current_task = 0
        
    def show_splash(self):
        """Show the splash screen."""
        self.splash.show_with_fade()
        
    def simulate_startup_progress(self, callback=None):
        """Simulate startup progress with realistic tasks.
        
        Args:
            callback: Function to call when startup is complete
        """
        def process_next_task():
            if self.current_task < len(self.startup_tasks):
                status, progress = self.startup_tasks[self.current_task]
                self.splash.update_progress(progress, status)
                self.current_task += 1
                
                # Schedule next task
                QTimer.singleShot(300 + (progress * 5), process_next_task)
            else:
                # Startup complete
                QTimer.singleShot(200, lambda: self.close_splash(callback))
                
        # Start the first task
        process_next_task()
        
    def close_splash(self, callback=None):
        """Close the splash screen.
        
        Args:
            callback: Function to call after splash closes
        """
        self.splash.close_with_fade(callback)
        
    def update_progress(self, value: int, status: str = ""):
        """Update progress manually.
        
        Args:
            value: Progress value (0-100) 
            status: Status message
        """
        self.splash.update_progress(value, status)