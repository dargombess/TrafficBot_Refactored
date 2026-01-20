"""
TrafficBot MAIN APPLICATION
Updated to work with new organized settings interface
"""

import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QPushButton, QLabel, QTabWidget,
    QStatusBar, QMenuBar, QMenu, QAction, QMessageBox,
    QSplitter, QTextEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QToolBar, QSystemTrayIcon, QStyle,
    QDialog
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt5.QtGui import QIcon, QFont, QPalette, QColor

# Import components
from core.orchestrator import BotOrchestrator
from ui.advanced_settings import AdvancedSettings
from ui.components import StatusPanel, WorkerTable, ControlPanel
from ui.styles import apply_dark_theme, apply_light_theme
from ui.logger import setup_logger, log_to_gui

# Configure logger
logger = setup_logger()


class TrafficBotApp(QMainWindow):
    """Main application window for TrafficBot"""
    
    def __init__(self):
        super().__init__()
        self.orchestrator = None
        self.setup_ui()
        self.setup_menu()
        self.setup_toolbar()
        self.apply_styling()
        
        # Initialize orchestrator
        self.init_orchestrator()
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_status)
        self.update_timer.start(1000)  # Update every second
        
        logger.info("TrafficBot application started")
    
    def setup_ui(self):
        """Setup main user interface"""
        self.setWindowTitle("TrafficBot - Advanced Web Traffic Generator")
        self.setGeometry(100, 100, 1400, 800)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Header
        header = QLabel("🚀 TrafficBot - Professional Web Traffic Generator")
        header.setStyleSheet("font-size: 18px; font-weight: bold; padding: 15px; color: #2c3e50;")
        header.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header)
        
        # Splitter for main content
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Controls
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Control panel from components
        self.control_panel = ControlPanel()
        self.control_panel.start_signal.connect(self.start_bot)
        self.control_panel.stop_signal.connect(self.stop_bot)
        self.control_panel.pause_signal.connect(self.pause_bot)
        left_layout.addWidget(self.control_panel)
        
        # Worker table
        self.worker_table = WorkerTable()
        left_layout.addWidget(self.worker_table)
        
        # Right panel - Logs and status
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Status panel
        self.status_panel = StatusPanel()
        right_layout.addWidget(self.status_panel)
        
        # Log display
        log_label = QLabel("Activity Log")
        log_label.setStyleSheet("font-weight: bold; padding: 5px;")
        right_layout.addWidget(log_label)
        
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setMaximumHeight(300)
        right_layout.addWidget(self.log_display)
        
        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([700, 700])
        
        main_layout.addWidget(splitter)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Setup log redirection
        log_to_gui(self.log_display)
    
    def setup_menu(self):
        """Setup application menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        new_action = QAction("New Session", self)
        new_action.triggered.connect(self.new_session)
        file_menu.addAction(new_action)
        
        load_action = QAction("Load Session", self)
        load_action.triggered.connect(self.load_session)
        file_menu.addAction(load_action)
        
        save_action = QAction("Save Session", self)
        save_action.triggered.connect(self.save_session)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        export_action = QAction("Export Logs", self)
        export_action.triggered.connect(self.export_logs)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Settings menu
        settings_menu = menubar.addMenu("Settings")
        
        # THIS IS THE IMPORTANT PART - Settings action
        settings_action = QAction("Advanced Settings", self)
        settings_action.triggered.connect(self.open_settings)
        settings_action.setShortcut("Ctrl+S")
        settings_menu.addAction(settings_action)
        
        theme_menu = settings_menu.addMenu("Theme")
        
        dark_action = QAction("Dark Theme", self)
        dark_action.triggered.connect(lambda: apply_dark_theme(self))
        theme_menu.addAction(dark_action)
        
        light_action = QAction("Light Theme", self)
        light_action.triggered.connect(lambda: apply_light_theme(self))
        theme_menu.addAction(light_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        
        test_action = QAction("Test Configuration", self)
        test_action.triggered.connect(self.test_config)
        tools_menu.addAction(test_action)
        
        proxy_test_action = QAction("Test Proxies", self)
        proxy_test_action.triggered.connect(self.test_proxies)
        tools_menu.addAction(proxy_test_action)
        
        captcha_test_action = QAction("Test CAPTCHA", self)
        captcha_test_action.triggered.connect(self.test_captcha)
        tools_menu.addAction(captcha_test_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        docs_action = QAction("Documentation", self)
        docs_action.triggered.connect(self.open_docs)
        help_menu.addAction(docs_action)
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_toolbar(self):
        """Setup application toolbar"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        # Start button
        start_btn = QPushButton("▶ Start")
        start_btn.clicked.connect(self.start_bot)
        start_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #219653;
            }
        """)
        toolbar.addWidget(start_btn)
        
        # Stop button
        stop_btn = QPushButton("■ Stop")
        stop_btn.clicked.connect(self.stop_bot)
        stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        toolbar.addWidget(stop_btn)
        
        toolbar.addSeparator()
        
        # Settings button
        settings_btn = QPushButton("⚙ Settings")
        settings_btn.clicked.connect(self.open_settings)
        settings_btn.setToolTip("Open advanced settings")
        toolbar.addWidget(settings_btn)
        
        toolbar.addSeparator()
        
        # Status indicator
        self.status_indicator = QLabel("● Stopped")
        self.status_indicator.setStyleSheet("""
            QLabel {
                color: #e74c3c;
                font-weight: bold;
                padding: 8px;
            }
        """)
        toolbar.addWidget(self.status_indicator)
    
    def apply_styling(self):
        """Apply application styling"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f7fa;
            }
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QTextEdit {
                background-color: white;
                border: 1px solid #dce1e6;
                border-radius: 4px;
                font-family: 'Consolas', monospace;
                font-size: 10px;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #dce1e6;
                border-radius: 4px;
                alternate-background-color: #f8f9fa;
            }
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                padding: 5px;
                border: none;
                font-weight: bold;
            }
            QMenuBar {
                background-color: #2c3e50;
                color: white;
            }
            QMenuBar::item:selected {
                background-color: #3498db;
            }
            QMenu {
                background-color: white;
                border: 1px solid #dce1e6;
            }
            QMenu::item:selected {
                background-color: #3498db;
                color: white;
            }
            QStatusBar {
                background-color: #ecf0f1;
                color: #2c3e50;
            }
        """)
    
    def init_orchestrator(self):
        """Initialize orchestrator"""
        try:
            self.orchestrator = BotOrchestrator()
            self.orchestrator.set_status_callback(self.handle_status_update)
            self.orchestrator.set_worker_callback(self.handle_worker_update)
            logger.info("Orchestrator initialized")
        except Exception as e:
            logger.error(f"Failed to initialize orchestrator: {e}")
            QMessageBox.critical(self, "Error", f"Failed to initialize orchestrator: {e}")
    
    def handle_status_update(self, message):
        """Handle status updates from orchestrator"""
        self.log_display.append(f"[STATUS] {message}")
        # Scroll to bottom
        scrollbar = self.log_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def handle_worker_update(self, worker_id, status, color, message):
        """Handle worker updates from orchestrator"""
        # Update worker table if needed
        pass
    
    # ==================== SETTINGS FUNCTIONS ====================
    
    def open_settings(self):
        """
        Open advanced settings dialog
        NOW USING THE NEW TABBED INTERFACE
        """
        try:
            # Create settings dialog
            settings_dialog = AdvancedSettings(self)
            
            # Show dialog
            if settings_dialog.exec_() == QDialog.Accepted:
                logger.info("Settings saved")
                self.status_bar.showMessage("Settings saved successfully", 3000)
            else:
                logger.info("Settings cancelled")
                
        except Exception as e:
            logger.error(f"Error opening settings: {e}")
            QMessageBox.critical(self, "Error", f"Cannot open settings: {e}")
    
    # ==================== BOT CONTROL FUNCTIONS ====================
    
    def start_bot(self):
        """Start the bot"""
        try:
            if self.orchestrator:
                # Get worker count from control panel
                worker_count = self.control_panel.get_worker_count()
                self.orchestrator.start(num_workers=worker_count)
                self.status_indicator.setText("● Running")
                self.status_indicator.setStyleSheet("color: #27ae60; font-weight: bold; padding: 8px;")
                self.status_bar.showMessage("Bot started", 2000)
                logger.info("Bot started")
        except Exception as e:
            logger.error(f"Failed to start bot: {e}")
            QMessageBox.critical(self, "Error", f"Failed to start bot: {e}")
    
    def stop_bot(self):
        """Stop the bot"""
        try:
            if self.orchestrator:
                self.orchestrator.stop()
                self.status_indicator.setText("● Stopped")
                self.status_indicator.setStyleSheet("color: #e74c3c; font-weight: bold; padding: 8px;")
                self.status_bar.showMessage("Bot stopped", 2000)
                logger.info("Bot stopped")
        except Exception as e:
            logger.error(f"Failed to stop bot: {e}")
    
    def pause_bot(self):
        """Pause the bot"""
        try:
            if self.orchestrator:
                self.status_indicator.setText("● Paused")
                self.status_indicator.setStyleSheet("color: #f39c12; font-weight: bold; padding: 8px;")
                self.status_bar.showMessage("Bot paused", 2000)
                logger.info("Bot paused")
        except Exception as e:
            logger.error(f"Failed to pause/resume bot: {e}")
    
    # ==================== UI UPDATE FUNCTIONS ====================
    
    def update_status(self):
        """Update status display"""
        if self.orchestrator:
            stats = self.orchestrator.get_statistics()
            self.status_panel.update_stats(stats)
            
            # Update status bar
            status_text = f"Active Workers: {stats['active_workers']} | "
            status_text += f"Completed: {stats['total_tasks_completed']} | "
            status_text += f"Failed: {stats['total_tasks_failed']} | "
            status_text += f"Cycles: {stats['cycles']}"
            self.status_bar.showMessage(status_text)
    
    # ==================== OTHER MENU FUNCTIONS ====================
    
    def new_session(self):
        """Create new session"""
        reply = QMessageBox.question(self, "New Session", 
                                   "Start a new session? Current data will be cleared.",
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            if self.orchestrator:
                self.orchestrator.stop()
                self.orchestrator = BotOrchestrator()
                self.init_orchestrator()
            self.log_display.clear()
            logger.info("New session started")
    
    def load_session(self):
        """Load session from file"""
        logger.info("Load session requested")
        QMessageBox.information(self, "Info", "Load session functionality will be implemented")
    
    def save_session(self):
        """Save session to file"""
        logger.info("Save session requested")
        QMessageBox.information(self, "Info", "Save session functionality will be implemented")
    
    def export_logs(self):
        """Export logs to file"""
        logger.info("Export logs requested")
        QMessageBox.information(self, "Info", "Export logs functionality will be implemented")
    
    def test_config(self):
        """Test configuration"""
        from bot_config import config
        try:
            # Simple validation
            if not hasattr(config, 'FILE_ARTICLES') or not config.FILE_ARTICLES:
                QMessageBox.warning(self, "Configuration Test", 
                                  "⚠️ Article file not configured!")
                return
            
            if not os.path.exists(config.FILE_ARTICLES):
                QMessageBox.warning(self, "Configuration Test", 
                                  f"⚠️ Article file not found: {config.FILE_ARTICLES}")
                return
            
            QMessageBox.information(self, "Configuration Test", 
                                  "✅ Configuration is valid and ready to use.")
        except Exception as e:
            QMessageBox.warning(self, "Configuration Test", f"❌ Configuration error: {e}")
    
    def test_proxies(self):
        """Test proxy configuration"""
        logger.info("Test proxies requested")
        QMessageBox.information(self, "Info", "Proxy test functionality will be implemented")
    
    def test_captcha(self):
        """Test CAPTCHA configuration"""
        logger.info("Test CAPTCHA requested")
        QMessageBox.information(self, "CAPTCHA Test", 
                              "CAPTCHA configuration test will be implemented in future version.")
    
    def open_docs(self):
        """Open documentation"""
        logger.info("Open documentation requested")
        QMessageBox.information(self, "Documentation", 
                              "Documentation will be available in the next version.")
    
    def show_about(self):
        """Show about dialog"""
        about_text = """
        <h2>TrafficBot</h2>
        <p>Advanced Web Traffic Generator with AI Enhancement</p>
        <p>Version: 2.0.0</p>
        <p>Features:</p>
        <ul>
            <li>Multi-worker parallel processing</li>
            <li>AI-powered behavior simulation</li>
            <li>Advanced fingerprinting and anti-detection</li>
            <li>CAPTCHA solving integration</li>
            <li>Professional dashboard interface</li>
            <li>Infinite loop with intelligent shuffle</li>
        </ul>
        <p>© 2024 TrafficBot Project</p>
        """
        QMessageBox.about(self, "About TrafficBot", about_text)
    
    def closeEvent(self, event):
        """Handle application close event"""
        reply = QMessageBox.question(self, "Exit", 
                                   "Are you sure you want to exit?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Stop orchestrator
            if self.orchestrator:
                self.orchestrator.stop()
            
            # Stop update timer
            self.update_timer.stop()
            
            logger.info("Application closing")
            event.accept()
        else:
            event.ignore()


# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("TrafficBot")
    app.setApplicationVersion("2.0.0")
    
    # Set application style
    app.setStyle("Fusion")
    
    # Create and show main window
    window = TrafficBotApp()
    window.show()
    
    # Start application
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()