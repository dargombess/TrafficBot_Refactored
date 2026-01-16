"""
ui/app.py - PROFESSIONAL EDITION (COMPLETE OPTIMIZED)
Dashboard + Settings dengan Conditional Display & Browser Hide Control
Window: 1200x750 (ramping) | Worker Monitor: 6 cards per row | Event Logs: bigger
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import threading

from ui.styles import *
from ui.components import *
from bot_config import config
from orchestrator import orchestrator
from core.resource_manager import resource_manager

class TrafficBotGUI(tk.Tk):
    """Main GUI Application - Professional Edition"""
    
    def __init__(self):
        super().__init__()
        
        self.title("Traffic Bot - Professional Edition")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.configure(bg=COLOR_BG_MAIN)
        
        self.grid_columnconfigure(0, weight=0, minsize=SIDEBAR_WIDTH)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.is_running = False
        self.worker_cards = {}
        self.stat_cards = {}
        self.current_page = "dashboard"
        self.pages = {}
        
        # Settings state
        self.current_fp_mode = "Cortex"
        self.current_traffic_mode = "Hybrid"
        self.fp_dynamic_widgets = {}
        self.traffic_dynamic_widgets = {}
        
        self._create_sidebar()
        self._create_pages_container()
        self._create_dashboard_page()
        self._create_settings_page()
        self._show_page("dashboard")
        
        orchestrator.set_status_callback(self._on_status_change)
        orchestrator.set_worker_callback(self._on_worker_update)
        self._start_stats_update()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _bind_mousewheel(self, widget, canvas):
        """Bind mouse wheel to canvas for scrolling"""
        def on_mousewheel(event):
            # Windows & Mac
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def on_mousewheel_linux(event):
            # Linux
            if event.num == 5:
                canvas.yview_scroll(1, "units")
            elif event.num == 4:
                canvas.yview_scroll(-1, "units")
        
        def on_enter(event):
            # Windows/Mac
            widget.bind_all("<MouseWheel>", on_mousewheel)
            # Linux
            widget.bind_all("<Button-4>", on_mousewheel_linux)
            widget.bind_all("<Button-5>", on_mousewheel_linux)
        
        def on_leave(event):
            widget.unbind_all("<MouseWheel>")
            widget.unbind_all("<Button-4>")
            widget.unbind_all("<Button-5>")
        
        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)
    
    def _create_sidebar(self):
        sidebar = SharpPanel(self, width=SIDEBAR_WIDTH)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)
        
        tk.Label(sidebar, text="TRAFFIC BOT", font=(FONT_FAMILY_PRIMARY, 16, "bold"),
                bg=COLOR_BG_PANEL, fg=COLOR_ACCENT_CYAN).pack(pady=(20, 3))
        tk.Label(sidebar, text="Professional Edition", font=(FONT_FAMILY_PRIMARY, 9),
                bg=COLOR_BG_PANEL, fg=COLOR_TEXT_SECONDARY).pack(pady=(0, 20))
        
        self.btn_dashboard = Bevel3DButton(sidebar, text="📊 DASHBOARD",
            command=lambda: self._show_page("dashboard"), color=COLOR_ACCENT_CYAN, height=1)
        self.btn_dashboard.pack(fill="x", padx=15, pady=3)
        
        self.btn_settings = Bevel3DButton(sidebar, text="⚙️ SETTINGS",
            command=lambda: self._show_page("settings"), color=COLOR_BG_MAIN, height=1)
        self.btn_settings.pack(fill="x", padx=15, pady=3)
        
        tk.Frame(sidebar, bg=COLOR_BG_PANEL, height=15).pack()
        
        tk.Label(sidebar, text="QUICK START", font=(FONT_FAMILY_PRIMARY, 9, "bold"),
                bg=COLOR_BG_PANEL, fg=COLOR_TEXT_SECONDARY).pack(pady=(5, 5))
        
        frame = tk.Frame(sidebar, bg=COLOR_BG_PANEL)
        frame.pack(fill="x", padx=15, pady=3)
        tk.Label(frame, text="Workers:", font=(FONT_FAMILY_PRIMARY, 10),
                bg=COLOR_BG_PANEL, fg=COLOR_TEXT_SECONDARY).pack(side="left")
        self.entry_workers = tk.Entry(frame, font=(FONT_FAMILY_PRIMARY, 10),
            bg=COLOR_INPUT_BG, fg=COLOR_TEXT_PRIMARY, relief="flat", width=6)
        self.entry_workers.insert(0, "50")
        self.entry_workers.pack(side="right")
        
        self.btn_start = Bevel3DButton(sidebar, text="🚀 START ENGINE",
            command=self._toggle_bot, color=COLOR_SUCCESS, height=1)
        self.btn_start.pack(side="bottom", fill="x", padx=15, pady=15)
    
    def _create_pages_container(self):
        self.pages_container = tk.Frame(self, bg=COLOR_BG_MAIN)
        self.pages_container.grid(row=0, column=1, sticky="nsew")
    
    def _create_dashboard_page(self):
        page = tk.Frame(self.pages_container, bg=COLOR_BG_MAIN)
        
        # ========== STATS CARDS ==========
        stats_frame = SharpPanel(page)
        stats_frame.pack(fill="x", padx=15, pady=(15, 10))
        for i in range(4):
            stats_frame.grid_columnconfigure(i, weight=1)
        
        stats = [("SUCCESS", "0", COLOR_SUCCESS), ("FAILED", "0", COLOR_ACCENT_RED),
                ("ACTIVE", "0", COLOR_ACCENT_CYAN), ("BLOCKED", "0", COLOR_WARNING)]
        for i, (label, value, color) in enumerate(stats):
            card = StatCard(stats_frame, label, value, color)
            card.grid(row=0, column=i, padx=8, pady=10, sticky="ew")
            self.stat_cards[label.lower()] = card
        
        # ========== WORKER MONITOR (6 CARDS PER ROW - FIT SCREEN) ==========
        monitor_panel = SharpPanel(page, height=260)  # Optimized height
        monitor_panel.pack(fill="both", expand=True, padx=15, pady=(0, 10))
        monitor_panel.pack_propagate(False)
        
        tk.Label(monitor_panel, text="WORKER MONITOR", font=(FONT_FAMILY_PRIMARY, 12, "bold"),
                bg=COLOR_BG_PANEL, fg=COLOR_TEXT_PRIMARY).pack(pady=(10, 8))
        
        canvas = tk.Canvas(monitor_panel, bg=COLOR_BG_PANEL, highlightthickness=0)
        scrollbar = tk.Scrollbar(monitor_panel, orient="vertical", command=canvas.yview)
        self.worker_grid_frame = tk.Frame(canvas, bg=COLOR_BG_PANEL)
        canvas.create_window((0, 0), window=self.worker_grid_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True, padx=12, pady=(0, 12))
        scrollbar.pack(side="right", fill="y")
        
        # ========== 6 COLUMNS GRID (FIT DALAM LAYAR) ==========
        for i in range(6):  # 6 kolom (optimized!)
            self.worker_grid_frame.grid_columnconfigure(i, weight=1, minsize=150)
        
        # Create 50 worker cards
        for i in range(50):
            card = WorkerCard(self.worker_grid_frame, i + 1, self._on_worker_click)
            card.grid(row=i//6, column=i%6, padx=4, pady=4, sticky="ew")  # 6 kolom
            self.worker_cards[i + 1] = card
        
        self.worker_grid_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))
        
        # Bind mouse wheel untuk worker monitor
        self._bind_mousewheel(canvas, canvas)
        
        # ========== EVENT LOGS (PROPORTIONAL HEIGHT FOR ANALYSIS) ==========
        log_panel = SharpPanel(page, height=250)  # Optimized for 750px window
        log_panel.pack(fill="both", padx=15, pady=(0, 15))
        log_panel.pack_propagate(False)
        
        tk.Label(log_panel, text="EVENT LOGS", font=(FONT_FAMILY_PRIMARY, 12, "bold"),
                bg=COLOR_BG_PANEL, fg=COLOR_TEXT_PRIMARY).pack(pady=(10, 8))
        self.log_console = ConsoleLog(log_panel)
        self.log_console.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self.log_console.log("[SYSTEM] Traffic Bot Ready")
        
        self.pages["dashboard"] = page
    
    def _create_settings_page(self):
        page = tk.Frame(self.pages_container, bg=COLOR_BG_MAIN)
        
        # Header
        header = SharpPanel(page, height=60)
        header.pack(fill="x", padx=15, pady=(15, 10))
        header.pack_propagate(False)
        tk.Label(header, text="⚙️ CONFIGURATION SETTINGS", font=(FONT_FAMILY_PRIMARY, 16, "bold"),
                bg=COLOR_BG_PANEL, fg=COLOR_ACCENT_CYAN).pack(expand=True)
        
        # Scrollable area
        canvas = tk.Canvas(page, bg=COLOR_BG_MAIN, highlightthickness=0)
        scrollbar = tk.Scrollbar(page, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=COLOR_BG_MAIN)
        
        # Create window in canvas
        canvas_window = canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        def on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(canvas_window, width=event.width)
        
        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        canvas.bind('<Configure>', on_configure)
        scroll_frame.bind('<Configure>', on_frame_configure)
        
        canvas.pack(side="left", fill="both", expand=True, padx=(15, 0))
        scrollbar.pack(side="right", fill="y", padx=(0, 15))
        
        # Bind mouse wheel untuk settings scroll
        self._bind_mousewheel(canvas, canvas)
        
        # Build sections
        self._build_files_section(scroll_frame)
        self._build_fingerprint_section(scroll_frame)
        self._build_proxy_section(scroll_frame)
        self._build_traffic_section(scroll_frame)
        self._build_interaction_section(scroll_frame)
        self._build_browser_section(scroll_frame)
        self._build_operational_section(scroll_frame)
        self._build_performance_section(scroll_frame)
        self._build_ai_section(scroll_frame)
        
        self.pages["settings"] = page
    
    def _build_files_section(self, parent):
        section = SharpPanel(parent)
        section.pack(fill="x", pady=(0, 10))
        
        tk.Label(section, text="📁 FILE CONFIGURATION", font=(FONT_FAMILY_PRIMARY, 11, "bold"),
                bg=COLOR_BG_PANEL, fg=COLOR_SUCCESS, anchor="w").pack(fill="x", padx=12, pady=(10, 8))
        
        content = tk.Frame(section, bg=COLOR_BG_PANEL)
        content.pack(fill="x", padx=12, pady=(0, 10))
        
        self._add_file_row(content, "Article File", "FILE_ARTICLES")
        self._add_file_row(content, "Proxy File", "FILE_PROXIES")
        self._add_file_row(content, "Referrer File", "FILE_REFERRERS")
    
    def _build_fingerprint_section(self, parent):
        section = SharpPanel(parent)
        section.pack(fill="x", pady=(0, 10))
        
        tk.Label(section, text="🔐 FINGERPRINT & IDENTITY", font=(FONT_FAMILY_PRIMARY, 11, "bold"),
                bg=COLOR_BG_PANEL, fg=COLOR_SUCCESS, anchor="w").pack(fill="x", padx=12, pady=(10, 8))
        
        content = tk.Frame(section, bg=COLOR_BG_PANEL)
        content.pack(fill="x", padx=12, pady=(0, 10))
        
        # Fingerprint method radio
        row = tk.Frame(content, bg=COLOR_BG_PANEL)
        row.pack(fill="x", pady=3)
        tk.Label(row, text="Fingerprint Method", font=(FONT_FAMILY_PRIMARY, 10), bg=COLOR_BG_PANEL,
                fg=COLOR_TEXT_SECONDARY, width=22, anchor="w").pack(side="left")
        
        self.fp_mode_var = tk.StringVar(value=getattr(config, "FINGERPRINT_MODE", "Cortex"))
        for opt in ["Cortex", "Pro", "JSON"]:
            tk.Radiobutton(row, text=opt, variable=self.fp_mode_var, value=opt,
                          command=self._on_fingerprint_change,
                          font=(FONT_FAMILY_PRIMARY, 9), bg=COLOR_BG_PANEL,
                          fg=COLOR_TEXT_PRIMARY, selectcolor=COLOR_INPUT_BG,
                          activebackground=COLOR_BG_PANEL).pack(side="left", padx=8)
        
        # Dynamic area for conditional fields
        self.fp_dynamic_area = tk.Frame(content, bg=COLOR_BG_PANEL)
        self.fp_dynamic_area.pack(fill="x")
        self._refresh_fingerprint_ui()
        
        # Other fingerprint settings
        self._add_switch_row(content, "WebRTC Protection", "WEBRTC_ENABLED")
        self._add_switch_row(content, "Timezone Synchronization", "TIMEZONE_SYNC")
        self._add_radio_row(content, "User Agent Strategy", "USER_AGENT_MODE", 
                           ["Mixed", "Mobile Only", "Desktop Only"])
    
    def _build_proxy_section(self, parent):
        section = SharpPanel(parent)
        section.pack(fill="x", pady=(0, 10))
        
        tk.Label(section, text="📦 PROXY CONFIGURATION", font=(FONT_FAMILY_PRIMARY, 11, "bold"),
                bg=COLOR_BG_PANEL, fg=COLOR_SUCCESS, anchor="w").pack(fill="x", padx=12, pady=(10, 8))
        
        content = tk.Frame(section, bg=COLOR_BG_PANEL)
        content.pack(fill="x", padx=12, pady=(0, 10))
        
        self._add_radio_row(content, "Proxy Type", "PROXY_TYPE", 
                           ["auto", "http", "https", "socks4", "socks5"])
        self._add_number_row(content, "Max Latency (ms)", "MAX_PROXY_LATENCY")
        self._add_switch_row(content, "Check Duplicate IP", "CHECK_DUPLICATE_IP")
    
    def _build_traffic_section(self, parent):
        section = SharpPanel(parent)
        section.pack(fill="x", pady=(0, 10))
        
        tk.Label(section, text="🌐 TRAFFIC SIMULATION", font=(FONT_FAMILY_PRIMARY, 11, "bold"),
                bg=COLOR_BG_PANEL, fg=COLOR_SUCCESS, anchor="w").pack(fill="x", padx=12, pady=(10, 8))
        
        content = tk.Frame(section, bg=COLOR_BG_PANEL)
        content.pack(fill="x", padx=12, pady=(0, 10))
        
        # Traffic mode radio
        row = tk.Frame(content, bg=COLOR_BG_PANEL)
        row.pack(fill="x", pady=3)
        tk.Label(row, text="Traffic Mode", font=(FONT_FAMILY_PRIMARY, 10), bg=COLOR_BG_PANEL,
                fg=COLOR_TEXT_SECONDARY, width=22, anchor="w").pack(side="left")
        
        self.traffic_mode_var = tk.StringVar(value=getattr(config, "TRAFFIC_MODE", "Hybrid"))
        for opt in ["Hybrid", "External"]:
            tk.Radiobutton(row, text=opt, variable=self.traffic_mode_var, value=opt,
                          command=self._on_traffic_change,
                          font=(FONT_FAMILY_PRIMARY, 9), bg=COLOR_BG_PANEL,
                          fg=COLOR_TEXT_PRIMARY, selectcolor=COLOR_INPUT_BG,
                          activebackground=COLOR_BG_PANEL).pack(side="left", padx=8)
        
        # Dynamic area
        self.traffic_dynamic_area = tk.Frame(content, bg=COLOR_BG_PANEL)
        self.traffic_dynamic_area.pack(fill="x")
        self._refresh_traffic_ui()
    
    def _build_interaction_section(self, parent):
        section = SharpPanel(parent)
        section.pack(fill="x", pady=(0, 10))
        
        tk.Label(section, text="🖱️ INTERACTION & BEHAVIOR", font=(FONT_FAMILY_PRIMARY, 11, "bold"),
                bg=COLOR_BG_PANEL, fg=COLOR_SUCCESS, anchor="w").pack(fill="x", padx=12, pady=(10, 8))
        
        content = tk.Frame(section, bg=COLOR_BG_PANEL)
        content.pack(fill="x", padx=12, pady=(0, 10))
        
        self._add_number_row(content, "Target CTR (%)", "TARGET_CTR")
        self._add_range_row(content, "Scroll Range", "SCROLL_MIN", "SCROLL_MAX")
        self._add_range_row(content, "Delay Range (seconds)", "DELAY_MIN", "DELAY_MAX")
        self._add_radio_row(content, "Mouse Movement", "MOUSE_STYLE", 
                           ["Human Curves", "Direct Jump"])
        self._add_radio_row(content, "Ad-Guard Strategy", "ADGUARD_MODE", 
                           ["Dynamic", "Always OFF", "Always ON"])
    
    def _build_browser_section(self, parent):
        section = SharpPanel(parent)
        section.pack(fill="x", pady=(0, 10))
        
        tk.Label(section, text="🖥️ BROWSER CONFIGURATION", font=(FONT_FAMILY_PRIMARY, 11, "bold"),
                bg=COLOR_BG_PANEL, fg=COLOR_SUCCESS, anchor="w").pack(fill="x", padx=12, pady=(10, 8))
        
        content = tk.Frame(section, bg=COLOR_BG_PANEL)
        content.pack(fill="x", padx=12, pady=(0, 10))
        
        self._add_switch_row(content, "Headless Mode", "HEADLESS")
        self._add_switch_row(content, "Auto Headless", "AUTO_HEADLESS")
        self._add_radio_row(content, "Window Visibility", "BROWSER_VISIBILITY", 
                           ["stealth", "ghost", "normal"])
        self._add_switch_row(content, "Hide from Taskbar", "HIDE_FROM_TASKBAR")
    
    def _build_operational_section(self, parent):
        section = SharpPanel(parent)
        section.pack(fill="x", pady=(0, 10))
        
        tk.Label(section, text="⚙️ OPERATIONAL SETTINGS", font=(FONT_FAMILY_PRIMARY, 11, "bold"),
                bg=COLOR_BG_PANEL, fg=COLOR_SUCCESS, anchor="w").pack(fill="x", padx=12, pady=(10, 8))
        
        content = tk.Frame(section, bg=COLOR_BG_PANEL)
        content.pack(fill="x", padx=12, pady=(0, 10))
        
        self._add_number_row(content, "Total Tasks", "TASK_COUNT")
        self._add_number_row(content, "Max Retries", "MAX_RETRIES")
        self._add_number_row(content, "Retry Delay (s)", "RETRY_DELAY")
        self._add_radio_row(content, "Manual Mode", "MANUAL_CLICK", 
                           ["Auto", "Manual"])
    
    def _build_performance_section(self, parent):
        section = SharpPanel(parent)
        section.pack(fill="x", pady=(0, 10))
        
        tk.Label(section, text="⚡ HIGH-PERFORMANCE SETTINGS", font=(FONT_FAMILY_PRIMARY, 11, "bold"),
                bg=COLOR_BG_PANEL, fg=COLOR_SUCCESS, anchor="w").pack(fill="x", padx=12, pady=(10, 8))
        
        content = tk.Frame(section, bg=COLOR_BG_PANEL)
        content.pack(fill="x", padx=12, pady=(0, 10))
        
        self._add_switch_row(content, "Massive Parallel Processing", "PARALLEL_PROCESSING")
        self._add_switch_row(content, "In-Memory Caching (50GB)", "IN_MEMORY_CACHING")
        self._add_switch_row(content, "CPU Core Affinity", "CPU_AFFINITY")
        self._add_switch_row(content, "Intelligent Batch Processing", "BATCH_PROCESSING")
    
    def _build_ai_section(self, parent):
        section = SharpPanel(parent)
        section.pack(fill="x", pady=(0, 10))
        
        tk.Label(section, text="🤖 AI/ML INTELLIGENCE ENGINE", font=(FONT_FAMILY_PRIMARY, 11, "bold"),
                bg=COLOR_BG_PANEL, fg=COLOR_SUCCESS, anchor="w").pack(fill="x", padx=12, pady=(10, 8))
        
        content = tk.Frame(section, bg=COLOR_BG_PANEL)
        content.pack(fill="x", padx=12, pady=(0, 10))
        
        self._add_switch_row(content, "Behavioral Learning AI", "AI_BEHAVIORAL_LEARNING")
        self._add_switch_row(content, "Pattern Detection AI", "AI_PATTERN_DETECTION")
        self._add_switch_row(content, "Predictive CTR Optimization", "AI_CTR_OPTIMIZATION")
        self._add_switch_row(content, "Anomaly Detection AI", "AI_ANOMALY_DETECTION")
        self._add_switch_row(content, "Proxy Intelligence AI", "AI_PROXY_INTELLIGENCE")
    
    def _add_file_row(self, parent, label, key):
        row = tk.Frame(parent, bg=COLOR_BG_PANEL)
        row.pack(fill="x", pady=3)
        tk.Label(row, text=label, font=(FONT_FAMILY_PRIMARY, 10), bg=COLOR_BG_PANEL,
                fg=COLOR_TEXT_SECONDARY, width=22, anchor="w").pack(side="left")
        entry = tk.Entry(row, font=(FONT_FAMILY_PRIMARY, 9), bg=COLOR_INPUT_BG,
                        fg=COLOR_TEXT_PRIMARY, relief="flat")
        entry.pack(side="left", fill="x", expand=True, padx=5)
        entry.insert(0, getattr(config, key, ""))
        
        def browse():
            path = filedialog.askopenfilename(title=f"Select {label}",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
            if path:
                entry.delete(0, tk.END)
                entry.insert(0, path)
                setattr(config, key, path)
        
        tk.Button(row, text="📁", command=browse, font=(FONT_FAMILY_PRIMARY, 10),
                 bg=COLOR_INPUT_BG, fg=COLOR_TEXT_PRIMARY, relief="flat",
                 padx=8, cursor="hand2").pack(side="right")
    
    def _add_radio_row(self, parent, label, key, options):
        row = tk.Frame(parent, bg=COLOR_BG_PANEL)
        row.pack(fill="x", pady=3)
        tk.Label(row, text=label, font=(FONT_FAMILY_PRIMARY, 10), bg=COLOR_BG_PANEL,
                fg=COLOR_TEXT_SECONDARY, width=22, anchor="w").pack(side="left")
        var = tk.StringVar(value=getattr(config, key, options[0]))
        
        def on_change():
            setattr(config, key, var.get())
        
        for opt in options:
            tk.Radiobutton(row, text=opt, variable=var, value=opt, command=on_change,
                          font=(FONT_FAMILY_PRIMARY, 9), bg=COLOR_BG_PANEL,
                          fg=COLOR_TEXT_PRIMARY, selectcolor=COLOR_INPUT_BG,
                          activebackground=COLOR_BG_PANEL).pack(side="left", padx=8)
    
    def _add_switch_row(self, parent, label, key):
        row = tk.Frame(parent, bg=COLOR_BG_PANEL)
        row.pack(fill="x", pady=3)
        tk.Label(row, text=label, font=(FONT_FAMILY_PRIMARY, 10), bg=COLOR_BG_PANEL,
                fg=COLOR_TEXT_SECONDARY, anchor="w").pack(side="left", fill="x", expand=True)
        var = tk.BooleanVar(value=getattr(config, key, False))
        
        def on_toggle():
            setattr(config, key, var.get())
        
        tk.Checkbutton(row, variable=var, command=on_toggle, bg=COLOR_BG_PANEL,
                      activebackground=COLOR_BG_PANEL, selectcolor=COLOR_SUCCESS).pack(side="right")
    
    def _add_number_row(self, parent, label, key):
        row = tk.Frame(parent, bg=COLOR_BG_PANEL)
        row.pack(fill="x", pady=3)
        tk.Label(row, text=label, font=(FONT_FAMILY_PRIMARY, 10), bg=COLOR_BG_PANEL,
                fg=COLOR_TEXT_SECONDARY, anchor="w").pack(side="left", fill="x", expand=True)
        entry = tk.Entry(row, font=(FONT_FAMILY_PRIMARY, 10), bg=COLOR_INPUT_BG,
                        fg=COLOR_TEXT_PRIMARY, relief="flat", width=10)
        entry.insert(0, str(getattr(config, key, 0)))
        entry.pack(side="right")
        
        def on_change(event):
            try:
                val = float(entry.get()) if '.' in entry.get() else int(entry.get())
                setattr(config, key, val)
            except:
                pass
        entry.bind('<FocusOut>', on_change)
        entry.bind('<Return>', on_change)
    
    def _add_range_row(self, parent, label, key_min, key_max):
        row = tk.Frame(parent, bg=COLOR_BG_PANEL)
        row.pack(fill="x", pady=3)
        tk.Label(row, text=label, font=(FONT_FAMILY_PRIMARY, 10), bg=COLOR_BG_PANEL,
                fg=COLOR_TEXT_SECONDARY, anchor="w").pack(side="left", fill="x", expand=True)
        
        entry_max = tk.Entry(row, font=(FONT_FAMILY_PRIMARY, 10), bg=COLOR_INPUT_BG,
                            fg=COLOR_TEXT_PRIMARY, relief="flat", width=7)
        entry_max.insert(0, str(getattr(config, key_max, 0)))
        entry_max.pack(side="right")
        
        tk.Label(row, text="-", font=(FONT_FAMILY_PRIMARY, 10), bg=COLOR_BG_PANEL,
                fg=COLOR_TEXT_SECONDARY).pack(side="right", padx=3)
        
        entry_min = tk.Entry(row, font=(FONT_FAMILY_PRIMARY, 10), bg=COLOR_INPUT_BG,
                            fg=COLOR_TEXT_PRIMARY, relief="flat", width=7)
        entry_min.insert(0, str(getattr(config, key_min, 0)))
        entry_min.pack(side="right")
        
        def on_change_min(event):
            try:
                setattr(config, key_min, int(entry_min.get()))
            except:
                pass
        
        def on_change_max(event):
            try:
                setattr(config, key_max, int(entry_max.get()))
            except:
                pass
        
        entry_min.bind('<FocusOut>', on_change_min)
        entry_min.bind('<Return>', on_change_min)
        entry_max.bind('<FocusOut>', on_change_max)
        entry_max.bind('<Return>', on_change_max)
    
    def _on_fingerprint_change(self):
        mode = self.fp_mode_var.get()
        setattr(config, "FINGERPRINT_MODE", mode)
        self._refresh_fingerprint_ui()
    
    def _refresh_fingerprint_ui(self):
        for widget in self.fp_dynamic_area.winfo_children():
            widget.destroy()
        
        mode = self.fp_mode_var.get()
        
        if mode == "Cortex":
            pass
        elif mode == "Pro":
            self._add_file_row(self.fp_dynamic_area, "Pro License File", "FINGERPRINT_PRO_FILE")
        elif mode == "JSON":
            row = tk.Frame(self.fp_dynamic_area, bg=COLOR_BG_PANEL)
            row.pack(fill="x", pady=3)
            tk.Label(row, text="JSON Folder Path", font=(FONT_FAMILY_PRIMARY, 10), bg=COLOR_BG_PANEL,
                    fg=COLOR_TEXT_SECONDARY, width=22, anchor="w").pack(side="left")
            entry = tk.Entry(row, font=(FONT_FAMILY_PRIMARY, 9), bg=COLOR_INPUT_BG,
                            fg=COLOR_TEXT_PRIMARY, relief="flat")
            entry.pack(side="left", fill="x", expand=True, padx=5)
            entry.insert(0, getattr(config, "FINGERPRINT_FOLDER", ""))
            
            def browse():
                path = filedialog.askdirectory(title="Select JSON Folder")
                if path:
                    entry.delete(0, tk.END)
                    entry.insert(0, path)
                    setattr(config, "FINGERPRINT_FOLDER", path)
            
            tk.Button(row, text="📁", command=browse, font=(FONT_FAMILY_PRIMARY, 10),
                     bg=COLOR_INPUT_BG, fg=COLOR_TEXT_PRIMARY, relief="flat",
                     padx=8, cursor="hand2").pack(side="right")
    
    def _on_traffic_change(self):
        mode = self.traffic_mode_var.get()
        setattr(config, "TRAFFIC_MODE", mode)
        self._refresh_traffic_ui()
    
    def _refresh_traffic_ui(self):
        for widget in self.traffic_dynamic_area.winfo_children():
            widget.destroy()
        
        mode = self.traffic_mode_var.get()
        
        if mode == "Hybrid":
            row = tk.Frame(self.traffic_dynamic_area, bg=COLOR_BG_PANEL)
            row.pack(fill="x", pady=5)
            
            label_frame = tk.Frame(row, bg=COLOR_BG_PANEL)
            label_frame.pack(fill="x", padx=20)
            
            search_label = tk.Label(label_frame, text="Search: 40%", 
                                   font=(FONT_FAMILY_PRIMARY, 10, "bold"),
                                   bg=COLOR_BG_PANEL, fg=COLOR_ACCENT_CYAN)
            search_label.pack(side="left")
            
            social_label = tk.Label(label_frame, text="Social: 60%",
                                   font=(FONT_FAMILY_PRIMARY, 10, "bold"),
                                   bg=COLOR_BG_PANEL, fg="#3699ff")
            social_label.pack(side="right")
            
            var = tk.IntVar(value=getattr(config, "SEARCH_RATIO", 40))
            
            def on_change(val):
                search_pct = int(float(val))
                social_pct = 100 - search_pct
                search_label.config(text=f"Search: {search_pct}%")
                social_label.config(text=f"Social: {social_pct}%")
                setattr(config, "SEARCH_RATIO", search_pct)
            
            slider = tk.Scale(row, from_=0, to=100, orient="horizontal", variable=var,
                            command=on_change, bg=COLOR_BG_PANEL, fg=COLOR_ACCENT_CYAN,
                            troughcolor=COLOR_INPUT_BG, highlightthickness=0,
                            showvalue=False, length=300)
            slider.pack(fill="x", padx=20, pady=(3, 0))
            
        elif mode == "External":
            self._add_file_row(self.traffic_dynamic_area, "External Referrer File", "FILE_REFERRERS")
    
    def _on_worker_click(self, worker_id):
        if orchestrator.has_worker(worker_id):
            orchestrator.toggle_worker_visibility(worker_id)
        else:
            self.log_console.log(f"[WARNING] Worker #{worker_id} is not active")
    
    def _show_page(self, page_name):
        for name, page in self.pages.items():
            page.pack_forget() if name != page_name else page.pack(fill="both", expand=True)
        self.current_page = page_name
        
        if page_name == "dashboard":
            self.btn_dashboard.config(bg=COLOR_ACCENT_CYAN)
            self.btn_settings.config(bg=COLOR_BG_MAIN)
        else:
            self.btn_dashboard.config(bg=COLOR_BG_MAIN)
            self.btn_settings.config(bg=COLOR_ACCENT_CYAN)
    
    def _toggle_bot(self):
        self._start_bot() if not self.is_running else self._stop_bot()
    
    def _start_bot(self):
        if not config.FILE_ARTICLES:
            messagebox.showerror("Error", "Please select article file in Settings!")
            return
        try:
            num = int(self.entry_workers.get())
            if num < 1 or num > 100:
                raise ValueError()
        except:
            messagebox.showerror("Error", "Workers must be 1-100!")
            return
        
        config.TASK_COUNT = num
        self.is_running = True
        self.btn_start.config(text="⛔ STOP ENGINE", bg=COLOR_ACCENT_RED)
        self.log_console.log(f"[START] Launching {num} workers...")
        threading.Thread(target=lambda: orchestrator.start(num), daemon=True).start()
    
    def _stop_bot(self):
        self.log_console.log("[STOP] Stopping all workers...")
        self.is_running = False
        self.btn_start.config(text="🚀 START ENGINE", bg=COLOR_SUCCESS)
        threading.Thread(target=orchestrator.stop, daemon=True).start()
    
    def _on_status_change(self, status):
        """Callback dari orchestrator untuk log ke console GUI"""
        if hasattr(self, 'log_console'):
            self.log_console.log(status)
    
    def _on_worker_update(self, worker_id, status, color, info=""):
        """Callback dari orchestrator untuk update worker card"""
        if worker_id in self.worker_cards:
            self.worker_cards[worker_id].update_status(status, color, info)
    
    def _start_stats_update(self):
        def loop():
            if self.is_running:
                stats = orchestrator.get_statistics()
                self.stat_cards['success'].update_value(stats.get('success_count', 0))
                self.stat_cards['failed'].update_value(stats.get('failed_count', 0))
                self.stat_cards['active'].update_value(stats.get('active_workers', 0))
                self.stat_cards['blocked'].update_value(stats.get('blacklisted_ips', 0))
            self.after(1000, loop)
        loop()
    
    def _on_close(self):
        if self.is_running:
            if messagebox.askyesno("Exit", "Bot is running. Stop and exit?"):
                self._stop_bot()
                self.after(2000, self.destroy)
        else:
            self.destroy()
