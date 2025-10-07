"""
en_04_main_tkinter.py
Tkinter desktop interface for ChatBotAnalyzer (documented).
Features:
- Input for API key (paste / load file / env)
- Select CSV
- Start analysis in background thread (non-blocking)
- Progress log and Cancel button (thread-safe via threading.Event)
- Tabs for AI Analysis and Statistics (text)
- Attempt to render Plotly figures as PNG using kaleido; fallback: open HTML file in browser
Notes:
- Requires pillow and kaleido for image rendering from Plotly.
- To run: python en_04_main_tkinter.py
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import queue
import time
import os
from data_eng_insights.statitics_analisys_with_ai_chats.test_en_02_api_key_reader import get_api_key, read_api_key_from_file
from data_eng_insights.statitics_analisys_with_ai_chats.test_en_01_analyzer import ChatBotAnalyzer
import json
import io
import webbrowser

# Optional: pillow for image display and kaleido for fig -> image
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False

class AnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ChatBot Analyzer — Desktop")
        self.api_key = ""
        self.model = os.environ.get("DEFAULT_LLM_MODEL", "deepseek")
        self.csv_path = None
        self.cancel_event = threading.Event()
        self.log_queue = queue.Queue()

        # UI layout
        self._build_ui()

        # Start a loop to poll the log queue and update UI
        self.root.after(200, self._process_log_queue)

    def _build_ui(self):
        frm = ttk.Frame(self.root, padding=8)
        frm.pack(fill="both", expand=True)

        # Top: API key and CSV selection
        top = ttk.Frame(frm)
        top.pack(fill="x", pady=4)
        ttk.Label(top, text="API Key:").pack(side="left")
        self.api_entry = ttk.Entry(top, width=50, show="*")
        self.api_entry.pack(side="left", padx=4)
        ttk.Button(top, text="Load key file", command=self._load_key_file).pack(side="left", padx=4)
        ttk.Button(top, text="Use env key", command=self._use_env_key).pack(side="left", padx=4)

        ttk.Button(top, text="Select CSV", command=self._select_csv).pack(side="left", padx=6)
        self.csv_label = ttk.Label(top, text="No CSV selected", width=40)
        self.csv_label.pack(side="left", padx=4)

        # Control buttons: Analyze / Cancel
        ctrl = ttk.Frame(frm)
        ctrl.pack(fill="x", pady=4)
        self.analyze_btn = ttk.Button(ctrl, text="Analyze Data", command=self.start_analysis, state="normal")
        self.analyze_btn.pack(side="left", padx=2)
        self.cancel_btn = ttk.Button(ctrl, text="Cancel", command=self._cancel, state="disabled")
        self.cancel_btn.pack(side="left", padx=2)

        # Progress log
        log_frame = ttk.LabelFrame(frm, text="Progress log")
        log_frame.pack(fill="both", expand=False, pady=6)
        self.log_text = tk.Text(log_frame, height=8, wrap="word")
        self.log_text.pack(fill="both", expand=True)

        # Tabs for outputs
        tabs = ttk.Notebook(frm)
        tabs.pack(fill="both", expand=True)
        self.tab_ai = ttk.Frame(tabs)
        self.tab_stats = ttk.Frame(tabs)
        tabs.add(self.tab_ai, text="AI Analysis")
        tabs.add(self.tab_stats, text="Statistics")

        # AI analysis text
        self.ai_text = tk.Text(self.tab_ai, wrap="word")
        self.ai_text.pack(fill="both", expand=True)

        # Stats text
        self.stats_text = tk.Text(self.tab_stats, wrap="word")
        self.stats_text.pack(fill="both", expand=True)

        # Visualizations frame (below tabs)
        vis_frame = ttk.LabelFrame(frm, text="Visualizations (images or open HTML)")
        vis_frame.pack(fill="both", expand=False, pady=6)
        self.vis_container = ttk.Frame(vis_frame)
        self.vis_container.pack(fill="both", expand=True)

    def _load_key_file(self):
        p = filedialog.askopenfilename(filetypes=[("Text files","*.txt"),("All files","*.*")])
        if not p:
            return
        k = read_api_key_from_file(p)
        if k:
            self.api_entry.delete(0, tk.END)
            self.api_entry.insert(0, k)
            self._log("Loaded API key from file.")
        else:
            messagebox.showwarning("Key not detected", "Could not parse key from file.")

    def _use_env_key(self):
        k = get_api_key()
        if k:
            self.api_entry.delete(0, tk.END)
            self.api_entry.insert(0, k)
            self._log("Loaded API key from environment variable.")
        else:
            messagebox.showinfo("Not found", "No API key found in environment.")

    def _select_csv(self):
        p = filedialog.askopenfilename(filetypes=[("CSV files","*.csv"),("All files","*.*")])
        if not p:
            return
        self.csv_path = p
        self.csv_label.config(text=os.path.basename(p))
        self._log(f"Selected CSV: {p}")

    def _log(self, msg: str):
        ts = time.strftime("%H:%M:%S")
        self.log_queue.put(f"[{ts}] {msg}\\n")

    def _process_log_queue(self):
        try:
            while True:
                msg = self.log_queue.get_nowait()
                self.log_text.insert("end", msg)
                self.log_text.see("end")
        except queue.Empty:
            pass
        # schedule next poll
        self.root.after(200, self._process_log_queue)

    def start_analysis(self):
        if not self.csv_path:
            messagebox.showwarning("CSV not selected", "Please select a CSV file first.")
            return
        self.api_key = self.api_entry.get().strip()
        if not self.api_key:
            self._log("Warning: no API key provided; LLM step will be skipped.")
        self.analyze_btn.config(state="disabled")
        self.cancel_btn.config(state="normal")
        self.cancel_event.clear()
        t = threading.Thread(target=self._worker)
        t.daemon = True
        t.start()

    def _cancel(self):
        self._log("Cancellation requested. Attempting to stop worker...")
        self.cancel_event.set()
        self.cancel_btn.config(state="disabled")

    def _worker(self):
        try:
            self._log("Starting analysis worker...")
            # Load small sample quickly to show immediate stats
            analyzer = ChatBotAnalyzer(openrouter_api_key=self.api_key or "", model=self.model)
            self._log("Loading CSV...")
            df = analyzer.load_csv(self.csv_path, nrows=5000)
            if self.cancel_event.is_set():
                self._log("Cancelled after loading CSV.")
                return
            self._log("Generating structured statistics...")
            struct = analyzer.generate_statistics_struct(df)
            md = analyzer.generate_statistics_markdown(df, struct)
            self._log("Generating visualizations...")
            figs = analyzer.generate_visualizations(df)
            if self.cancel_event.is_set():
                self._log("Cancelled before calling LLM.")
            ai_json, ai_text = None, ""
            if self.api_key:
                self._log("Calling LLM (OpenRouter)...")
                prompt = analyzer.create_analysis_prompt(struct, md[:2000])
                ai_json, ai_text = analyzer.call_llm(prompt)
                self._log("LLM call finished.")
            else:
                self._log("No API key: skipping LLM call.")
            # Update UI (must run in main thread)
            self.root.after(10, lambda: self._update_ui(md, struct, ai_text, ai_json, figs))
            self._log("Worker finished.")
        except Exception as e:
            self._log(f"Worker error: {e}")
        finally:
            self.root.after(10, lambda: self.analyze_btn.config(state="normal"))
            self.root.after(10, lambda: self.cancel_btn.config(state="disabled"))

    def _update_ui(self, md, struct, ai_text, ai_json, figs):
        # Update texts
        self.stats_text.delete("1.0", "end")
        self.stats_text.insert("1.0", md)
        self.ai_text.delete("1.0", "end")
        if ai_json:
            pretty = json.dumps(ai_json, indent=2, ensure_ascii=False)
            self.ai_text.insert("1.0", pretty + "\\n\\n---\\n\\n" + (ai_text or ""))
        else:
            self.ai_text.insert("1.0", ai_text or "No AI output (no key or error).")
        # Visualizations: try to render as images
        for widget in self.vis_container.winfo_children():
            widget.destroy()
        if not figs:
            ttk.Label(self.vis_container, text="No visualizations generated.").pack()
        else:
            for name, fig in figs.items():
                # Try to render as PNG (kaleido) if pillow available; else write HTML and provide button
                try:
                    img_bytes = fig.to_image(format="png", engine="kaleido")
                    if PIL_AVAILABLE:
                        img = Image.open(io.BytesIO(img_bytes))
                        photo = ImageTk.PhotoImage(img)
                        lbl = ttk.Label(self.vis_container, image=photo)
                        lbl.image = photo
                        lbl.pack(padx=4, pady=4)
                    else:
                        # write to temp file and open in browser
                        tmp_html = f"viz_{name}.html"
                        fig.write_html(tmp_html)
                        b = ttk.Button(self.vis_container, text=f"Open {name} in browser", command=lambda p=tmp_html: webbrowser.open('file://' + os.path.abspath(p)))
                        b.pack(padx=2, pady=2)
                except Exception:
                    # Fallback: write HTML and present button
                    tmp_html = f"viz_{name}.html"
                    fig.write_html(tmp_html)
                    b = ttk.Button(self.vis_container, text=f"Open {name} in browser", command=lambda p=tmp_html: webbrowser.open('file://' + os.path.abspath(p)))
                    b.pack(padx=2, pady=2)

if __name__ == "__main__":
    root = tk.Tk()
    app = AnalyzerApp(root)
    root.geometry("1100x700")
    root.mainloop()