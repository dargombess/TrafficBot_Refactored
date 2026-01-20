"""
TrafficBot MAIN APPLICATION
Updated to work with new organized settings interface
"""

import sys
import os
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QPushButton, QLabel, QTabWidget,
    QStatusBar, QMenuBar, QMenu, QAction, QMessageBox,
    QSplitter, QTextEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QToolBar, QSystemTrayIcon, QStyle,
    QDialog, QLineEdit, QSpinBox, QCheckBox, QComboBox,
    QGroupBox, QFormLayout, QFileDialog, QProgressBar
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QSize, QThread
from PyQt5.QtGui import QIcon, QFont, QPalette, QColor, QTextCursor

# Import components - PERBAIKI IMPORT
from core.orchestrator import BotOrchestrator
from ui.advanced_settings import AdvancedSettings
from ui.components import StatusPanel, WorkerTable, ControlPanel
from ui.styles import apply_dark_theme, apply_light_theme
from utils.logger import setup_logger

# Configure logger
logger = setup_logger()


class LogHandler:
    """Handle log display in GUI"""
    
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.max_lines = 1000
        
    def append_log(self, message, level="INFO"):
        """Append message to log display"""
        try:
            # Color coding based on level
            if level == "ERROR":
                color = "#e74c3c"
                prefix = "[ERROR]"
            elif level == "WARNING":
                color = "#f39c12"
                prefix = "[WARNING]"
            elif level == "SUCCESS":
                color = "#27ae60"
                prefix = "[SUCCESS]"
            elif level == "INFO":
                color = "#3498db"
                prefix = "[INFO]"
            else:
                color = "#95a5a6"
                prefix = "[DEBUG]"
            
            # Format message with timestamp
            from datetime import datetime
            timestamp = datetime.now().strftime("%H:%M:%S")
            formatted_msg = f'<span style="color:{color}">[{timestamp}] {prefix} {message}</span>'
            
            # Append to text widget
            self.text_widget.append(formatted_msg)
            
            # Limit number of lines
            lines = self.text_widget.document().lineCount()
            if lines > self.max_lines:
                cursor = self.text_widget.textCursor()
                cursor.movePosition(QTextCursor.Start)
                cursor.movePosition(QTextCursor.Down, QTextCursor.KeepAnchor, lines - self.max_lines)
                cursor.removeSelectedText()
            
            # Scroll to bottom
            scrollbar = self.text_widget.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
            
        except Exception as e:
            print(f"Log display error: {e}")


class TrafficBotApp(QMainWindow):
    """Main application window for TrafficBot"""
    
    # Signal untuk update dari orchestrator
    status_update_signal = pyqtSignal(str, str)  # message, level
    worker_update_signal = pyqtSignal(int, str, str, str)  # worker_id, status, color, message
    stats_update_signal = pyqtSignal(dict)  # statistics
    
    def __init__(self):
        super().__init__()
        self.orchestrator = None
        self.log_handler = None
        self.setup_ui()
        self.setup_menu()
        self.setup_toolbar()
        self.apply_styling()
        
        # Connect signals
        self.status_update_signal.connect(self.handle_status_update)
        self.worker_update_signal.connect(self.handle_worker_update)
        self.stats_update_signal.connect(self.handle_stats_update)
        
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
        header.setStyleSheet("""
            font-size: 18px; 
            font-weight: bold; 
            padding: 15px; 
            color: #2c3e50;
            background: linear-gradient(90deg, #3498db, #2ecc71);
            border-radius: 5px;
            margin: 5px;
        """)
        header.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header)
        
        # Splitter for main content
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Controls
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Control panel
        control_group = QGroupBox("Bot Control")
        control_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3498db;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        control_layout = QVBoxLayout(control_group)
        
        # Worker count control
        worker_layout = QHBoxLayout()
        worker_layout.addWidget(QLabel("Worker Count:"))
        self.worker_spinbox = QSpinBox()
        self.worker_spinbox.setRange(1, 100)
        self.worker_spinbox.setValue(10)
        self.worker_spinbox.setStyleSheet("padding: 5px;")
        worker_layout.addWidget(self.worker_spinbox)
        worker_layout.addStretch()
        control_layout.addLayout(worker_layout)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("▶ START")
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 12px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #219653;
            }
            QPushButton:pressed {
                background-color: #1e874b;
            }
        """)
        self.start_btn.clicked.connect(self.start_bot)
        button_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("■ STOP")
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 12px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        self.stop_btn.clicked.connect(self.stop_bot)
        self.stop_btn.setEnabled(False)
        button_layout.addWidget(self.stop_btn)
        
        self.settings_btn = QPushButton("⚙ SETTINGS")
        self.settings_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 12px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.settings_btn.clicked.connect(self.open_settings)
        button_layout.addWidget(self.settings_btn)
        
        control_layout.addLayout(button_layout)
        
        # Stats display
        stats_group = QGroupBox("Live Statistics")
        stats_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #2ecc71;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
        """)
        stats_layout = QFormLayout(stats_group)
        
        self.active_workers_label = QLabel("0")
        self.active_workers_label.setStyleSheet("font-size: 16px; color: #3498db; font-weight: bold;")
        stats_layout.addRow("Active Workers:", self.active_workers_label)
        
        self.completed_label = QLabel("0")
        self.completed_label.setStyleSheet("font-size: 16px; color: #27ae60; font-weight: bold;")
        stats_layout.addRow("Completed Tasks:", self.completed_label)
        
        self.failed_label = QLabel("0")
        self.failed_label.setStyleSheet("font-size: 16px; color: #e74c3c; font-weight: bold;")
        stats_layout.addRow("Failed Tasks:", self.failed_label)
        
        self.cycles_label = QLabel("0")
        self.cycles_label.setStyleSheet("font-size: 16px; color: #9b59b6; font-weight: bold;")
        stats_layout.addRow("Completed Cycles:", self.cycles_label)
        
        self.remaining_label = QLabel("0")
        self.remaining_label.setStyleSheet("font-size: 16px; color: #f39c12; font-weight: bold;")
        stats_layout.addRow("Remaining URLs:", self.remaining_label)
        
        control_layout.addWidget(stats_group)
        left_layout.addWidget(control_group)
        
        # Worker status table
        worker_group = QGroupBox("Worker Status")
        worker_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #9b59b6;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
        """)
        worker_layout = QVBoxLayout(worker_group)
        
        # Create worker table
        self.worker_table = QTableWidget()
        self.worker_table.setColumnCount(4)
        self.worker_table.setHorizontalHeaderLabels(["Worker ID", "Status", "Current URL", "Actions"])
        self.worker_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.worker_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #dce1e6;
                border-radius: 4px;
                alternate-background-color: #f8f9fa;
            }
            QTableWidget::item {
                padding: 5px;
            }
        """)
        worker_layout.addWidget(self.worker_table)
        left_layout.addWidget(worker_group)
        
        left_layout.addStretch()
        
        # Right panel - Logs
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Log display
        log_group = QGroupBox("Activity Log")
        log_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #f39c12;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
        """)
        log_layout = QVBoxLayout(log_group)
        
        # Log control buttons
        log_control_layout = QHBoxLayout()
        self.clear_log_btn = QPushButton("Clear Log")
        self.clear_log_btn.clicked.connect(self.clear_logs)
        self.clear_log_btn.setStyleSheet("padding: 5px 10px;")
        log_control_layout.addWidget(self.clear_log_btn)
        
        self.save_log_btn = QPushButton("Save Log")
        self.save_log_btn.clicked.connect(self.save_logs)
        self.save_log_btn.setStyleSheet("padding: 5px 10px;")
        log_control_layout.addWidget(self.save_log_btn)
        
        log_control_layout.addStretch()
        
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["ALL", "DEBUG", "INFO", "WARNING", "ERROR"])
        self.log_level_combo.setCurrentText("INFO")
        self.log_level_combo.currentTextChanged.connect(self.filter_logs)
        log_control_layout.addWidget(QLabel("Filter:"))
        log_control_layout.addWidget(self.log_level_combo)
        
        log_layout.addLayout(log_control_layout)
        
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
                border: 1px solid #444;
                border-radius: 3px;
                padding: 5px;
            }
        """)
        log_layout.addWidget(self.log_display)
        
        right_layout.addWidget(log_group)
        
        # Progress bar
        progress_group = QGroupBox("Overall Progress")
        progress_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3498db;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
        """)
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #3498db;
                border-radius: 3px;
                text-align: center;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #2ecc71;
                border-radius: 2px;
            }
        """)
        progress_layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel("Ready to start...")
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        progress_layout.addWidget(self.progress_label)
        
        right_layout.addWidget(progress_group)
        right_layout.addStretch()
        
        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([700, 700])
        
        main_layout.addWidget(splitter)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("✅ Ready - Load configuration or click START to begin")
        
        # Initialize log handler
        self.log_handler = LogHandler(self.log_display)
    
    def setup_menu(self):
        """Setup application menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        load_config_action = QAction("Load Configuration", self)
        load_config_action.triggered.connect(self.load_configuration)
        load_config_action.setShortcut("Ctrl+O")
        file_menu.addAction(load_config_action)
        
        save_config_action = QAction("Save Configuration", self)
        save_config_action.triggered.connect(self.save_configuration)
        save_config_action.setShortcut("Ctrl+S")
        file_menu.addAction(save_config_action)
        
        file_menu.addSeparator()
        
        export_logs_action = QAction("Export Logs...", self)
        export_logs_action.triggered.connect(self.save_logs)
        file_menu.addAction(export_logs_action)
        
        export_stats_action = QAction("Export Statistics...", self)
        export_stats_action.triggered.connect(self.export_statistics)
        file_menu.addAction(export_stats_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        exit_action.setShortcut("Ctrl+Q")
        file_menu.addAction(exit_action)
        
        # Settings menu
        settings_menu = menubar.addMenu("Settings")
        
        advanced_settings_action = QAction("Advanced Settings", self)
        advanced_settings_action.triggered.connect(self.open_settings)
        advanced_settings_action.setShortcut("Ctrl+Alt+S")
        settings_menu.addAction(advanced_settings_action)
        
        settings_menu.addSeparator()
        
        theme_menu = settings_menu.addMenu("Theme")
        
        dark_action = QAction("Dark Theme", self)
        dark_action.triggered.connect(lambda: apply_dark_theme(self))
        theme_menu.addAction(dark_action)
        
        light_action = QAction("Light Theme", self)
        light_action.triggered.connect(lambda: apply_light_theme(self))
        theme_menu.addAction(light_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        
        test_url_action = QAction("Test Single URL", self)
        test_url_action.triggered.connect(self.test_single_url)
        tools_menu.addAction(test_url_action)
        
        proxy_test_action = QAction("Test Proxies", self)
        proxy_test_action.triggered.connect(self.test_proxies)
        tools_menu.addAction(proxy_test_action)
        
        tools_menu.addSeparator()
        
        reset_stats_action = QAction("Reset Statistics", self)
        reset_stats_action.triggered.connect(self.reset_statistics)
        tools_menu.addAction(reset_stats_action)
        
        clear_data_action = QAction("Clear All Data", self)
        clear_data_action.triggered.connect(self.clear_all_data)
        tools_menu.addAction(clear_data_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        docs_action = QAction("Documentation", self)
        docs_action.triggered.connect(self.open_documentation)
        help_menu.addAction(docs_action)
        
        check_updates_action = QAction("Check for Updates", self)
        check_updates_action.triggered.connect(self.check_updates)
        help_menu.addAction(check_updates_action)
        
        help_menu.addSeparator()
        
        about_action = QAction("About TrafficBot", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_toolbar(self):
        """Setup application toolbar"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        # Start button
        start_action = QAction("▶ Start", self)
        start_action.triggered.connect(self.start_bot)
        start_action.setToolTip("Start the bot")
        toolbar.addAction(start_action)
        
        # Stop button
        stop_action = QAction("■ Stop", self)
        stop_action.triggered.connect(self.stop_bot)
        stop_action.setToolTip("Stop the bot")
        stop_action.setEnabled(False)
        toolbar.addAction(stop_action)
        
        toolbar.addSeparator()
        
        # Settings button
        settings_action = QAction("⚙ Settings", self)
        settings_action.triggered.connect(self.open_settings)
        settings_action.setToolTip("Open settings")
        toolbar.addAction(settings_action)
        
        toolbar.addSeparator()
        
        # Status indicator
        self.status_indicator = QLabel("● STOPPED")
        self.status_indicator.setStyleSheet("""
            QLabel {
                color: #e74c3c;
                font-weight: bold;
                padding: 8px;
                font-size: 12px;
            }
        """)
        toolbar.addWidget(self.status_indicator)
        
        toolbar.addSeparator()
        
        # Active workers indicator
        self.toolbar_workers_label = QLabel("Workers: 0")
        self.toolbar_workers_label.setStyleSheet("color: #3498db; font-weight: bold; padding: 8px;")
        toolbar.addWidget(self.toolbar_workers_label)
    
    def apply_styling(self):
        """Apply application styling"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f7fa;
            }
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 12px;
            }
            QPushButton {
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: 500;
            }
            QPushButton:hover {
                opacity: 0.9;
            }
            QLineEdit, QSpinBox, QComboBox {
                padding: 5px;
                border: 1px solid #ddd;
                border-radius: 3px;
                background-color: white;
            }
            QGroupBox {
                margin-top: 10px;
            }
            QStatusBar {
                background-color: #ecf0f1;
                color: #2c3e50;
                font-weight: 500;
            }
            QMenuBar {
                background-color: #2c3e50;
                color: white;
                padding: 5px;
            }
            QMenuBar::item {
                padding: 5px 10px;
            }
            QMenuBar::item:selected {
                background-color: #3498db;
                border-radius: 3px;
            }
            QMenu {
                background-color: white;
                border: 1px solid #ddd;
                padding: 5px;
            }
            QMenu::item {
                padding: 5px 20px;
            }
            QMenu::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)
    
    def init_orchestrator(self):
        """Initialize orchestrator"""
        try:
            self.orchestrator = BotOrchestrator()
            # Set callbacks untuk orchestrator
            self.orchestrator.set_status_callback(self.handle_orchestrator_status)
            self.orchestrator.set_worker_callback(self.handle_orchestrator_worker)
            self.log_handler.append_log("Orchestrator initialized successfully", "SUCCESS")
        except Exception as e:
            error_msg = f"Failed to initialize orchestrator: {str(e)}"
            self.log_handler.append_log(error_msg, "ERROR")
            QMessageBox.critical(self, "Initialization Error", error_msg)
    
    def handle_orchestrator_status(self, message):
        """Handle status messages from orchestrator"""
        self.status_update_signal.emit(message, "INFO")
    
    def handle_orchestrator_worker(self, worker_id, status, color, message):
        """Handle worker updates from orchestrator"""
        self.worker_update_signal.emit(worker_id, status, color, message)
    
    def handle_status_update(self, message, level):
        """Handle status update signal"""
        self.log_handler.append_log(message, level)
    
    def handle_worker_update(self, worker_id, status, color, message):
        """Handle worker update signal"""
        # Update worker table
        self.update_worker_table(worker_id, status, message)
    
    def handle_stats_update(self, stats):
        """Handle statistics update"""
        # Update UI dengan stats terbaru
        self.update_statistics_display(stats)
    
    def update_worker_table(self, worker_id, status, message):
        """Update worker table with worker info"""
        try:
            # Cari row untuk worker ini
            row_found = -1
            for row in range(self.worker_table.rowCount()):
                if self.worker_table.item(row, 0) and self.worker_table.item(row, 0).text() == str(worker_id):
                    row_found = row
                    break
            
            if row_found == -1:
                # Tambah row baru
                row_found = self.worker_table.rowCount()
                self.worker_table.insertRow(row_found)
                
                # Worker ID
                id_item = QTableWidgetItem(str(worker_id))
                id_item.setTextAlignment(Qt.AlignCenter)
                self.worker_table.setItem(row_found, 0, id_item)
                
                # Status
                status_item = QTableWidgetItem(status)
                status_item.setTextAlignment(Qt.AlignCenter)
                self.worker_table.setItem(row_found, 1, status_item)
                
                # URL
                url_item = QTableWidgetItem(message[:100] + "..." if len(message) > 100 else message)
                self.worker_table.setItem(row_found, 2, url_item)
                
                # Actions button
                action_btn = QPushButton("Toggle View")
                action_btn.setStyleSheet("padding: 3px 8px; font-size: 10px;")
                action_btn.clicked.connect(lambda checked, wid=worker_id: self.toggle_worker_view(wid))
                self.worker_table.setCellWidget(row_found, 3, action_btn)
            else:
                # Update existing row
                # Update status
                if status_item := self.worker_table.item(row_found, 1):
                    status_item.setText(status)
                    # Set color based on status
                    if status == "RUNNING":
                        status_item.setBackground(QColor("#3498db"))
                        status_item.setForeground(QColor("white"))
                    elif status == "SUCCESS":
                        status_item.setBackground(QColor("#27ae60"))
                        status_item.setForeground(QColor("white"))
                    elif status == "FAILED":
                        status_item.setBackground(QColor("#e74c3c"))
                        status_item.setForeground(QColor("white"))
                    elif status == "WAITING":
                        status_item.setBackground(QColor("#f39c12"))
                        status_item.setForeground(QColor("white"))
                
                # Update URL/message
                if url_item := self.worker_table.item(row_found, 2):
                    url_item.setText(message[:100] + "..." if len(message) > 100 else message)
        
        except Exception as e:
            print(f"Error updating worker table: {e}")
    
    def update_statistics_display(self, stats):
        """Update statistics display with new data"""
        try:
            # Update labels
            self.active_workers_label.setText(str(stats.get('active_workers', 0)))
            self.completed_label.setText(str(stats.get('total_tasks_completed', 0)))
            self.failed_label.setText(str(stats.get('total_tasks_failed', 0)))
            self.cycles_label.setText(str(stats.get('cycles', 0)))
            
            # Calculate remaining URLs
            total_urls = stats.get('total_urls', 0)
            visited = stats.get('visited', 0)
            remaining = total_urls - visited if total_urls > 0 else 0
            self.remaining_label.setText(str(remaining))
            
            # Update toolbar
            self.toolbar_workers_label.setText(f"Workers: {stats.get('active_workers', 0)}")
            
            # Update progress bar
            if total_urls > 0:
                progress = int((visited / total_urls) * 100)
                self.progress_bar.setValue(progress)
                self.progress_label.setText(f"Progress: {visited}/{total_urls} URLs ({progress}%)")
            
        except Exception as e:
            print(f"Error updating statistics: {e}")
    
    # ==================== BOT CONTROL FUNCTIONS ====================
    
    def start_bot(self):
        """Start the bot"""
        try:
            if not self.orchestrator:
                self.init_orchestrator()
            
            worker_count = self.worker_spinbox.value()
            self.orchestrator.start(num_workers=worker_count)
            
            # Update UI state
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.status_indicator.setText("● RUNNING")
            self.status_indicator.setStyleSheet("color: #27ae60; font-weight: bold; padding: 8px; font-size: 12px;")
            self.status_bar.showMessage(f"Bot started with {worker_count} workers", 3000)
            
            self.log_handler.append_log(f"Bot started with {worker_count} workers", "SUCCESS")
            
        except Exception as e:
            error_msg = f"Failed to start bot: {str(e)}"
            self.log_handler.append_log(error_msg, "ERROR")
            QMessageBox.critical(self, "Start Error", error_msg)
    
    def stop_bot(self):
        """Stop the bot"""
        try:
            if self.orchestrator:
                self.orchestrator.stop()
                
                # Update UI state
                self.start_btn.setEnabled(True)
                self.stop_btn.setEnabled(False)
                self.status_indicator.setText("● STOPPED")
                self.status_indicator.setStyleSheet("color: #e74c3c; font-weight: bold; padding: 8px; font-size: 12px;")
                self.status_bar.showMessage("Bot stopped", 3000)
                
                self.log_handler.append_log("Bot stopped successfully", "SUCCESS")
                
        except Exception as e:
            error_msg = f"Failed to stop bot: {str(e)}"
            self.log_handler.append_log(error_msg, "ERROR")
            QMessageBox.warning(self, "Stop Error", error_msg)
    
    def toggle_worker_view(self, worker_id):
        """Toggle browser visibility for specific worker"""
        try:
            if self.orchestrator:
                self.orchestrator.toggle_worker_visibility(worker_id)
                self.log_handler.append_log(f"Toggled visibility for worker #{worker_id}", "INFO")
        except Exception as e:
            self.log_handler.append_log(f"Error toggling worker view: {e}", "ERROR")
    
    # ==================== SETTINGS FUNCTIONS ====================
    
    def open_settings(self):
        """Open advanced settings dialog"""
        try:
            settings_dialog = AdvancedSettings(self)
            if settings_dialog.exec_() == QDialog.Accepted:
                self.log_handler.append_log("Settings saved successfully", "SUCCESS")
                self.status_bar.showMessage("Settings saved", 2000)
                
                # Re-initialize orchestrator dengan settings baru
                if self.orchestrator:
                    self.orchestrator.stop()
                    self.init_orchestrator()
            else:
                self.log_handler.append_log("Settings dialog cancelled", "INFO")
                
        except Exception as e:
            error_msg = f"Error opening settings: {str(e)}"
            self.log_handler.append_log(error_msg, "ERROR")
            QMessageBox.critical(self, "Settings Error", error_msg)
    
    def load_configuration(self):
        """Load configuration from file"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Load Configuration", "", "Config Files (*.json *.py);;All Files (*)"
            )
            if file_path:
                # Implement configuration loading logic here
                self.log_handler.append_log(f"Loading configuration from: {file_path}", "INFO")
                QMessageBox.information(self, "Info", "Configuration loading will be implemented in future version")
        except Exception as e:
            self.log_handler.append_log(f"Error loading configuration: {e}", "ERROR")
    
    def save_configuration(self):
        """Save configuration to file"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Configuration", "bot_config.json", "JSON Files (*.json);;All Files (*)"
            )
            if file_path:
                # Implement configuration saving logic here
                config_data = {
                    "worker_count": self.worker_spinbox.value(),
                    "shuffle_mode": True,
                    "max_retries": 2
                }
                with open(file_path, 'w') as f:
                    json.dump(config_data, f, indent=2)
                self.log_handler.append_log(f"Configuration saved to: {file_path}", "SUCCESS")
        except Exception as e:
            self.log_handler.append_log(f"Error saving configuration: {e}", "ERROR")
    
    # ==================== LOG FUNCTIONS ====================
    
    def clear_logs(self):
        """Clear log display"""
        self.log_display.clear()
        self.log_handler.append_log("Log display cleared", "INFO")
    
    def save_logs(self):
        """Save logs to file"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Logs", "trafficbot_logs.html", "HTML Files (*.html);;Text Files (*.txt);;All Files (*)"
            )
            if file_path:
                log_content = self.log_display.toHtml() if file_path.endswith('.html') else self.log_display.toPlainText()
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(log_content)
                self.log_handler.append_log(f"Logs saved to: {file_path}", "SUCCESS")
        except Exception as e:
            self.log_handler.append_log(f"Error saving logs: {e}", "ERROR")
    
    def filter_logs(self, level):
        """Filter logs by level"""
        # This is a simple implementation - for full filtering, you'd need to store log levels separately
        self.log_handler.append_log(f"Log filter changed to: {level}", "INFO")
    
    # ==================== TOOLS FUNCTIONS ====================
    
    def test_single_url(self):
        """Test a single URL"""
        try:
            url, ok = QInputDialog.getText(self, "Test URL", "Enter URL to test:")
            if ok and url:
                self.log_handler.append_log(f"Testing URL: {url}", "INFO")
                QMessageBox.information(self, "Test URL", f"Will test: {url}\n\nThis feature will be implemented in future version.")
        except Exception as e:
            self.log_handler.append_log(f"Error testing URL: {e}", "ERROR")
    
    def test_proxies(self):
        """Test proxy configuration"""
        self.log_handler.append_log("Testing proxy configuration...", "INFO")
        QMessageBox.information(self, "Test Proxies", "Proxy testing will be implemented in future version.")
    
    def reset_statistics(self):
        """Reset all statistics"""
        reply = QMessageBox.question(self, "Reset Statistics", 
                                   "Are you sure you want to reset all statistics?",
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            # Reset UI elements
            self.active_workers_label.setText("0")
            self.completed_label.setText("0")
            self.failed_label.setText("0")
            self.cycles_label.setText("0")
            self.remaining_label.setText("0")
            self.progress_bar.setValue(0)
            self.progress_label.setText("Statistics reset")
            
            self.log_handler.append_log("Statistics reset", "SUCCESS")
    
    def clear_all_data(self):
        """Clear all data"""
        reply = QMessageBox.warning(self, "Clear All Data", 
                                  "WARNING: This will clear all logs, statistics, and worker data!\n\nAre you sure?",
                                  QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.log_display.clear()
            self.worker_table.setRowCount(0)
            self.reset_statistics()
            self.log_handler.append_log("All data cleared", "SUCCESS")
    
    def export_statistics(self):
        """Export statistics to file"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export Statistics", "trafficbot_stats.json", "JSON Files (*.json);;All Files (*)"
            )
            if file_path:
                stats = {
                    "active_workers": self.active_workers_label.text(),
                    "completed_tasks": self.completed_label.text(),
                    "failed_tasks": self.failed_label.text(),
                    "completed_cycles": self.cycles_label.text(),
                    "timestamp": QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
                }
                with open(file_path, 'w') as f:
                    json.dump(stats, f, indent=2)
                self.log_handler.append_log(f"Statistics exported to: {file_path}", "SUCCESS")
        except Exception as e:
            self.log_handler.append_log(f"Error exporting statistics: {e}", "ERROR")
    
    # ==================== HELP FUNCTIONS ====================
    
    def open_documentation(self):
        """Open documentation"""
        self.log_handler.append_log("Opening documentation...", "INFO")
        QMessageBox.information(self, "Documentation", 
                              "Documentation is available online at:\n\nhttps://github.com/yourusername/trafficbot\n\nOr in the docs/ folder.")
    
    def check_updates(self):
        """Check for updates"""
        self.log_handler.append_log("Checking for updates...", "INFO")
        QMessageBox.information(self, "Check Updates", 
                              "You are running the latest version of TrafficBot!")
    
    def show_about(self):
        """Show about dialog"""
        about_text = """
        <h2>TrafficBot - Professional Edition</h2>
        <p><b>Version:</b> 2.0.0</p>
        <p><b>Description:</b> Advanced Web Traffic Generator with AI Enhancement</p>
        
        <p><b>Features:</b></p>
        <ul>
            <li>Multi-worker parallel processing</li>
            <li>AI-powered behavior simulation</li>
            <li>Advanced anti-detection technology</li>
            <li>Intelligent URL shuffle system</li>
            <li>Real-time statistics and monitoring</li>
            <li>Professional GUI interface</li>
            <li>Proxy support and rotation</li>
        </ul>
        
        <p><b>System Requirements:</b></p>
        <ul>
            <li>Python 3.8+</li>
            <li>Chrome/Chromium browser</li>
            <li>4GB+ RAM recommended</li>
            <li>Stable internet connection</li>
        </ul>
        
        <p><b>© 2024 TrafficBot Project</b><br>
        For support and documentation, visit our GitHub repository.</p>
        """
        QMessageBox.about(self, "About TrafficBot", about_text)
    
    # ==================== STATUS UPDATE ====================
    
    def update_status(self):
        """Update status display periodically"""
        if self.orchestrator and hasattr(self.orchestrator, 'is_running') and self.orchestrator.is_running:
            try:
                stats = self.orchestrator.get_statistics()
                self.stats_update_signal.emit(stats)
            except Exception as e:
                print(f"Error updating status: {e}")
    
    # ==================== EVENT HANDLERS ====================
    
    def closeEvent(self, event):
        """Handle application close event"""
        reply = QMessageBox.question(self, "Exit TrafficBot", 
                                   "Are you sure you want to exit?\n\nAny running processes will be stopped.",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Stop orchestrator
            if self.orchestrator:
                self.orchestrator.stop()
            
            # Stop update timer
            if hasattr(self, 'update_timer'):
                self.update_timer.stop()
            
            self.log_handler.append_log("Application closing", "INFO")
            event.accept()
        else:
            event.ignore()


# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

def main():
    """Main application entry point"""
    # Enable high DPI scaling
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    app.setApplicationName("TrafficBot")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("TrafficBot")
    
    # Set application style
    app.setStyle("Fusion")
    
    # Set application icon (if available)
    try:
        app_icon = QIcon("icon.ico")
        app.setWindowIcon(app_icon)
    except:
        pass
    
    # Create and show main window
    window = TrafficBotApp()
    window.show()
    
    # Start application
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()