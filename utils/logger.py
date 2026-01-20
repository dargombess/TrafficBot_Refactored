"""
Advanced Logger for TrafficBot UI
Features: Colored logs, filtering, export, and real-time updates
"""

import sys
import os
import logging
import html
from datetime import datetime
from typing import Optional, Callable
from PyQt5.QtCore import QObject, pyqtSignal, QTimer, Qt
from PyQt5.QtWidgets import (
    QTextEdit, QApplication, QMenu, QAction, QInputDialog,
    QMessageBox, QFileDialog, QColorDialog
)
from PyQt5.QtGui import (
    QTextCursor, QTextCharFormat, QColor, QFont, 
    QTextDocument, QSyntaxHighlighter, QTextFormat
)


class LogHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for log messages"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighting_rules = []
        
        # Error level
        error_format = QTextCharFormat()
        error_format.setForeground(QColor("#e74c3c"))  # Red
        error_format.setFontWeight(QFont.Bold)
        self.highlighting_rules.append(("\\[ERROR\\].*", error_format))
        
        # Warning level
        warning_format = QTextCharFormat()
        warning_format.setForeground(QColor("#f39c12"))  # Orange
        warning_format.setFontWeight(QFont.Bold)
        self.highlighting_rules.append(("\\[WARNING\\].*", warning_format))
        
        # Success level
        success_format = QTextCharFormat()
        success_format.setForeground(QColor("#27ae60"))  # Green
        success_format.setFontWeight(QFont.Bold)
        self.highlighting_rules.append(("\\[SUCCESS\\].*", success_format))
        
        # Info level
        info_format = QTextCharFormat()
        info_format.setForeground(QColor("#3498db"))  # Blue
        self.highlighting_rules.append(("\\[INFO\\].*", info_format))
        
        # Debug level
        debug_format = QTextCharFormat()
        debug_format.setForeground(QColor("#95a5a6"))  # Gray
        self.highlighting_rules.append(("\\[DEBUG\\].*", debug_format))
        
        # URLs
        url_format = QTextCharFormat()
        url_format.setForeground(QColor("#9b59b6"))  # Purple
        url_format.setFontUnderline(True)
        self.highlighting_rules.append(
            ("(https?://[^\\s]+|www\\.[^\\s]+)", url_format)
        )
        
        # Timestamps
        timestamp_format = QTextCharFormat()
        timestamp_format.setForeground(QColor("#7f8c8d"))  # Dark gray
        timestamp_format.setFontItalic(True)
        self.highlighting_rules.append(
            ("\\[\\d{2}:\\d{2}:\\d{2}\\]", timestamp_format)
        )
        
        # Worker IDs
        worker_format = QTextCharFormat()
        worker_format.setForeground(QColor("#e67e22"))  # Dark orange
        self.highlighting_rules.append(
            ("\\[WORKER #\\d+\\]", worker_format)
        )
        
        # Numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#16a085"))  # Teal
        self.highlighting_rules.append(
            ("\\b\\d+\\b", number_format)
        )
    
    def highlightBlock(self, text):
        """Apply highlighting rules to text block"""
        for pattern, format in self.highlighting_rules:
            import re
            expression = re.compile(pattern)
            
            for match in expression.finditer(text):
                start = match.start()
                length = match.end() - start
                self.setFormat(start, length, format)


class LogEmitter(QObject):
    """Emit log signals from background threads to GUI thread"""
    
    # Signals for different log levels
    log_debug = pyqtSignal(str)
    log_info = pyqtSignal(str)
    log_warning = pyqtSignal(str)
    log_error = pyqtSignal(str)
    log_success = pyqtSignal(str)
    log_custom = pyqtSignal(str, str)  # message, level
    
    # Clear signal
    clear_signal = pyqtSignal()
    
    # Filter signal
    filter_changed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.log_buffer = []
        self.buffer_size = 100
        self.current_filter = "ALL"
        
    def emit(self, message: str, level: str = "INFO"):
        """Emit log message with specified level"""
        # Add to buffer
        self.log_buffer.append((datetime.now(), level, message))
        if len(self.log_buffer) > self.buffer_size:
            self.log_buffer.pop(0)
        
        # Emit based on level
        level = level.upper()
        if level == "DEBUG":
            self.log_debug.emit(message)
        elif level == "INFO":
            self.log_info.emit(message)
        elif level == "WARNING":
            self.log_warning.emit(message)
        elif level == "ERROR":
            self.log_error.emit(message)
        elif level == "SUCCESS":
            self.log_success.emit(message)
        else:
            self.log_custom.emit(message, level)
    
    def clear_buffer(self):
        """Clear log buffer"""
        self.log_buffer.clear()
        self.clear_signal.emit()
    
    def get_buffer(self, filter_level: str = "ALL"):
        """Get filtered log buffer"""
        if filter_level == "ALL":
            return self.log_buffer
        
        filtered = []
        for timestamp, level, message in self.log_buffer:
            if self._level_matches(level, filter_level):
                filtered.append((timestamp, level, message))
        return filtered
    
    def _level_matches(self, actual_level: str, filter_level: str) -> bool:
        """Check if log level matches filter"""
        level_order = ["DEBUG", "INFO", "WARNING", "ERROR", "SUCCESS"]
        
        try:
            actual_index = level_order.index(actual_level.upper())
            filter_index = level_order.index(filter_level.upper())
            return actual_index >= filter_index
        except ValueError:
            return actual_level.upper() == filter_level.upper()


class LogWidget(QTextEdit):
    """Enhanced QTextEdit widget for displaying logs with advanced features"""
    
    # Custom signals
    context_menu_requested = pyqtSignal(int, int)  # x, y positions
    export_requested = pyqtSignal()
    search_requested = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_context_menu()
        self.setup_connections()
        
        # Log settings
        self.max_lines = 5000
        self.auto_scroll = True
        self.word_wrap = True
        self.show_timestamps = True
        self.colored_logs = True
        
        # Search
        self.search_text = ""
        self.search_results = []
        self.current_search_index = -1
        
        # Initialize highlighter
        self.highlighter = LogHighlighter(self.document())
        
        # Custom styles
        self.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 11px;
                border: 1px solid #444;
                border-radius: 3px;
                padding: 5px;
                selection-background-color: #264f78;
            }
        """)
        
        # Set font
        font = QFont("Consolas", 9)
        font.setStyleHint(QFont.Monospace)
        self.setFont(font)
    
    def setup_ui(self):
        """Setup UI elements"""
        self.setReadOnly(True)
        self.setLineWrapMode(QTextEdit.NoWrap)
        
        # Set tab width (4 spaces)
        self.setTabStopWidth(40)
    
    def setup_context_menu(self):
        """Setup right-click context menu"""
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
    
    def setup_connections(self):
        """Setup signal connections"""
        # Connect scrollbar to check auto-scroll
        self.verticalScrollBar().valueChanged.connect(self.check_auto_scroll)
    
    def check_auto_scroll(self, value):
        """Check if user has scrolled away from bottom"""
        scrollbar = self.verticalScrollBar()
        self.auto_scroll = (value == scrollbar.maximum())
    
    def show_context_menu(self, position):
        """Show custom context menu"""
        menu = QMenu(self)
        
        # Copy action
        copy_action = QAction("Copy", self)
        copy_action.triggered.connect(self.copy_selection)
        menu.addAction(copy_action)
        
        # Copy All action
        copy_all_action = QAction("Copy All", self)
        copy_all_action.triggered.connect(self.copy_all)
        menu.addAction(copy_all_action)
        
        menu.addSeparator()
        
        # Clear action
        clear_action = QAction("Clear Logs", self)
        clear_action.triggered.connect(self.clear)
        menu.addAction(clear_action)
        
        menu.addSeparator()
        
        # Search action
        search_action = QAction("Search...", self)
        search_action.triggered.connect(self.show_search_dialog)
        menu.addAction(search_action)
        
        # Find Next action
        find_next_action = QAction("Find Next", self)
        find_next_action.triggered.connect(self.find_next)
        find_next_action.setEnabled(bool(self.search_text))
        menu.addAction(find_next_action)
        
        menu.addSeparator()
        
        # Export submenu
        export_menu = QMenu("Export", self)
        
        export_txt_action = QAction("As Text File", self)
        export_txt_action.triggered.connect(lambda: self.export_logs("txt"))
        export_menu.addAction(export_txt_action)
        
        export_html_action = QAction("As HTML File", self)
        export_html_action.triggered.connect(lambda: self.export_logs("html"))
        export_menu.addAction(export_html_action)
        
        export_csv_action = QAction("As CSV File", self)
        export_csv_action.triggered.connect(lambda: self.export_logs("csv"))
        export_menu.addAction(export_csv_action)
        
        menu.addMenu(export_menu)
        
        menu.addSeparator()
        
        # Settings submenu
        settings_menu = QMenu("Settings", self)
        
        # Timestamp toggle
        timestamp_action = QAction("Show Timestamps", self)
        timestamp_action.setCheckable(True)
        timestamp_action.setChecked(self.show_timestamps)
        timestamp_action.triggered.connect(self.toggle_timestamps)
        settings_menu.addAction(timestamp_action)
        
        # Color toggle
        color_action = QAction("Colored Logs", self)
        color_action.setCheckable(True)
        color_action.setChecked(self.colored_logs)
        color_action.triggered.connect(self.toggle_colors)
        settings_menu.addAction(color_action)
        
        # Word wrap toggle
        wrap_action = QAction("Word Wrap", self)
        wrap_action.setCheckable(True)
        wrap_action.setChecked(self.word_wrap)
        wrap_action.triggered.connect(self.toggle_word_wrap)
        settings_menu.addAction(wrap_action)
        
        # Auto-scroll toggle
        scroll_action = QAction("Auto-scroll", self)
        scroll_action.setCheckable(True)
        scroll_action.setChecked(self.auto_scroll)
        scroll_action.triggered.connect(self.toggle_auto_scroll)
        settings_menu.addAction(scroll_action)
        
        menu.addMenu(settings_menu)
        
        menu.addSeparator()
        
        # Select All action
        select_all_action = QAction("Select All", self)
        select_all_action.triggered.connect(self.selectAll)
        menu.addAction(select_all_action)
        
        # Show menu
        menu.exec_(self.mapToGlobal(position))
    
    def copy_selection(self):
        """Copy selected text to clipboard"""
        cursor = self.textCursor()
        if cursor.hasSelection():
            selected_text = cursor.selectedText()
            QApplication.clipboard().setText(selected_text)
    
    def copy_all(self):
        """Copy all text to clipboard"""
        QApplication.clipboard().setText(self.toPlainText())
    
    def show_search_dialog(self):
        """Show search dialog"""
        text, ok = QInputDialog.getText(
            self, "Search Logs", "Enter search term:"
        )
        if ok and text:
            self.search_text = text
            self.find_all_occurrences()
            self.find_next()
    
    def find_all_occurrences(self):
        """Find all occurrences of search text"""
        self.search_results = []
        document = self.document()
        cursor = QTextCursor(document)
        
        while not cursor.isNull() and not cursor.atEnd():
            cursor = document.find(self.search_text, cursor)
            if not cursor.isNull():
                self.search_results.append(cursor.position())
        
        self.current_search_index = -1
    
    def find_next(self):
        """Find next occurrence of search text"""
        if not self.search_results:
            return
        
        self.current_search_index = (self.current_search_index + 1) % len(self.search_results)
        position = self.search_results[self.current_search_index]
        
        cursor = self.textCursor()
        cursor.setPosition(position)
        cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, len(self.search_text))
        cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, len(self.search_text))
        
        self.setTextCursor(cursor)
        self.centerCursor()
        
        # Highlight
        extra_selections = []
        selection = QTextEdit.ExtraSelection()
        selection.cursor = cursor
        selection.format.setBackground(QColor("#2d5a7a"))
        extra_selections.append(selection)
        
        self.setExtraSelections(extra_selections)
    
    def toggle_timestamps(self):
        """Toggle timestamp display"""
        self.show_timestamps = not self.show_timestamps
        # Note: This would require re-rendering all logs
    
    def toggle_colors(self):
        """Toggle colored logs"""
        self.colored_logs = not self.colored_logs
        self.highlighter.setDocument(None if not self.colored_logs else self.document())
    
    def toggle_word_wrap(self):
        """Toggle word wrap"""
        self.word_wrap = not self.word_wrap
        self.setLineWrapMode(QTextEdit.WidgetWidth if self.word_wrap else QTextEdit.NoWrap)
    
    def toggle_auto_scroll(self):
        """Toggle auto-scroll"""
        self.auto_scroll = not self.auto_scroll
        if self.auto_scroll:
            self.scroll_to_bottom()
    
    def scroll_to_bottom(self):
        """Scroll to bottom of log"""
        scrollbar = self.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        self.auto_scroll = True
    
    def export_logs(self, format_type: str = "txt"):
        """Export logs to file"""
        file_filter = ""
        if format_type == "txt":
            file_filter = "Text Files (*.txt);;All Files (*)"
        elif format_type == "html":
            file_filter = "HTML Files (*.html);;All Files (*)"
        elif format_type == "csv":
            file_filter = "CSV Files (*.csv);;All Files (*)"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Logs", f"trafficbot_logs.{format_type}", file_filter
        )
        
        if file_path:
            try:
                if format_type == "txt":
                    content = self.toPlainText()
                elif format_type == "html":
                    content = self.toHtml()
                elif format_type == "csv":
                    content = self._convert_to_csv()
                else:
                    content = self.toPlainText()
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.append_log(f"Logs exported to: {file_path}", "SUCCESS")
                
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export logs: {e}")
    
    def _convert_to_csv(self) -> str:
        """Convert log content to CSV format"""
        lines = self.toPlainText().split('\n')
        csv_lines = ["Timestamp,Level,Message"]
        
        for line in lines:
            if line.strip():
                # Simple parsing - adjust based on your log format
                parts = line.split(' - ', 2)
                if len(parts) >= 3:
                    timestamp, level, message = parts[0], parts[1], parts[2]
                    # Escape quotes and commas in message
                    message_escaped = message.replace('"', '""')
                    if ',' in message_escaped or '"' in message_escaped:
                        message_escaped = f'"{message_escaped}"'
                    csv_lines.append(f'{timestamp},{level},{message_escaped}')
        
        return '\n'.join(csv_lines)
    
    def append_log(self, message: str, level: str = "INFO"):
        """Append log message with formatting"""
        try:
            # Create timestamp
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            # Format message based on settings
            if self.show_timestamps:
                formatted_message = f"[{timestamp}] [{level}] {message}"
            else:
                formatted_message = f"[{level}] {message}"
            
            # Escape HTML if not using colors
            if not self.colored_logs:
                formatted_message = html.escape(formatted_message)
            
            # Append to widget
            self.append(formatted_message)
            
            # Limit number of lines
            document = self.document()
            if document.lineCount() > self.max_lines:
                cursor = QTextCursor(document)
                cursor.movePosition(QTextCursor.Start)
                cursor.movePosition(
                    QTextCursor.Down, 
                    QTextCursor.KeepAnchor, 
                    document.lineCount() - self.max_lines
                )
                cursor.removeSelectedText()
            
            # Auto-scroll if enabled
            if self.auto_scroll:
                self.scroll_to_bottom()
            
        except Exception as e:
            print(f"Error appending log: {e}")


class Logger:
    """Main logger class integrating with TrafficBot"""
    
    def __init__(self):
        self.emitter = LogEmitter()
        self.widget = None
        self.log_file = None
        self.console_handler = None
        
        # Log levels
        self.levels = {
            "DEBUG": 10,
            "INFO": 20,
            "WARNING": 30,
            "ERROR": 40,
            "SUCCESS": 25  # Custom level between INFO and WARNING
        }
        
        # Current filter
        self.filter_level = "INFO"
        
        # Setup file logging
        self._setup_file_logging()
    
    def _setup_file_logging(self):
        """Setup file logging"""
        try:
            log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
            os.makedirs(log_dir, exist_ok=True)
            
            log_file = os.path.join(log_dir, 'trafficbot_ui.log')
            self.log_file = open(log_file, 'a', encoding='utf-8')
        except Exception as e:
            print(f"Failed to setup file logging: {e}")
    
    def set_widget(self, widget: LogWidget):
        """Set log widget and connect signals"""
        self.widget = widget
        
        # Connect signals
        self.emitter.log_debug.connect(
            lambda msg: self.widget.append_log(msg, "DEBUG")
        )
        self.emitter.log_info.connect(
            lambda msg: self.widget.append_log(msg, "INFO")
        )
        self.emitter.log_warning.connect(
            lambda msg: self.widget.append_log(msg, "WARNING")
        )
        self.emitter.log_error.connect(
            lambda msg: self.widget.append_log(msg, "ERROR")
        )
        self.emitter.log_success.connect(
            lambda msg: self.widget.append_log(msg, "SUCCESS")
        )
        self.emitter.log_custom.connect(
            lambda msg, level: self.widget.append_log(msg, level)
        )
        self.emitter.clear_signal.connect(self.widget.clear)
        self.emitter.filter_changed.connect(self.set_filter_level)
    
    def set_filter_level(self, level: str):
        """Set log filter level"""
        self.filter_level = level.upper()
    
    def log(self, message: str, level: str = "INFO", source: str = None):
        """Log message with specified level"""
        level = level.upper()
        
        # Apply filter
        if self._should_log(level):
            # Format message
            if source:
                formatted_message = f"[{source}] {message}"
            else:
                formatted_message = message
            
            # Emit to GUI
            if self.emitter:
                self.emitter.emit(formatted_message, level)
            
            # Write to file
            if self.log_file:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.log_file.write(f"{timestamp} - {level} - {formatted_message}\n")
                self.log_file.flush()
            
            # Print to console for debugging
            if level in ["ERROR", "WARNING"]:
                print(f"{level}: {formatted_message}")
    
    def _should_log(self, level: str) -> bool:
        """Check if message should be logged based on filter"""
        if self.filter_level == "ALL":
            return True
        
        level_value = self.levels.get(level, 20)  # Default to INFO
        filter_value = self.levels.get(self.filter_level, 20)
        
        return level_value >= filter_value
    
    def debug(self, message: str, source: str = None):
        """Log debug message"""
        self.log(message, "DEBUG", source)
    
    def info(self, message: str, source: str = None):
        """Log info message"""
        self.log(message, "INFO", source)
    
    def warning(self, message: str, source: str = None):
        """Log warning message"""
        self.log(message, "WARNING", source)
    
    def error(self, message: str, source: str = None):
        """Log error message"""
        self.log(message, "ERROR", source)
    
    def success(self, message: str, source: str = None):
        """Log success message"""
        self.log(message, "SUCCESS", source)
    
    def clear(self):
        """Clear all logs"""
        if self.emitter:
            self.emitter.clear_buffer()
        if self.widget:
            self.widget.clear()
    
    def get_stats(self) -> dict:
        """Get logging statistics"""
        if not hasattr(self.emitter, 'log_buffer'):
            return {}
        
        stats = {
            "total_logs": len(self.emitter.log_buffer),
            "debug_count": 0,
            "info_count": 0,
            "warning_count": 0,
            "error_count": 0,
            "success_count": 0,
        }
        
        for _, level, _ in self.emitter.log_buffer:
            level_lower = level.lower()
            if f"{level_lower}_count" in stats:
                stats[f"{level_lower}_count"] += 1
        
        return stats
    
    def close(self):
        """Close logger and clean up"""
        if self.log_file:
            self.log_file.close()
            self.log_file = None


# Global logger instance
logger = Logger()


def setup_logger() -> Logger:
    """Setup and return logger instance"""
    return logger


def get_log_widget() -> LogWidget:
    """Create and return log widget"""
    widget = LogWidget()
    logger.set_widget(widget)
    return widget


def log_to_gui(message: str, level: str = "INFO"):
    """Convenience function to log to GUI"""
    logger.log(message, level)


if __name__ == "__main__":
    # Test the logger
    app = QApplication(sys.argv)
    
    widget = get_log_widget()
    widget.setWindowTitle("Log Widget Test")
    widget.resize(800, 600)
    widget.show()
    
    # Test logs
    logger.info("Application started")
    logger.success("Configuration loaded successfully")
    logger.warning("Proxy connection slow")
    logger.error("Failed to connect to target")
    logger.debug("Debug information here")
    
    sys.exit(app.exec_())