"""
Advanced Configuration Window
Window pop-up untuk semua settings detail
"""

import tkinter as tk
from tkinter import ttk, filedialog
from ui.styles import *
from ui.components import Bevel3DButton, SharpPanel
from bot_config import config

class AdvancedSettingsWindow(tk.Toplevel):
    """Window untuk advanced configuration"""
    
    def __init__(self, parent):
        """Initialize advanced settings window"""
        super().__init__(parent)
        
        self.title("Advanced Configuration")
        self.geometry("900x700")
        self.configure(bg=COLOR_BG_MAIN)
        self.resizable(False, False)
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        # Storage untuk widgets
        self.widgets = {}
        
        # Create UI
        self._create_header()
        self._create_scrollable_content()
        self._create_footer()
        
        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (900 // 2)
        y = (self.winfo_screenheight() // 2) - (700 // 2)
        self.geometry(f"900x700+{x}+{y}")
    
    def _create_header(self):
        """Create header"""
        header = tk.Frame(self, bg=COLOR_BG_PANEL, height=80)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="⚙️ ADVANCED CONFIGURATION",
            font=(FONT_FAMILY_PRIMARY, 18, "bold"),
            bg=COLOR_BG_PANEL,
            fg=COLOR_ACCENT_CYAN
        ).pack(pady=25)
    
    def _create_scrollable_content(self):
        """Create scrollable content area"""
        # Container
        container = tk.Frame(self, bg=COLOR_BG_MAIN)
        container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Canvas + Scrollbar
        canvas = tk.Canvas(container, bg=COLOR_BG_MAIN, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        
        self.scroll_frame = tk.Frame(canvas, bg=COLOR_BG_MAIN)
        
        canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Build sections
        self._build_files_section()
        self._build_identity_section()
        self._build_gatekeeper_section()
        self._build_traffic_section()
        self._build_interaction_section()
        self._build_browser_section()
        
        # Update scroll region
        self.scroll_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))
    
    def _create_section(self, title):
        """Create section frame"""
        section = SharpPanel(self.scroll_frame)
        section.pack(fill="x", pady=(0, 15))
        
        # Title
        tk.Label(
            section,
            text=title,
            font=(FONT_FAMILY_PRIMARY, FONT_SIZE_HEADER, "bold"),
            bg=COLOR_BG_PANEL,
            fg=COLOR_SUCCESS,
            anchor="w"
        ).pack(fill="x", padx=15, pady=(15, 10))
        
        # Content frame
        content = tk.Frame(section, bg=COLOR_BG_PANEL)
        content.pack(fill="x", padx=15, pady=(0, 15))
        
        return content
    
    def _add_file_input(self, parent, label, config_key):
        """Add file input row"""
        row = tk.Frame(parent, bg=COLOR_BG_PANEL)
        row.pack(fill="x", pady=5)
        
        tk.Label(
            row,
            text=label,
            font=(FONT_FAMILY_PRIMARY, FONT_SIZE_NORMAL),
            bg=COLOR_BG_PANEL,
            fg=COLOR_TEXT_SECONDARY,
            width=15,
            anchor="w"
        ).pack(side="left")
        
        entry = tk.Entry(
            row,
            font=(FONT_FAMILY_PRIMARY, FONT_SIZE_SMALL),
            bg=COLOR_INPUT_BG,
            fg=COLOR_TEXT_PRIMARY,
            relief="flat"
        )
        entry.pack(side="left", fill="x", expand=True, padx=5)
        entry.insert(0, getattr(config, config_key))
        
        def browse():
            filepath = filedialog.askopenfilename(
                title=f"Select {label}",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if filepath:
                entry.delete(0, tk.END)
                entry.insert(0, filepath)
        
        tk.Button(
            row,
            text="📁",
            command=browse,
            bg=COLOR_INPUT_BG,
            fg=COLOR_TEXT_PRIMARY,
            relief="flat",
            padx=10
        ).pack(side="right")
        
        self.widgets[config_key] = entry
    
    def _add_radio_group(self, parent, label, config_key, options):
        """Add radio button group"""
        row = tk.Frame(parent, bg=COLOR_BG_PANEL)
        row.pack(fill="x", pady=5)
        
        tk.Label(
            row,
            text=label,
            font=(FONT_FAMILY_PRIMARY, FONT_SIZE_NORMAL),
            bg=COLOR_BG_PANEL,
            fg=COLOR_TEXT_SECONDARY,
            width=15,
            anchor="w"
        ).pack(side="left")
        
        var = tk.StringVar(value=getattr(config, config_key))
        
        for option in options:
            tk.Radiobutton(
                row,
                text=option,
                variable=var,
                value=option,
                font=(FONT_FAMILY_PRIMARY, FONT_SIZE_SMALL),
                bg=COLOR_BG_PANEL,
                fg=COLOR_TEXT_PRIMARY,
                selectcolor=COLOR_INPUT_BG,
                activebackground=COLOR_BG_PANEL
            ).pack(side="left", padx=10)
        
        self.widgets[config_key] = var
    
    def _add_switch(self, parent, label, config_key):
        """Add toggle switch"""
        row = tk.Frame(parent, bg=COLOR_BG_PANEL)
        row.pack(fill="x", pady=5)
        
        tk.Label(
            row,
            text=label,
            font=(FONT_FAMILY_PRIMARY, FONT_SIZE_NORMAL),
            bg=COLOR_BG_PANEL,
            fg=COLOR_TEXT_SECONDARY,
            anchor="w"
        ).pack(side="left", fill="x", expand=True)
        
        var = tk.BooleanVar(value=getattr(config, config_key))
        
        switch = tk.Checkbutton(
            row,
            text="",
            variable=var,
            bg=COLOR_BG_PANEL,
            activebackground=COLOR_BG_PANEL,
            selectcolor=COLOR_SUCCESS
        )
        switch.pack(side="right")
        
        self.widgets[config_key] = var
    
    def _add_number_input(self, parent, label, config_key):
        """Add number input"""
        row = tk.Frame(parent, bg=COLOR_BG_PANEL)
        row.pack(fill="x", pady=5)
        
        tk.Label(
            row,
            text=label,
            font=(FONT_FAMILY_PRIMARY, FONT_SIZE_NORMAL),
            bg=COLOR_BG_PANEL,
            fg=COLOR_TEXT_SECONDARY,
            anchor="w"
        ).pack(side="left", fill="x", expand=True)
        
        entry = tk.Entry(
            row,
            font=(FONT_FAMILY_PRIMARY, FONT_SIZE_NORMAL),
            bg=COLOR_INPUT_BG,
            fg=COLOR_TEXT_PRIMARY,
            relief="flat",
            width=10
        )
        entry.insert(0, str(getattr(config, config_key)))
        entry.pack(side="right")
        
        self.widgets[config_key] = entry
    
    def _add_slider(self, parent, label, config_key, min_val, max_val):
        """Add slider with label"""
        row = tk.Frame(parent, bg=COLOR_BG_PANEL)
        row.pack(fill="x", pady=5)
        
        label_frame = tk.Frame(row, bg=COLOR_BG_PANEL)
        label_frame.pack(fill="x")
        
        tk.Label(
            label_frame,
            text=label,
            font=(FONT_FAMILY_PRIMARY, FONT_SIZE_NORMAL),
            bg=COLOR_BG_PANEL,
            fg=COLOR_TEXT_SECONDARY,
            anchor="w"
        ).pack(side="left")
        
        value_label = tk.Label(
            label_frame,
            text=f"{getattr(config, config_key)}%",
            font=(FONT_FAMILY_PRIMARY, FONT_SIZE_NORMAL),
            bg=COLOR_BG_PANEL,
            fg=COLOR_ACCENT_CYAN,
            anchor="e"
        )
        value_label.pack(side="right")
        
        var = tk.IntVar(value=getattr(config, config_key))
        
        def on_change(val):
            value_label.config(text=f"{int(float(val))}%")
        
        slider = tk.Scale(
            row,
            from_=min_val,
            to=max_val,
            orient="horizontal",
            variable=var,
            command=on_change,
            bg=COLOR_BG_PANEL,
            fg=COLOR_ACCENT_CYAN,
            troughcolor=COLOR_INPUT_BG,
            highlightthickness=0,
            showvalue=False
        )
        slider.pack(fill="x", pady=(5, 0))
        
        self.widgets[config_key] = var
    
    def _build_files_section(self):
        """Build files section"""
        content = self._create_section("[section_files]")
        self._add_file_input(content, "Article File", "FILE_ARTICLES")
        self._add_file_input(content, "Proxy File", "FILE_PROXIES")
        self._add_file_input(content, "Referrer File", "FILE_REFERRERS")
    
    def _build_identity_section(self):
        """Build identity/fingerprint section"""
        content = self._create_section("[section_identity]")
        self._add_radio_group(content, "Fingerprint Mode", "FINGERPRINT_MODE", 
                             ["Cortex", "Pro", "JSON"])
        self._add_file_input(content, "JSON Folder", "FINGERPRINT_FOLDER")
        self._add_switch(content, "WebRTC Protection", "WEBRTC_ENABLED")
        self._add_switch(content, "Timezone Sync", "TIMEZONE_SYNC")
        self._add_radio_group(content, "User Agent", "USER_AGENT_MODE",
                             ["Mixed", "Mobile Only", "Desktop Only"])
    
    def _build_gatekeeper_section(self):
        """Build proxy gatekeeper section"""
        content = self._create_section("[section_gatekeeper]")
        self._add_number_input(content, "Max Latency (ms)", "MAX_PROXY_LATENCY")
        self._add_switch(content, "Check Duplicate IP", "CHECK_DUPLICATE_IP")
        self._add_radio_group(content, "Protocol", "PROXY_TYPE",
                             ["auto", "http", "socks4", "socks5"])
    
    def _build_traffic_section(self):
        """Build traffic section"""
        content = self._create_section("[section_traffic]")
        self._add_radio_group(content, "Traffic Mode", "TRAFFIC_MODE",
                             ["Hybrid", "External"])
        self._add_slider(content, "Search / Social Ratio", "SEARCH_RATIO", 0, 100)
    
    def _build_interaction_section(self):
        """Build interaction section"""
        content = self._create_section("[section_interaction]")
        self._add_number_input(content, "Target CTR (%)", "TARGET_CTR")
        self._add_number_input(content, "Scroll Min", "SCROLL_MIN")
        self._add_number_input(content, "Scroll Max", "SCROLL_MAX")
        self._add_number_input(content, "Delay Min (s)", "DELAY_MIN")
        self._add_number_input(content, "Delay Max (s)", "DELAY_MAX")
        self._add_radio_group(content, "Mouse Style", "MOUSE_STYLE",
                             ["Human Curves", "Direct Jump"])
    
    def _build_browser_section(self):
        """Build browser section"""
        content = self._create_section("[section_browser]")
        self._add_switch(content, "Headless Mode", "HEADLESS")
        self._add_radio_group(content, "Visibility", "BROWSER_VISIBILITY",
                             ["stealth", "ghost", "normal"])
    
    def _create_footer(self):
        """Create footer with buttons"""
        footer = tk.Frame(self, bg=COLOR_BG_PANEL, height=80)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)
        
        button_frame = tk.Frame(footer, bg=COLOR_BG_PANEL)
        button_frame.pack(expand=True)
        
        Bevel3DButton(
            button_frame,
            text="💾 SAVE CONFIGURATION",
            command=self._save_config,
            color=COLOR_SUCCESS,
            width=20
        ).pack(side="left", padx=10)
        
        Bevel3DButton(
            button_frame,
            text="❌ CANCEL",
            command=self.destroy,
            color=COLOR_ACCENT_RED,
            width=15
        ).pack(side="left", padx=10)
    
    def _save_config(self):
        """Save all configurations"""
        try:
            # Update config values
            for key, widget in self.widgets.items():
                if isinstance(widget, tk.Entry):
                    value = widget.get()
                    # Convert to appropriate type
                    if key in ['SCROLL_MIN', 'SCROLL_MAX', 'MAX_PROXY_LATENCY', 
                              'DELAY_MIN', 'DELAY_MAX', 'MAX_RETRIES', 'RETRY_DELAY']:
                        value = int(value) if value else 0
                    elif key == 'TARGET_CTR':
                        value = float(value) if value else 0.0
                    setattr(config, key, value)
                elif isinstance(widget, (tk.StringVar, tk.BooleanVar, tk.IntVar)):
                    setattr(config, key, widget.get())
            
            # Show success message
            tk.messagebox.showinfo("Success", "Configuration saved successfully!")
            self.destroy()
        
        except Exception as e:
            tk.messagebox.showerror("Error", f"Failed to save configuration: {e}")
