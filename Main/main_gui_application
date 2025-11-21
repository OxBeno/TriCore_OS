#!/usr/bin/env python3
import customtkinter as ctk
from customtkinter import filedialog
import subprocess
import sys
import os
import datetime
import threading
from collections import deque # (جديد) عشان سجل الأوامر

# --- (جديد) إضافة مكتبة pandas عشان نقدر نقرا الملف بسرعة ---
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("Warning: 'pandas' library not found. Data Analysis feature will be disabled.")
    print("Please install it: pip install pandas")

# --- Import the function from your ai_shell_helper.py file ---
try:
    # (جديد) تعديل بسيط في ملف الهيلبر (هييجي في الملف الجاي)
    from ai_shell_helper import get_shell_command
except ImportError:
    print("Error: 'ai_shell_helper.py' not found.")
    print("Please make sure all .py files are in the same folder.")
    sys.exit(1)

# --- Find the path to EDA_final.py ---
EDA_SCRIPT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'EDA_final.py')

if not os.path.exists(EDA_SCRIPT_PATH):
    print(f"Warning: '{EDA_SCRIPT_PATH}' not found.")
    print("The 'Data Analysis' button may not work.")

# --- (جديد) برومبت الشرح ---
EXPLAIN_SYSTEM_PROMPT = (
    "You are an expert programming and shell command tutor. "
    "A user will provide a shell command, and your job is to explain it. "
    "Break down the command into its core components (the command itself, flags, arguments). "
    "Explain what each part does in a simple, clear, and beginner-friendly way. "
    "Format your response as a simple text log. "
    "Start with a one-line summary. Example:\n\n"
    "Summary: This command finds all '.py' files and counts them.\n\n"
    "Breakdown:\n"
    "  - `find .`: Searches the current directory.\n"
    "  - `-name '*.py'`: Looks for files ending in '.py'.\n"
    "  - `| wc -l`: Pipes the results to 'word count' to count the lines."
)

# --- (جديد) نافذة الـ History ---
class HistoryWindow(ctk.CTkToplevel):
    def __init__(self, master_app, command_history):
        super().__init__(master_app)
        self.master_app = master_app
        
        self.configure(fg_color=master_app.APP_BG)
        self.title("Command History")
        self.geometry("600x400")
        self.transient(master_app)
        self.resizable(True, True)

        if not command_history:
            label = ctk.CTkLabel(self, text="History is empty.", font=master_app.FONT_TEXT)
            label.pack(padx=20, pady=20, expand=True)
            return

        scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # نعرضهم من الأحدث للأقدم
        for command in reversed(command_history):
            self.add_history_entry(scroll_frame, command)
            
    def add_history_entry(self, frame, command):
        btn_text = command.replace('\n', ' ').strip()
        if len(btn_text) > 80:
            btn_text = btn_text[:80] + "..."
            
        btn = ctk.CTkButton(
            frame,
            text=btn_text,
            font=self.master_app.FONT_MONO,
            anchor="w",
            fg_color=self.master_app.COLOR_GRAY,
            hover_color=self.master_app.COLOR_GRAY_HOVER,
            command=lambda c=command: self.select_command(c)
        )
        btn.pack(fill="x", pady=4, padx=5)

    def select_command(self, command):
        self.master_app.set_command_from_history(command)
        self.destroy()

# --- (معدل) نافذة الـ EDA ---
class EdaWindow(ctk.CTkToplevel):
    def __init__(self, master_app):
        super().__init__(master_app)
        
        self.master_app = master_app 
        self.selected_file_path = None
        
        self.configure(fg_color=master_app.APP_BG)
        self.title("Data Analysis")
        self.geometry("500x300")
        self.transient(master_app) 
        self.resizable(False, False)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        main_frame = ctk.CTkFrame(self, fg_color=master_app.NAV_RAIL_BG) 
        main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)

        self.browse_button = ctk.CTkButton(
            main_frame,
            text="📁 Browse...",
            command=self.browse_file,
            font=master_app.FONT_BUTTON_SIDE,
            fg_color=master_app.COLOR_GRAY, 
            hover_color=master_app.COLOR_GRAY_HOVER 
        )
        self.browse_button.grid(row=0, column=0, columnspan=2, padx=10, pady=15, sticky="ew")

        self.file_label = ctk.CTkLabel(
            main_frame,
            text="No file selected.",
            font=master_app.FONT_STATUS,
            text_color=master_app.TEXT_COLOR_DIM 
        )
        self.file_label.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        self.info_label = ctk.CTkLabel(
            main_frame,
            text="Rows: N/A  |  Columns: N/A",
            font=master_app.FONT_TEXT,
            text_color=master_app.TEXT_COLOR_NORMAL 
        )
        self.info_label.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="w")
        
        self.generate_button = ctk.CTkButton(
            self,
            text="🚀 Generate EDA Report",
            command=self.run_eda_script,
            font=master_app.FONT_BUTTON_LARGE,
            height=40,
            state="disabled", 
            fg_color=master_app.COLOR_PRIMARY, 
            hover_color=master_app.COLOR_PRIMARY_HOVER 
        )
        self.generate_button.grid(row=1, column=0, padx=20, pady=15, sticky="ew")

    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="Select a CSV file",
            filetypes=(("CSV files", "*.csv"), ("All files", "*.*"))
        )
        if not file_path:
            return
            
        self.selected_file_path = file_path
        self.file_label.configure(text=f"Selected: {os.path.basename(file_path)}", text_color=self.master_app.TEXT_COLOR_DIM)
        self.master_app.log_to_output(f"File selected for EDA: {os.path.basename(file_path)}")
        
        self.info_label.configure(text="Reading file info...", text_color=self.master_app.TEXT_COLOR_DIM)
        self.generate_button.configure(state="disabled")
        threading.Thread(target=self._get_file_info, args=(file_path,), daemon=True).start()

    def _get_file_info(self, file_path):
        try:
            df = pd.read_csv(file_path, nrows=2) 
            cols = len(df.columns)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                rows = sum(1 for line in f) - 1 

            self.after(0, self._update_file_info, rows, cols, None)
        except Exception as e:
            self.after(0, self._update_file_info, -1, -1, str(e))

    def _update_file_info(self, rows, cols, error):
        if error:
            self.info_label.configure(text=f"Error: Could not read file.", text_color=self.master_app.COLOR_RED)
            self.master_app.log_to_output(f"Error reading CSV info: {error}")
            self.generate_button.configure(state="disabled")
        else:
            self.info_label.configure(text=f"Rows: {rows}  |  Columns: {cols}", text_color=self.master_app.TEXT_COLOR_NORMAL)
            self.master_app.log_to_output(f"File Info: {rows} rows, {cols} columns.")
            self.generate_button.configure(state="normal") 

    def run_eda_script(self):
        if not self.selected_file_path:
            return
        
        if not os.path.exists(EDA_SCRIPT_PATH):
            self.master_app.log_to_output(f"Error: 'EDA_final.py' not found at {EDA_SCRIPT_PATH}")
            return

        self.master_app.log_to_output(f"Starting data analysis on {os.path.basename(self.selected_file_path)}...")
        self.master_app.log_to_output("A new terminal window will open to run the analysis.")
        
        try:
            if sys.platform == "win32":
                subprocess.Popen([sys.executable, EDA_SCRIPT_PATH, self.selected_file_path], creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                subprocess.Popen([sys.executable, EDA_SCRIPT_PATH, self.selected_file_path])
            self.master_app.log_to_output("EDA script launched. Check the new window/console for progress.")
        except Exception as e:
            self.master_app.log_to_output(f"Failed to launch data analysis: {str(e)}")
            
        self.destroy() 


# --- GUI Application Class ---
class App(ctk.CTk):
    
    NAV_RAIL_WIDTH_MIN = 70
    NAV_RAIL_WIDTH_MAX = 220

    def __init__(self):
        super().__init__()

        # --- ثيم "Cyber" ---
        self.COLOR_PRIMARY = "#8b5cf6"           # بنفسجي
        self.COLOR_PRIMARY_HOVER = "#a78bfa"    
        self.COLOR_BLUE = "#38bdf8"             
        self.COLOR_BLUE_HOVER = "#7dd3fc"
        self.COLOR_ORANGE = "#ec4899"           
        self.COLOR_ORANGE_HOVER = "#f472b6"
        self.COLOR_RED_ACTIVE = "#e11d48"       # (جديد) أحمر فاقع
        self.COLOR_RED_ACTIVE_HOVER = "#f43f5e"
        self.COLOR_RED_DISABLED = "#450a0a"     # (جديد) أحمر مطفي غامق
        self.COLOR_GRAY = "#3f3f46"             
        self.COLOR_GRAY_HOVER = "#52525b"
        
        self.APP_BG = "#14141c"                 
        self.NAV_RAIL_BG = "#1e1e2b"            
        self.BOX_BG = "#1e1e2b"                 
        self.BORDER_COLOR = "#3f3f46"
        
        self.TEXT_COLOR_NORMAL = "#e2e8f0"      
        self.TEXT_COLOR_DIM = "#a1a1aa"         
        self.TEXT_COLOR_ACCENT = self.COLOR_PRIMARY 
        self.TERMINAL_TEXT_COLOR = "#67e8f9"    
        self.TERMINAL_ERROR_COLOR = "#fca5a5"   # (جديد) لون أخطاء التيرمينال

        # --- Fonts ---
        self.FONT_LOGO = ctk.CTkFont(family="Segoe UI", size=26, weight="bold")
        self.FONT_SUBTITLE = ctk.CTkFont(family="Segoe UI", size=14, weight="normal")
        self.FONT_LABEL = ctk.CTkFont(family="Segoe UI", size=15, weight="bold")
        self.FONT_BUTTON_LARGE = ctk.CTkFont(family="Segoe UI", size=16, weight="bold")
        self.FONT_BUTTON_SIDE = ctk.CTkFont(family="Segoe UI", size=13, weight="bold")
        self.FONT_TEXT = ctk.CTkFont(family="Segoe UI", size=14)
        self.FONT_MONO = ctk.CTkFont(family="Consolas", size=14)
        self.FONT_STATUS = ctk.CTkFont(family="Segoe UI", size=12, weight="normal")

        # --- State ---
        self.sidebar_expanded = False
        self.eda_window = None 
        self.history_window = None # (جديد)
        self.command_history = deque(maxlen=20) # (جديد) سجل لآخر 20 أمر

        # --- Window Setup ---
        self.title("AI Shell Helper")
        self.geometry("1200x750")
        self.minsize(900, 600)
        ctk.set_appearance_mode("Dark")
        self.configure(fg_color=self.APP_BG)

        # --- Main Layout (2 Columns) ---
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- 1. Left Navigation Rail (Toggleable) ---
        self.nav_rail = ctk.CTkFrame(self, fg_color=self.NAV_RAIL_BG, width=self.NAV_RAIL_WIDTH_MIN, corner_radius=0)
        self.nav_rail.grid(row=0, column=0, rowspan=2, sticky="nsw")
        self.nav_rail.grid_propagate(False)

        self.nav_rail.grid_rowconfigure(0, weight=0) 
        self.nav_rail.grid_rowconfigure(1, weight=0) 
        self.nav_rail.grid_rowconfigure(2, weight=0) 
        self.nav_rail.grid_rowconfigure(3, weight=0) # (جديد) زرار الـ History
        self.nav_rail.grid_rowconfigure(4, weight=1) # Spacer

        self.sidebar_toggle_button = ctk.CTkButton(
            self.nav_rail,
            text="≡",
            font=self.FONT_LOGO,
            width=self.NAV_RAIL_WIDTH_MIN - 20,
            height=40,
            anchor="center",
            fg_color="transparent",
            hover_color=self.COLOR_GRAY,
            command=self.toggle_sidebar
        )
        self.sidebar_toggle_button.grid(row=0, column=0, padx=10, pady=25)
        
        self.data_button = ctk.CTkButton(
            self.nav_rail,
            text="📊",
            command=self.open_eda_window, 
            font=self.FONT_BUTTON_SIDE,
            height=40,
            width=self.NAV_RAIL_WIDTH_MIN - 20,
            anchor="center", 
            fg_color=self.COLOR_BLUE,
            hover_color=self.COLOR_BLUE_HOVER
        )
        self.data_button.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        
        if not PANDAS_AVAILABLE:
            self.data_button.configure(state="disabled")

        self.security_button = ctk.CTkButton(
            self.nav_rail,
            text="🛡️",
            command=self.run_security_scan_event,
            font=self.FONT_BUTTON_SIDE,
            height=40,
            width=self.NAV_RAIL_WIDTH_MIN - 20,
            anchor="center", 
            fg_color=self.COLOR_ORANGE,
            hover_color=self.COLOR_ORANGE_HOVER
        )
        self.security_button.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        
        # (جديد) زرار الـ History
        self.history_button = ctk.CTkButton(
            self.nav_rail,
            text="🕒",
            command=self.open_history_window, 
            font=self.FONT_BUTTON_SIDE,
            height=40,
            width=self.NAV_RAIL_WIDTH_MIN - 20,
            anchor="center", 
            fg_color=self.COLOR_GRAY,
            hover_color=self.COLOR_GRAY_HOVER
        )
        self.history_button.grid(row=3, column=0, padx=10, pady=10, sticky="w")

        # --- 2. Main Content Area (Right Side) ---
        main_content = ctk.CTkFrame(self, fg_color="transparent")
        main_content.grid(row=0, column=1, sticky="nsew", padx=20, pady=15)
        
        # (نفس التقسيمة)
        main_content.grid_columnconfigure(0, weight=1)
        main_content.grid_rowconfigure(0, weight=0, pad=0) 
        main_content.grid_rowconfigure(1, weight=0, pad=0) 
        main_content.grid_rowconfigure(2, weight=1) 
        main_content.grid_rowconfigure(3, weight=0, pad=0) 
        main_content.grid_rowconfigure(4, weight=0, pad=0) 
        main_content.grid_rowconfigure(5, weight=1) 
        main_content.grid_rowconfigure(6, weight=0, pad=0) 
        main_content.grid_rowconfigure(7, weight=2) 
        main_content.grid_rowconfigure(8, weight=0, pad=0) 
        main_content.grid_rowconfigure(9, weight=0, pad=0) 


        # --- Header (Logo & Subtitles) ---
        header_frame = ctk.CTkFrame(main_content, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        header_title = ctk.CTkLabel(header_frame, text="New ERA of AI", font=self.FONT_LOGO, text_color=self.COLOR_PRIMARY) 
        header_title.pack(anchor="w")
        
        header_subtitle = ctk.CTkLabel(header_frame, text="Human Language  ➔  Shell Command", font=self.FONT_SUBTITLE, text_color=self.TEXT_COLOR_DIM) 
        header_subtitle.pack(anchor="w")

        # --- Query Box ---
        query_label = ctk.CTkLabel(main_content, text="Enter Your Query", font=self.FONT_LABEL, text_color=self.TEXT_COLOR_DIM) 
        query_label.grid(row=1, column=0, sticky="sw", pady=(10, 5))
        
        self.query_box = ctk.CTkTextbox(
            main_content, 
            border_width=1, 
            border_color=self.BORDER_COLOR, 
            font=self.FONT_TEXT, 
            text_color=self.TEXT_COLOR_NORMAL, 
            fg_color=self.BOX_BG 
        )
        self.query_box.grid(row=2, column=0, sticky="nsew", pady=(0, 10))
        self.query_box.bind("<Control-Return>", self.generate_command_event)

        # --- Generate Button ---
        self.generate_button = ctk.CTkButton(
            main_content,
            text="► GENERATE COMMAND (Ctrl+Enter)",
            command=self.generate_command_event,
            font=self.FONT_BUTTON_LARGE,
            height=50,
            fg_color=self.COLOR_PRIMARY, 
            hover_color=self.COLOR_PRIMARY_HOVER 
        )
        self.generate_button.grid(row=3, column=0, sticky="ew", pady=10)

        # --- Command Box (with Copy/Clear above) ---
        command_header_frame = ctk.CTkFrame(main_content, fg_color="transparent")
        command_header_frame.grid(row=4, column=0, sticky="sew", pady=(10, 5))
        
        command_label = ctk.CTkLabel(command_header_frame, text="Generated Command", font=self.FONT_LABEL, text_color=self.TEXT_COLOR_DIM) 
        command_label.pack(side="left")

        # (جديد) زرار الـ Explain
        self.explain_button = ctk.CTkButton(
            command_header_frame,
            text="✨ Explain",
            command=self.explain_command_event,
            font=self.FONT_BUTTON_SIDE,
            width=80,
            fg_color=self.COLOR_GRAY,
            hover_color=self.COLOR_GRAY_HOVER,
            state="disabled" # (هيبدأ مقفول)
        )
        self.explain_button.pack(side="right")
        
        self.copy_button = ctk.CTkButton(
            command_header_frame,
            text="📋 Copy",
            command=self.copy_command,
            font=self.FONT_BUTTON_SIDE,
            width=80,
            fg_color=self.COLOR_GRAY,
            hover_color=self.COLOR_GRAY_HOVER
        )
        self.copy_button.pack(side="right", padx=5)

        self.clear_button = ctk.CTkButton(
            command_header_frame,
            text="❌ Clear",
            command=self.clear_all_boxes,
            font=self.FONT_BUTTON_SIDE,
            width=80,
            fg_color=self.COLOR_GRAY,
            hover_color=self.COLOR_GRAY_HOVER
        )
        self.clear_button.pack(side="right", padx=5)
        
        self.command_box = ctk.CTkTextbox(
            main_content, 
            border_width=1, 
            border_color=self.BORDER_COLOR, 
            font=self.FONT_MONO, 
            wrap="word", 
            text_color=self.TEXT_COLOR_ACCENT, 
            height=150,
            fg_color=self.BOX_BG 
        )
        self.command_box.grid(row=5, column=0, sticky="nsew", pady=(0, 10))

        # --- Output Box ---
        output_label = ctk.CTkLabel(main_content, text="Execution Output", font=self.FONT_LABEL, text_color=self.TEXT_COLOR_DIM) 
        output_label.grid(row=6, column=0, sticky="sw", pady=(10, 5))
        
        self.output_box = ctk.CTkTextbox(
            main_content, 
            border_width=1, 
            border_color=self.BORDER_COLOR, 
            font=self.FONT_MONO, 
            wrap="word", 
            state="disabled", 
            text_color=self.TERMINAL_TEXT_COLOR, 
            fg_color=self.BOX_BG 
        )
        self.output_box.grid(row=7, column=0, sticky="nsew")
        
        # (جديد) تحديد ألوان التاجات
        self.output_box.tag_config("timestamp_tag", foreground=self.TEXT_COLOR_DIM)
        self.output_box.tag_config("info_tag", foreground=self.TERMINAL_TEXT_COLOR)
        self.output_box.tag_config("error_tag", foreground=self.TERMINAL_ERROR_COLOR)
        
        # --- Execute Button (below output) ---
        self.execute_button = ctk.CTkButton(
            main_content,
            text="🔥 Execute Command",
            command=self.execute_command_event, # (جديد) تغيير الوظيفة
            font=self.FONT_BUTTON_SIDE,
            height=35,
            fg_color=self.COLOR_RED_DISABLED, 
            hover_color=self.COLOR_RED_DISABLED, 
            state="disabled"
        )
        self.execute_button.grid(row=8, column=0, sticky="ew", pady=(10, 0))

        # --- Footer Status Bar ---
        self.status_bar = ctk.CTkLabel(main_content, text="Ready", anchor="w", font=self.FONT_STATUS, text_color=self.TEXT_COLOR_DIM, height=25) 
        self.status_bar.grid(row=9, column=0, sticky="ew", pady=(5, 0))

        if not PANDAS_AVAILABLE:
            self.log_to_output("Warning: 'pandas' library not found.")
            self.log_to_output("Data Analysis feature is disabled. Please run: pip install pandas")

    # --- Sidebar Toggle Function ---
    def toggle_sidebar(self):
        if self.sidebar_expanded:
            self.nav_rail.configure(width=self.NAV_RAIL_WIDTH_MIN)
            self.sidebar_toggle_button.configure(text="≡", anchor="center")
            self.data_button.configure(text="📊", anchor="center", width=self.NAV_RAIL_WIDTH_MIN - 20)
            self.security_button.configure(text="🛡️", anchor="center", width=self.NAV_RAIL_WIDTH_MIN - 20)
            self.history_button.configure(text="🕒", anchor="center", width=self.NAV_RAIL_WIDTH_MIN - 20)
            self.sidebar_expanded = False
        else:
            self.nav_rail.configure(width=self.NAV_RAIL_WIDTH_MAX)
            self.sidebar_toggle_button.configure(text="≡  AI Shell Helper", anchor="w")
            self.data_button.configure(text="📊 Data Analysis", anchor="w", width=self.NAV_RAIL_WIDTH_MAX - 20)
            self.security_button.configure(text="🛡️ Security Scan", anchor="w", width=self.NAV_RAIL_WIDTH_MAX - 20)
            self.history_button.configure(text="🕒 Command History", anchor="w", width=self.NAV_RAIL_WIDTH_MAX - 20)
            self.sidebar_expanded = True

    # --- Button Functions ---
    def log_to_output(self, message, tag="info_tag"):
        """Helper function to add messages to the output box."""
        self.output_box.configure(state="normal")
        timestamp = f"[{datetime.datetime.now().strftime('%H:%M:%S')}] "
        self.output_box.insert("end", timestamp, "timestamp_tag")
        self.output_box.insert("end", f"{message}\n\n", tag)
        self.output_box.configure(state="disabled")
        self.output_box.see("end")

    def open_eda_window(self):
        if self.eda_window is None or not self.eda_window.winfo_exists():
            self.eda_window = EdaWindow(self) 
            self.eda_window.focus()
        else:
            self.eda_window.focus() 

    # (جديد) وظيفة فتح نافذة الـ History
    def open_history_window(self):
        if self.history_window is None or not self.history_window.winfo_exists():
            self.history_window = HistoryWindow(self, self.command_history)
            self.history_window.focus()
        else:
            self.history_window.focus()
            
    # (جديد) وظيفة استرجاع الأمر من الـ History
    def set_command_from_history(self, command):
        self.command_box.delete("1.0", "end")
        self.command_box.insert("1.0", command)
        # (جديد) بعد ما نرجعه، نفعّل الزراير بتاعته
        self.after(10, self._update_ui_after_generation, command, from_history=True)

    # --- Generate Command (Threaded) ---
    def _generate_command_thread(self, query):
        try:
            # (معدل) نستخدم البرومبت الديفولت (None)
            command = get_shell_command(query, system_prompt_override=None)
            self.after(0, self._update_ui_after_generation, command)
        except Exception as e:
            error_message = f"# Error: {str(e)}"
            self.after(0, self._update_ui_after_generation, error_message)

    def _update_ui_after_generation(self, command, from_history=False):
        if not from_history:
            self.command_box.insert("1.0", command)
        
        if command.startswith("# Cannot fulfill") or command.startswith("# Error"):
            if not from_history:
                self.log_to_output(f"AI returned an error: {command}", "error_tag")
            # (جديد) اقفل الزراير لو الأمر فيه خطأ
            self.execute_button.configure(state="disabled", fg_color=self.COLOR_RED_DISABLED, hover_color=self.COLOR_RED_DISABLED)
            self.explain_button.configure(state="disabled")
        else:
            if not from_history:
                self.log_to_output("Command generated successfully.", "info_tag")
                # (جديد) خزّن الأمر في الـ History
                if command not in self.command_history:
                    self.command_history.append(command)
            
            # (جديد) افتح الزراير
            self.execute_button.configure(state="normal", fg_color=self.COLOR_RED_ACTIVE, hover_color=self.COLOR_RED_ACTIVE_HOVER)
            self.explain_button.configure(state="normal")
        
        self.generate_button.configure(state="normal", text="► GENERATE COMMAND (Ctrl+Enter)")
        self.status_bar.configure(text="Ready")

    def generate_command_event(self, event=None):
        query = self.query_box.get("1.0", "end-1c").strip()
        if not query:
            self.log_to_output("Error: Query is empty.", "error_tag")
            return

        self.status_bar.configure(text="Generating command...")
        self.command_box.delete("1.0", "end")
        
        # (جديد) اقفل كل الزراير المتعلقة بالكود
        self.generate_button.configure(state="disabled", text="⌛ Generating...")
        self.execute_button.configure(state="disabled", fg_color=self.COLOR_RED_DISABLED, hover_color=self.COLOR_RED_DISABLED)
        self.explain_button.configure(state="disabled")
        
        threading.Thread(target=self._generate_command_thread, args=(query,), daemon=True).start()

    # --- (جديد) Explain Command (Threaded) ---
    def _explain_command_thread(self, command):
        try:
            # (جديد) نبعت البرومبت بتاع الشرح
            explanation = get_shell_command(command, system_prompt_override=EXPLAIN_SYSTEM_PROMPT)
            self.after(0, self._update_ui_after_explain, explanation)
        except Exception as e:
            self.after(0, self._update_ui_after_explain, f"# Error explaining command: {str(e)}")

    def _update_ui_after_explain(self, explanation):
        self.log_to_output("--- AI EXPLANATION ---", "info_tag")
        self.log_to_output(explanation, "info_tag")
        self.log_to_output("--- END OF EXPLANATION ---", "info_tag")
        self.explain_button.configure(state="normal", text="✨ Explain")
        self.status_bar.configure(text="Ready")

    def explain_command_event(self):
        command = self.command_box.get("1.0", "end-1c").strip()
        if not command or command.startswith("#"):
            self.log_to_output("Error: No valid command to explain.", "error_tag")
            return
            
        self.status_bar.configure(text="AI is explaining...")
        self.explain_button.configure(state="disabled", text="...")
        threading.Thread(target=self._explain_command_thread, args=(command,), daemon=True).start()

    # --- (جديد) Execute Command (Threaded) ---
    def _execute_command_thread(self, command):
        try:
            # (جديد) تنفيذ الأمر
            # shell=True خطير، ولكنه ضروري عشان الأوامر زي | و > تشتغل
            result = subprocess.run(command, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
            self.after(0, self._update_ui_after_execute, result.stdout, result.stderr)
        except Exception as e:
            self.after(0, self._update_ui_after_execute, None, f"Execution failed: {str(e)}")

    def _update_ui_after_execute(self, stdout, stderr):
        if stdout:
            self.log_to_output("--- COMMAND OUTPUT (stdout) ---", "info_tag")
            self.log_to_output(stdout.strip(), "info_tag")
            self.log_to_output("--- END OF OUTPUT ---", "info_tag")
        if stderr:
            self.log_to_output("--- COMMAND ERROR (stderr) ---", "error_tag")
            self.log_to_output(stderr.strip(), "error_tag")
            self.log_to_output("--- END OF ERROR ---", "error_tag")
        
        self.log_to_output("Command execution finished.", "info_tag")
        
        # رجّع الزراير لحالتها الطبيعية
        self.execute_button.configure(state="normal", text="🔥 Execute Command")
        self.generate_button.configure(state="normal")
        self.status_bar.configure(text="Ready")

    def execute_command_event(self):
        command = self.command_box.get("1.0", "end-1c").strip()
        if not command or command.startswith("#"):
            self.log_to_output("Error: No valid command to execute.", "error_tag")
            return

        self.log_to_output(f"Executing: {command}", "info_tag")
        
        # (جديد) اقفل الزراير الأساسية أثناء التنفيذ
        self.status_bar.configure(text="Executing command...")
        self.execute_button.configure(state="disabled", text="⌛ Executing...")
        self.generate_button.configure(state="disabled")
        
        threading.Thread(target=self._execute_command_thread, args=(command,), daemon=True).start()

    # --- Security Scan (Threaded) ---
    def _security_scan_thread(self):
        try:
            response = get_shell_command("run quick scan", system_prompt_override=None)
            self.after(0, self._update_ui_after_scan, response)
        except Exception as e:
            self.after(0, self._update_ui_after_scan, f"# Error: {str(e)}")

    def _update_ui_after_scan(self, response):
        self.log_to_output(response)
        self.security_button.configure(state="normal")
        self.status_bar.configure(text="Ready")

    def run_security_scan_event(self):
        self.status_bar.configure(text="Running security scan...")
        self.security_button.configure(state="disabled")
        threading.Thread(target=self._security_scan_thread, daemon=True).start()

    # --- Other Utilities ---
    def copy_command(self):
        command = self.command_box.get("1.0", "end-1c").strip()
        if command and not command.startswith("#"):
            self.clipboard_clear()
            self.clipboard_append(command)
            self.log_to_output("Command copied to clipboard.")
        else:
            self.log_to_output("Error: Nothing valid to copy.", "error_tag")

    def clear_all_boxes(self):
        self.query_box.delete("1.0", "end")
        self.command_box.delete("1.0", "end")
        
        # (جديد) نقفل الزراير بعد المسح
        self.execute_button.configure(state="disabled", fg_color=self.COLOR_RED_DISABLED, hover_color=self.COLOR_RED_DISABLED)
        self.explain_button.configure(state="disabled")
        
        self.log_to_output("Query and Command boxes cleared.")
        self.status_bar.configure(text="Ready")


if __name__ == "__main__":
    app = App()
    app.mainloop()
