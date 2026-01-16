"""
UI Components - Reusable Widgets
"""

import tkinter as tk
from tkinter import scrolledtext
from ui.styles import *

class SharpPanel(tk.Frame):
    """Panel dengan border tajam dan background"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=COLOR_BG_PANEL, relief="flat", bd=1, **kwargs)
        self.config(highlightbackground=COLOR_BORDER, highlightthickness=1)

class Bevel3DButton(tk.Button):
    """Tombol dengan efek 3D bevel"""
    def __init__(self, parent, text, command, color=COLOR_ACCENT_CYAN, **kwargs):
        super().__init__(
            parent,
            text=text,
            command=command,
            font=(FONT_FAMILY_PRIMARY, 10, "bold"),
            bg=color,
            fg=COLOR_TEXT_PRIMARY,
            activebackground=self._darken_color(color),
            relief="raised",
            bd=2,
            cursor="hand2",
            **kwargs
        )
        self.bind("<Enter>", lambda e: self.config(relief="raised", bd=3))
        self.bind("<Leave>", lambda e: self.config(relief="raised", bd=2))
    
    def _darken_color(self, color):
        """Darken color untuk hover effect"""
        color_map = {
            COLOR_ACCENT_CYAN: "#1a7a8a",
            COLOR_SUCCESS: "#00a076",
            COLOR_ACCENT_RED: "#c0392b",
            COLOR_BG_MAIN: "#1a1a1a"
        }
        return color_map.get(color, color)

class StatCard(tk.Frame):
    """Card untuk menampilkan statistik"""
    def __init__(self, parent, label, value, color):
        super().__init__(parent, bg=COLOR_INPUT_BG, relief="flat")
        self.config(highlightbackground=color, highlightthickness=2)
        
        self.lbl_value = tk.Label(
            self, text=value,
            font=(FONT_FAMILY_PRIMARY, 24, "bold"),
            bg=COLOR_INPUT_BG, fg=color
        )
        self.lbl_value.pack(pady=(10, 0))
        
        tk.Label(
            self, text=label,
            font=(FONT_FAMILY_PRIMARY, 9),
            bg=COLOR_INPUT_BG, fg=COLOR_TEXT_SECONDARY
        ).pack(pady=(0, 10))
    
    def update_value(self, value):
        """Update nilai statistik"""
        self.lbl_value.config(text=str(value))

class WorkerCard(tk.Frame):
    """Worker status card - COMPACT VERSION (8 per row)"""
    
    def __init__(self, parent, worker_id: int, on_click_callback=None):
        super().__init__(parent, bg=COLOR_INPUT_BG, relief="flat", bd=1)
        self.config(highlightbackground=COLOR_BORDER, highlightthickness=1)
        
        self.worker_id = worker_id
        self.on_click_callback = on_click_callback
        self.status_color = COLOR_TEXT_SECONDARY
        
        # Main container - COMPACT PADDING
        container = tk.Frame(self, bg=COLOR_INPUT_BG)
        container.pack(fill="both", expand=True, padx=5, pady=4)
        
        # ========== TOP ROW - Worker ID + Eye Button ==========
        top_row = tk.Frame(container, bg=COLOR_INPUT_BG)
        top_row.pack(fill="x")
        
        # Worker number (left side)
        self.lbl_number = tk.Label(
            top_row,
            text=f"#{worker_id}",
            font=(FONT_FAMILY_PRIMARY, 12, "bold"),
            bg=COLOR_INPUT_BG,
            fg=COLOR_TEXT_PRIMARY,
            anchor="w"
        )
        self.lbl_number.pack(side="left")
        
        # Eye button (right side) - NO BACKGROUND!
        self.btn_eye = tk.Label(
            top_row,
            text="👁️",
            font=(FONT_FAMILY_PRIMARY, 12),
            bg=COLOR_INPUT_BG,
            fg=COLOR_TEXT_PRIMARY,
            cursor="hand2"
        )
        self.btn_eye.pack(side="right")
        self.btn_eye.bind("<Button-1>", lambda e: self._on_click())
        
        # ========== MIDDLE ROW - Status ==========
        middle_row = tk.Frame(container, bg=COLOR_INPUT_BG)
        middle_row.pack(fill="x", pady=(2, 0))
        
        # Status indicator (small circle)
        self.status_canvas = tk.Canvas(middle_row, width=8, height=8, 
                                      bg=COLOR_INPUT_BG, highlightthickness=0)
        self.status_canvas.pack(side="left", padx=(0, 4))
        self.status_indicator = self.status_canvas.create_oval(1, 1, 7, 7, 
                                                               fill=COLOR_TEXT_SECONDARY,
                                                               outline="")
        
        # Status text
        self.lbl_status = tk.Label(
            middle_row,
            text="IDLE",
            font=(FONT_FAMILY_PRIMARY, 8, "bold"),
            bg=COLOR_INPUT_BG,
            fg=COLOR_TEXT_SECONDARY,
            anchor="w"
        )
        self.lbl_status.pack(side="left", fill="x", expand=True)
        
        # ========== BOTTOM ROW - Info Text ==========
        self.lbl_info = tk.Label(
            container,
            text="Waiting...",
            font=(FONT_FAMILY_PRIMARY, 7),
            bg=COLOR_INPUT_BG,
            fg=COLOR_TEXT_SECONDARY,
            anchor="w",
            wraplength=120,
            justify="left",
            height=2
        )
        self.lbl_info.pack(fill="x", pady=(2, 0))
        
        # Hover effect
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        for widget in [container, top_row, middle_row]:
            widget.bind("<Enter>", self._on_enter)
            widget.bind("<Leave>", self._on_leave)
    
    def _on_enter(self, event):
        """Hover effect"""
        self.config(highlightbackground=self.status_color, highlightthickness=2)
    
    def _on_leave(self, event):
        """Leave hover"""
        self.config(highlightbackground=COLOR_BORDER, highlightthickness=1)
    
    def update_status(self, status: str, color: str, info: str = ""):
        """Update status worker card"""
        # Update status text & color
        self.lbl_status.config(text=status.upper(), fg=color)
        
        # Update status indicator circle
        self.status_canvas.itemconfig(self.status_indicator, fill=color)
        self.status_color = color
        
        # Update info text
        if info:
            # Truncate long text
            if len(info) > 35:
                info = info[:32] + "..."
            self.lbl_info.config(text=info, fg=COLOR_TEXT_SECONDARY)
        else:
            # Default info based on status
            default_info = {
                "IDLE": "Waiting...",
                "INITIALIZING": "Starting...",
                "RUNNING": "Processing...",
                "SUCCESS": "Completed!",
                "FAILED": "Failed",
                "ERROR": "Error",
                "STOPPED": "Stopped"
            }
            self.lbl_info.config(text=default_info.get(status.upper(), ""), fg=COLOR_TEXT_SECONDARY)
    
    def _on_click(self):
        """Handle eye button click"""
        if self.on_click_callback:
            self.on_click_callback(self.worker_id)

class ConsoleLog(tk.Frame):
    """Console log dengan scrollbar"""
    def __init__(self, parent):
        super().__init__(parent, bg=COLOR_BG_PANEL)
        
        # Text widget dengan scrollbar
        self.text = scrolledtext.ScrolledText(
            self,
            font=(FONT_FAMILY_MONO, 9),
            bg=COLOR_INPUT_BG,
            fg=COLOR_TEXT_PRIMARY,
            relief="flat",
            wrap="word",
            state="disabled"
        )
        self.text.pack(fill="both", expand=True)
        
        # Tag colors untuk different log levels
        self.text.tag_config("INFO", foreground=COLOR_ACCENT_CYAN)
        self.text.tag_config("SUCCESS", foreground=COLOR_SUCCESS)
        self.text.tag_config("WARNING", foreground=COLOR_WARNING)
        self.text.tag_config("ERROR", foreground=COLOR_ACCENT_RED)
        self.text.tag_config("SYSTEM", foreground=COLOR_TEXT_SECONDARY)
    
    def log(self, message: str):
        """Add log message"""
        self.text.config(state="normal")
        
        # Detect log level from message
        tag = "INFO"
        if "[SUCCESS]" in message or "✓" in message:
            tag = "SUCCESS"
        elif "[WARNING]" in message or "⚠" in message:
            tag = "WARNING"
        elif "[ERROR]" in message or "✗" in message:
            tag = "ERROR"
        elif "[SYSTEM]" in message:
            tag = "SYSTEM"
        elif "[START]" in message or "[STOP]" in message:
            tag = "INFO"
        
        # Add timestamp jika belum ada
        import datetime
        if not message.startswith("["):
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            message = f"[{timestamp}] {message}"
        
        # Insert message dengan tag color
        self.text.insert("end", message + "\n", tag)
        
        # Auto-scroll ke bawah
        self.text.see("end")
        
        # Limit log lines (max 1000 lines)
        lines = int(self.text.index('end-1c').split('.')[0])
        if lines > 1000:
            self.text.delete(1.0, 2.0)
        
        self.text.config(state="disabled")
    
    def clear(self):
        """Clear all logs"""
        self.text.config(state="normal")
        self.text.delete(1.0, "end")
        self.text.config(state="disabled")
