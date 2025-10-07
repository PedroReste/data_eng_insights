# en_04_main_tkinter.py
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import threading
import os

# Import from our modules
from en_01_analyzer import ChatBotAnalyzer

class AnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Analyzer")
        self.root.geometry("1000x700")
        
        self.current_file = ""
        self.results = None
        
        self.setup_ui()
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = ttk.Label(main_frame, text="📊 Data Analyzer", font=('Arial', 16, 'bold'))
        title.pack(pady=10)
        
        # Info Section
        info_frame = ttk.LabelFrame(main_frame, text="Information", padding="10")
        info_frame.pack(fill=tk.X, pady=5)
        
        info_text = "API key is automatically loaded from 'api_key.txt' file in the same folder."
        info_label = ttk.Label(info_frame, text=info_text, wraplength=800)
        info_label.pack()
        
        # File Section
        file_frame = ttk.LabelFrame(main_frame, text="Data File", padding="10")
        file_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(file_frame, text="Select CSV", command=self.select_csv).pack(side=tk.LEFT)
        self.file_label = ttk.Label(file_frame, text="No file selected")
        self.file_label.pack(side=tk.LEFT, padx=10)
        
        # Analyze Button
        self.analyze_btn = ttk.Button(main_frame, text="Analyze Data", 
                                     command=self.start_analysis, state="disabled")
        self.analyze_btn.pack(pady=10)
        
        # Progress
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=5)
        
        # Results Notebook
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # AI Analysis Tab
        ai_frame = ttk.Frame(self.notebook)
        self.notebook.add(ai_frame, text="AI Analysis")
        self.ai_text = scrolledtext.ScrolledText(ai_frame, wrap=tk.WORD)
        self.ai_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Stats Tab
        stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(stats_frame, text="Statistics")
        self.stats_text = scrolledtext.ScrolledText(stats_frame, wrap=tk.WORD)
        self.stats_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Save Buttons
        save_frame = ttk.Frame(main_frame)
        save_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(save_frame, text="Save Statistics", 
                  command=self.save_stats).pack(side=tk.LEFT, padx=5)
        ttk.Button(save_frame, text="Save AI Analysis", 
                  command=self.save_ai).pack(side=tk.LEFT, padx=5)
        ttk.Button(save_frame, text="Save Complete Report", 
                  command=self.save_complete).pack(side=tk.LEFT, padx=5)
    
    def select_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.current_file = file_path
            self.file_label.config(text=os.path.basename(file_path))
            self.check_ready()
    
    def check_ready(self):
        if self.current_file:
            self.analyze_btn.config(state="normal")
    
    def start_analysis(self):
        thread = threading.Thread(target=self.run_analysis)
        thread.daemon = True
        thread.start()
        self.progress.start()
        self.analyze_btn.config(state="disabled")
    
    def run_analysis(self):
        try:
            # API key is automatically loaded by ChatBotAnalyzer
            analyzer = ChatBotAnalyzer()
            self.results = analyzer.analyze_csv(self.current_file, save_output=False)
            self.root.after(0, self.show_results)
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        finally:
            self.root.after(0, self.progress.stop)
            self.root.after(0, lambda: self.analyze_btn.config(state="normal"))
    
    def show_results(self):
        if self.results:
            self.ai_text.delete(1.0, tk.END)
            self.ai_text.insert(tk.END, self.results['ai_analysis'])
            
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(tk.END, self.results['statistics'])
            
            messagebox.showinfo("Success", "Analysis complete!")
        else:
            messagebox.showerror("Error", "Analysis failed. Please check your API key file.")
    
    def save_stats(self):
        if self.results:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".md",
                filetypes=[("Markdown files", "*.md"), ("Text files", "*.txt")]
            )
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.results['statistics'])
                messagebox.showinfo("Success", "Statistics saved!")
    
    def save_ai(self):
        if self.results:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".md",
                filetypes=[("Markdown files", "*.md"), ("Text files", "*.txt")]
            )
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.results['ai_analysis'])
                messagebox.showinfo("Success", "AI analysis saved!")
    
    def save_complete(self):
        if self.results:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".md",
                filetypes=[("Markdown files", "*.md"), ("Text files", "*.txt")]
            )
            if file_path:
                combined = f"# Comprehensive Analysis Report\n\n## Statistics\n\n{self.results['statistics']}\n\n## AI Insights\n\n{self.results['ai_analysis']}"
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(combined)
                messagebox.showinfo("Success", "Complete report saved!")

if __name__ == "__main__":
    root = tk.Tk()
    app = AnalyzerApp(root)
    root.mainloop()