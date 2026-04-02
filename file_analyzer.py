"""
File Analyzer Application
A UI application that analyzes files in a folder and displays information in a table format.
"""

import os
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from typing import List, Dict, Any, Tuple
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# Settings file path
SETTINGS_FILE = Path(__file__).parent / "settings.json"
HISTORY_FILE = Path(__file__).parent / "analysis_history.json"

# Default settings
DEFAULT_SETTINGS = {
    "last_folder": "",
    "filter_extensions": "",
    "filter_exclude": "",
    "exclude_folders": "",
    "include_subfolders": True,
    "sort_columns": []  # List of (column, reverse) tuples for multi-column sort
}

# History structure
DEFAULT_HISTORY = {
    "analyses": []  # List of analysis entries
}


class FileAnalyzerApp:
    """Main application class for File Analyzer."""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("File Analyzer")
        self.root.geometry("1100x700")
        self.root.minsize(900, 500)
        
        # Load settings
        self.settings = self.load_settings()
        
        # Multi-column sort state: list of (column, reverse) tuples
        # First element is primary sort, subsequent are secondary, tertiary, etc.
        self.sort_columns: List[Tuple[str, bool]] = []
        
        # Store file data for filtering/sorting
        self.file_data: List[Dict[str, Any]] = []
        
        # Load analysis history
        self.history = self.load_history()
        
        self.setup_ui()
        self.load_saved_settings()
        
    def load_settings(self) -> Dict[str, Any]:
        """Load settings from JSON file."""
        try:
            if SETTINGS_FILE.exists():
                with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    return {**DEFAULT_SETTINGS, **settings}
        except (json.JSONDecodeError, IOError):
            pass
        return DEFAULT_SETTINGS.copy()
        
    def save_settings(self):
        """Save current settings to JSON file."""
        settings = {
            "last_folder": self.folder_path_var.get(),
            "filter_extensions": self.filter_extensions_var.get(),
            "filter_exclude": self.filter_exclude_var.get(),
            "exclude_folders": self.exclude_folders_var.get(),
            "include_subfolders": self.include_subfolders_var.get(),
            "sort_columns": self.sort_columns
        }
        try:
            with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save settings: {e}")
            
    def load_saved_settings(self):
        """Load saved settings into UI."""
        if self.settings.get("last_folder"):
            self.folder_path_var.set(self.settings["last_folder"])
        if self.settings.get("filter_extensions"):
            self.filter_extensions_var.set(self.settings["filter_extensions"])
        if self.settings.get("filter_exclude"):
            self.filter_exclude_var.set(self.settings["filter_exclude"])
        if self.settings.get("exclude_folders"):
            self.exclude_folders_var.set(self.settings["exclude_folders"])
        if "include_subfolders" in self.settings:
            self.include_subfolders_var.set(self.settings["include_subfolders"])
        if self.settings.get("sort_columns"):
            self.sort_columns = [tuple(col) for col in self.settings["sort_columns"]]
            
    def load_history(self) -> Dict[str, Any]:
        """Load analysis history from JSON file."""
        try:
            if HISTORY_FILE.exists():
                with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
        return DEFAULT_HISTORY.copy()
        
    def save_history(self):
        """Save current analysis history to JSON file."""
        try:
            with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save history: {e}")
            
    def add_to_history(self, folder_path: str, total_files: int, total_lines: int, total_size: int, file_data: List[Dict[str, Any]]):
        """Add current analysis to history."""
        analysis_entry = {
            "timestamp": datetime.now().isoformat(),
            "folder": folder_path,
            "total_files": total_files,
            "total_lines": total_lines,
            "total_size": total_size,
            "file_data": file_data
        }
        
        # Add to history (keep last 50 analyses)
        self.history["analyses"].append(analysis_entry)
        if len(self.history["analyses"]) > 50:
            self.history["analyses"] = self.history["analyses"][-50:]
            
        self.save_history()
        
    def setup_ui(self):
        """Setup the user interface components."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Top frame for folder selection
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Folder selection
        ttk.Label(top_frame, text="Folder:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.folder_path_var = tk.StringVar()
        folder_entry = ttk.Entry(top_frame, textvariable=self.folder_path_var, width=60)
        folder_entry.pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
        
        browse_btn = ttk.Button(top_frame, text="Browse...", command=self.browse_folder)
        browse_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        analyze_btn = ttk.Button(top_frame, text="Analyze", command=self.analyze_files)
        analyze_btn.pack(side=tk.LEFT)
        
        # Filter frame
        filter_frame = ttk.LabelFrame(main_frame, text="Filters", padding="5")
        filter_frame.pack(fill=tk.X, pady=(5, 5))
        
        # Row 1: Extensions
        filter_row1 = ttk.Frame(filter_frame)
        filter_row1.pack(fill=tk.X, pady=2)
        
        ttk.Label(filter_row1, text="Include extensions:").pack(side=tk.LEFT, padx=(0, 5))
        self.filter_extensions_var = tk.StringVar()
        extensions_entry = ttk.Entry(filter_row1, textvariable=self.filter_extensions_var, width=30)
        extensions_entry.pack(side=tk.LEFT, padx=(0, 5))
        ttk.Label(filter_row1, text="(e.g., .py,.txt,.md - leave empty for all)").pack(side=tk.LEFT)
        
        # Row 2: Exclude patterns
        filter_row2 = ttk.Frame(filter_frame)
        filter_row2.pack(fill=tk.X, pady=2)
        
        ttk.Label(filter_row2, text="Exclude file patterns:").pack(side=tk.LEFT, padx=(0, 5))
        self.filter_exclude_var = tk.StringVar()
        exclude_entry = ttk.Entry(filter_row2, textvariable=self.filter_exclude_var, width=30)
        exclude_entry.pack(side=tk.LEFT, padx=(0, 5))
        ttk.Label(filter_row2, text="(e.g., *.log,temp* - file name patterns to exclude)").pack(side=tk.LEFT)
        
        # Row 3: Exclude folders
        filter_row3 = ttk.Frame(filter_frame)
        filter_row3.pack(fill=tk.X, pady=2)
        
        ttk.Label(filter_row3, text="Exclude folders:").pack(side=tk.LEFT, padx=(0, 5))
        self.exclude_folders_var = tk.StringVar()
        exclude_folders_entry = ttk.Entry(filter_row3, textvariable=self.exclude_folders_var, width=30)
        exclude_folders_entry.pack(side=tk.LEFT, padx=(0, 5))
        ttk.Label(filter_row3, text="(e.g., node_modules,.git,__pycache__,venv - folders to skip)").pack(side=tk.LEFT)
        
        # Row 4: Options
        filter_row4 = ttk.Frame(filter_frame)
        filter_row4.pack(fill=tk.X, pady=2)
        
        self.include_subfolders_var = tk.BooleanVar(value=True)
        subfolders_check = ttk.Checkbutton(filter_row4, text="Include subfolders", variable=self.include_subfolders_var)
        subfolders_check.pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Label(filter_row4, text="Sort hint: Click column header to sort, Shift+Click for multi-column sort").pack(side=tk.LEFT)
        
        # Status label
        self.status_var = tk.StringVar(value="Select a folder to analyze")
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.pack(fill=tk.X, pady=(5, 5))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
        
        # Treeview for file information
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview with scrollbars
        columns = ("name", "path", "lines", "size", "extension")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")
        
        # Define column headings with sort functionality
        self.tree.heading("name", text="Name", anchor=tk.W, command=lambda: self.sort_column("name"))
        self.tree.heading("path", text="Path", anchor=tk.W, command=lambda: self.sort_column("path"))
        self.tree.heading("lines", text="Lines", anchor=tk.E, command=lambda: self.sort_column("lines"))
        self.tree.heading("size", text="Size (bytes)", anchor=tk.E, command=lambda: self.sort_column("size"))
        self.tree.heading("extension", text="Extension", anchor=tk.W, command=lambda: self.sort_column("extension"))
        
        # Set column widths
        self.tree.column("name", width=200, minwidth=100)
        self.tree.column("path", width=350, minwidth=150)
        self.tree.column("lines", width=80, minwidth=50, anchor=tk.E)
        self.tree.column("size", width=100, minwidth=80, anchor=tk.E)
        self.tree.column("extension", width=80, minwidth=50)
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid layout for treeview and scrollbars
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Bind keyboard events for sorting
        self.tree.bind("<Button-1>", self.on_tree_click)
        # Bind double click for chart
        self.tree.bind("<Double-1>", self.on_double_click)
        
        # Bottom frame for summary
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.summary_var = tk.StringVar(value="")
        summary_label = ttk.Label(bottom_frame, textvariable=self.summary_var)
        summary_label.pack(side=tk.LEFT)
        
        # Buttons
        btn_frame = ttk.Frame(bottom_frame)
        btn_frame.pack(side=tk.RIGHT)
        
        clear_sort_btn = ttk.Button(btn_frame, text="Clear Sort", command=self.clear_sort)
        clear_sort_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        export_btn = ttk.Button(btn_frame, text="Export to CSV", command=self.export_to_csv)
        export_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        history_btn = ttk.Button(btn_frame, text="View History", command=self.show_history_window)
        history_btn.pack(side=tk.LEFT)
        
        # Save settings on close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
    def on_tree_click(self, event):
        """Handle click on tree to detect Shift key for multi-column sort."""
        region = self.tree.identify("region", event.x, event.y)
        if region == "heading":
            column = self.tree.identify_column(event.x)
            if column:
                col_name = self.tree.column(column, "id")
                self.sort_column(col_name, shift_pressed=(event.state & 0x1) != 0)
                return "break"  # Prevent default handling
        return None
        
    def on_double_click(self, event):
        """Handle double click on tree to show chart."""
        region = self.tree.identify("region", event.x, event.y)
        if region == "cell":
            item = self.tree.identify_row(event.y)
            if item:
                self.show_chart_for_selected_file(item)
        
    def on_close(self):
        """Handle window close - save settings."""
        self.save_settings()
        self.root.destroy()
        
    def browse_folder(self):
        """Open folder selection dialog."""
        initial_dir = self.folder_path_var.get() or None
        folder = filedialog.askdirectory(title="Select Folder to Analyze", initialdir=initial_dir)
        if folder:
            self.folder_path_var.set(folder)
            
    def clear_sort(self):
        """Clear all sort columns."""
        self.sort_columns = []
        self.update_sort_indicators()
        # Re-display data in original order
        self.display_filtered_data()
        
    def get_filter_patterns(self) -> Tuple[List[str], List[str], List[str]]:
        """Parse filter patterns from UI."""
        # Parse include extensions
        extensions_text = self.filter_extensions_var.get().strip()
        include_extensions = []
        if extensions_text:
            include_extensions = [ext.strip().lower() for ext in extensions_text.split(',') if ext.strip()]
            # Ensure all start with dot
            include_extensions = [ext if ext.startswith('.') else f'.{ext}' for ext in include_extensions]
            
        # Parse exclude patterns
        exclude_text = self.filter_exclude_var.get().strip()
        exclude_patterns = []
        if exclude_text:
            exclude_patterns = [p.strip().lower() for p in exclude_text.split(',') if p.strip()]
            
        # Parse exclude folders
        exclude_folders_text = self.exclude_folders_var.get().strip()
        exclude_folders = []
        if exclude_folders_text:
            exclude_folders = [f.strip().lower() for f in exclude_folders_text.split(',') if f.strip()]
            
        return include_extensions, exclude_patterns, exclude_folders
        
    def should_skip_folder(self, folder_path: str, exclude_folders: List[str]) -> bool:
        """Check if a folder should be skipped during traversal."""
        folder_name = os.path.basename(folder_path).lower()
        return folder_name in exclude_folders
        
    def should_include_file(self, file_path: str, include_extensions: List[str], exclude_patterns: List[str]) -> bool:
        """Check if a file should be included based on filters."""
        path = Path(file_path)
        file_name = path.name.lower()
        file_ext = path.suffix.lower() if path.suffix else "no extension"
        
        # Check exclude patterns
        for pattern in exclude_patterns:
            # Simple wildcard matching for *.ext patterns
            if pattern.startswith('*.'):
                if file_ext == pattern[1:].lower():
                    return False
            elif pattern in file_name:
                return False
                    
        # Check include extensions
        if include_extensions:
            if file_ext not in include_extensions:
                return False
                
        return True
        
    def count_lines(self, file_path: str) -> int:
        """Count the number of lines in a file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return sum(1 for _ in f)
        except (IOError, OSError, PermissionError):
            return -1  # Indicates error reading file
            
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get information about a single file."""
        path = Path(file_path)
        try:
            size = path.stat().st_size
        except (OSError, PermissionError):
            size = -1
            
        lines = self.count_lines(file_path)
        extension = path.suffix.lower() if path.suffix else "no extension"
        
        return {
            "name": path.name,
            "path": str(path.parent),
            "lines": lines,
            "size": size,
            "extension": extension
        }
        
    def analyze_files(self):
        """Analyze all files in the selected folder."""
        folder = self.folder_path_var.get()
        
        if not folder:
            messagebox.showwarning("Warning", "Please select a folder first.")
            return
            
        if not os.path.isdir(folder):
            messagebox.showerror("Error", "Selected path is not a valid folder.")
            return
            
        # Save settings
        self.save_settings()
        
        # Clear existing data
        self.file_data = []
        
        # Get filter patterns
        include_extensions, exclude_patterns, exclude_folders = self.get_filter_patterns()
        include_subfolders = self.include_subfolders_var.get()
        
        # Collect all files
        all_files: List[str] = []
        if include_subfolders:
            for root_dir, dirs, files in os.walk(folder):
                # Filter out excluded folders (modifies dirs in-place to skip them)
                dirs[:] = [d for d in dirs if not self.should_skip_folder(os.path.join(root_dir, d), exclude_folders)]
                
                for file in files:
                    file_path = os.path.join(root_dir, file)
                    if self.should_include_file(file_path, include_extensions, exclude_patterns):
                        all_files.append(file_path)
        else:
            for item in os.listdir(folder):
                item_path = os.path.join(folder, item)
                if os.path.isfile(item_path):
                    if self.should_include_file(item_path, include_extensions, exclude_patterns):
                        all_files.append(item_path)
                
        total_files = len(all_files)
        if total_files == 0:
            self.status_var.set("No files found matching the criteria.")
            self.tree.delete(*self.tree.get_children())
            self.summary_var.set("Total: 0 files")
            return
            
        self.status_var.set(f"Analyzing {total_files} files...")
        self.progress_var.set(0)
        
        # Analyze files
        total_lines = 0
        total_size = 0
        
        for i, file_path in enumerate(all_files):
            info = self.get_file_info(file_path)
            self.file_data.append(info)
            
            if info["lines"] >= 0:
                total_lines += info["lines"]
            if info["size"] >= 0:
                total_size += info["size"]
                
            # Update progress
            progress = ((i + 1) / total_files) * 100
            self.progress_var.set(progress)
            self.root.update_idletasks()
            
        # Display data
        self.display_filtered_data()
        
        # Save to history
        self.add_to_history(folder, total_files, total_lines, total_size, self.file_data)
        
        self.status_var.set(f"Analysis complete. Found {total_files} files.")
        self.summary_var.set(f"Total: {total_files} files | {total_lines:,} lines | {self.format_size(total_size)}")
        
    def display_filtered_data(self):
        """Display file data in the tree, applying current sort."""
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Sort data if needed
        sorted_data = self.file_data.copy()
        if self.sort_columns:
            sorted_data = self.multi_sort_data(sorted_data)
            
        # Insert data
        for info in sorted_data:
            lines_display = str(info["lines"]) if info["lines"] >= 0 else "N/A"
            size_display = str(info["size"]) if info["size"] >= 0 else "N/A"
            
            self.tree.insert("", tk.END, values=(
                info["name"],
                info["path"],
                lines_display,
                size_display,
                info["extension"]
            ))
            
    def multi_sort_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort data by multiple columns."""
        # For multi-column sort with mixed ascending/descending, we need to sort in reverse order
        # Python's sort is stable, so we can sort by each column in reverse order
        result = data.copy()
        for col, reverse in reversed(self.sort_columns):
            def make_key(item, column=col):
                val = item.get(column)
                if column in ("lines", "size"):
                    if val is None or val < 0:
                        return float('inf')
                    return val
                return str(val).lower() if val else ""
            result.sort(key=make_key, reverse=reverse)
            
        return result
        
    def sort_column(self, col: str, shift_pressed: bool = False):
        """Sort tree contents when a column header is clicked."""
        if not self.file_data:
            return
            
        # Check if this column is already in sort list
        existing_index = None
        for i, (c, _) in enumerate(self.sort_columns):
            if c == col:
                existing_index = i
                break
                
        if shift_pressed:
            # Multi-column sort: add or toggle this column
            if existing_index is not None:
                # Toggle direction
                current_reverse = self.sort_columns[existing_index][1]
                self.sort_columns[existing_index] = (col, not current_reverse)
            else:
                # Add new column to sort
                self.sort_columns.append((col, False))
        else:
            # Single column sort: replace all with this column
            if existing_index is not None and len(self.sort_columns) == 1:
                # Toggle if clicking same column
                current_reverse = self.sort_columns[0][1]
                self.sort_columns = [(col, not current_reverse)]
            else:
                # Start new sort with this column
                self.sort_columns = [(col, False)]
                
        self.update_sort_indicators()
        self.display_filtered_data()
        
    def update_sort_indicators(self):
        """Update column heading text to show sort indicators."""
        # Base column names
        base_names = {
            "name": "Name",
            "path": "Path", 
            "lines": "Lines",
            "size": "Size (bytes)",
            "extension": "Extension"
        }
        
        for col in base_names:
            text = base_names[col]
            # Find this column in sort list
            for i, (sort_col, reverse) in enumerate(self.sort_columns):
                if sort_col == col:
                    # Add sort indicator with priority number
                    indicator = "↓" if reverse else "↑"
                    priority = i + 1
                    if len(self.sort_columns) > 1:
                        text = f"{base_names[col]} {indicator}{priority}"
                    else:
                        text = f"{base_names[col]} {indicator}"
                    break
            self.tree.heading(col, text=text)
    
    def format_size(self, size_bytes: float) -> str:
        """Format size in bytes to human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"
        
    def show_chart_for_selected_file(self, item_id: str):
        """Show chart with history for the selected file."""
        values = self.tree.item(item_id, 'values')
        if not values:
            return
            
        file_name = values[0]
        file_path = str(Path(values[1]) / file_name)
        
        # Find all entries in history for this file
        file_history = []
        for i, analysis in enumerate(self.history["analyses"]):
            for file_info in analysis["file_data"]:
                if file_info["path"] == values[1] and file_info["name"] == file_name:
                    file_history.append({
                        "timestamp": analysis["timestamp"],
                        "lines": file_info["lines"],
                        "size": file_info["size"]
                    })
                    break
        
        if not file_history:
            messagebox.showinfo("Info", f"No history data found for {file_name}")
            return
            
        self.show_history_chart(file_name, file_history)
        
    def show_history_chart(self, file_name: str, file_history: List[Dict[str, Any]]):
        """Show a chart with lines and size history for a file."""
        chart_window = tk.Toplevel(self.root)
        chart_window.title(f"File History: {file_name}")
        chart_window.geometry("900x600")
        
        fig, ax1 = plt.subplots(figsize=(10, 6))
        
        # Sort by timestamp
        file_history_sorted = sorted(file_history, key=lambda x: x["timestamp"])
        
        timestamps = [datetime.fromisoformat(h["timestamp"]) for h in file_history_sorted]
        lines = [h["lines"] if h["lines"] >= 0 else 0 for h in file_history_sorted]
        sizes = [h["size"] if h["size"] >= 0 else 0 for h in file_history_sorted]
        
        # Plot lines on left axis
        color1 = 'tab:blue'
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Lines', color=color1, fontweight='bold')
        
        # Plot lines with transparency to show overlapping markers
        line1 = ax1.plot(timestamps, lines, color=color1, marker='o', markersize=12, 
                         label='Lines', linewidth=2, zorder=5, alpha=0.7)
        
        ax1.tick_params(axis='y', labelcolor=color1)
        ax1.grid(True, alpha=0.3)
        
        # Set y-axis limits to ensure data is visible
        if lines:
            min_lines = min(lines)
            max_lines = max(lines)
            if min_lines == max_lines:
                # If all values are the same, set range around them
                margin = max(10, min_lines * 0.1)
                ax1.set_ylim(max(0, min_lines - margin), min_lines + margin)
            else:
                margin = max(1, (max_lines - min_lines) * 0.2)
                ax1.set_ylim(max(0, min_lines - margin), max_lines + margin)
        
        # Create second y-axis for size
        ax2 = ax1.twinx()
        color2 = 'tab:red'
        ax2.set_ylabel('Size (bytes)', color=color2, fontweight='bold')
        
        # Plot sizes with transparency to show overlapping markers
        line2 = ax2.plot(timestamps, sizes, color=color2, marker='s', markersize=12, 
                         label='Size (bytes)', linewidth=2, zorder=4, alpha=0.7)
        
        ax2.tick_params(axis='y', labelcolor=color2)
        
        # Set y-axis limits to ensure data is visible
        if sizes:
            min_sizes = min(sizes)
            max_sizes = max(sizes)
            if min_sizes == max_sizes:
                # If all values are the same, set range around them
                margin = max(10, min_sizes * 0.1)
                ax2.set_ylim(max(0, min_sizes - margin), min_sizes + margin)
            else:
                margin = max(1, (max_sizes - min_sizes) * 0.2)
                ax2.set_ylim(max(0, min_sizes - margin), max_sizes + margin)
        
        # Format x-axis dates
        fig.autofmt_xdate()
        
        # Add title
        plt.title(f'File History: {file_name}', fontweight='bold')
        
        # Add legend
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', framealpha=1.0)
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, master=chart_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add close button
        close_btn = ttk.Button(chart_window, text="Close", command=chart_window.destroy)
        close_btn.pack(pady=10)
        
    def show_history_window(self):
        """Show window with analysis history."""
        history_window = tk.Toplevel(self.root)
        history_window.title("Analysis History")
        history_window.geometry("1000x600")
        
        # Main frame
        main_frame = ttk.Frame(history_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Instructions
        ttk.Label(main_frame, text="Double-click on an analysis to view detailed information").pack(pady=(0, 10))
        
        # Create treeview for history
        columns = ("timestamp", "folder", "files", "lines", "size")
        history_tree = ttk.Treeview(main_frame, columns=columns, show="headings", selectmode="browse")
        
        history_tree.heading("timestamp", text="Date/Time")
        history_tree.heading("folder", text="Folder")
        history_tree.heading("files", text="Files")
        history_tree.heading("lines", text="Lines")
        history_tree.heading("size", text="Size")
        
        history_tree.column("timestamp", width=180)
        history_tree.column("folder", width=400)
        history_tree.column("files", width=80)
        history_tree.column("lines", width=100)
        history_tree.column("size", width=120)
        
        # Scrollbars
        vsb = ttk.Scrollbar(main_frame, orient="vertical", command=history_tree.yview)
        hsb = ttk.Scrollbar(main_frame, orient="horizontal", command=history_tree.xview)
        history_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid layout
        history_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Populate history
        for i, analysis in enumerate(reversed(self.history["analyses"])):
            timestamp_str = datetime.fromisoformat(analysis["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
            history_tree.insert("", tk.END, values=(
                timestamp_str,
                analysis["folder"],
                analysis["total_files"],
                f"{analysis['total_lines']:,}",
                self.format_size(analysis["total_size"])
            ), tags=(str(len(self.history["analyses"]) - 1 - i),))
        
        # Bind double click to show details
        history_tree.bind("<Double-1>", lambda event: self.show_analysis_details(history_window, history_tree))
        
        # Close button
        close_btn = ttk.Button(main_frame, text="Close", command=history_window.destroy)
        close_btn.grid(row=2, column=0, columnspan=2, pady=(10, 0))
        
    def show_analysis_details(self, parent_window: tk.Toplevel, history_tree: ttk.Treeview):
        """Show details for selected analysis."""
        selection = history_tree.selection()
        if not selection:
            return
            
        item = selection[0]
        tags = history_tree.item(item, 'tags')
        if not tags:
            return
            
        index = int(tags[0])
        analysis = self.history["analyses"][index]
        
        # Create details window
        details_window = tk.Toplevel(parent_window)
        details_window.title(f"Analysis Details - {datetime.fromisoformat(analysis['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}")
        details_window.geometry("1100x700")
        
        # Main frame
        main_frame = ttk.Frame(details_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Summary info
        summary_frame = ttk.LabelFrame(main_frame, text="Summary", padding="10")
        summary_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(summary_frame, text=f"Folder: {analysis['folder']}").pack(anchor=tk.W)
        ttk.Label(summary_frame, text=f"Total Files: {analysis['total_files']}").pack(anchor=tk.W)
        ttk.Label(summary_frame, text=f"Total Lines: {analysis['total_lines']:,}").pack(anchor=tk.W)
        ttk.Label(summary_frame, text=f"Total Size: {self.format_size(analysis['total_size'])}").pack(anchor=tk.W)
        
        # Files tree
        files_frame = ttk.LabelFrame(main_frame, text="Files (Double-click for chart)", padding="5")
        files_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("name", "path", "lines", "size", "extension")
        files_tree = ttk.Treeview(files_frame, columns=columns, show="headings", selectmode="browse")
        
        files_tree.heading("name", text="Name", anchor=tk.W)
        files_tree.heading("path", text="Path", anchor=tk.W)
        files_tree.heading("lines", text="Lines", anchor=tk.E)
        files_tree.heading("size", text="Size (bytes)", anchor=tk.E)
        files_tree.heading("extension", text="Extension", anchor=tk.W)
        
        files_tree.column("name", width=200, minwidth=100)
        files_tree.column("path", width=350, minwidth=150)
        files_tree.column("lines", width=80, minwidth=50, anchor=tk.E)
        files_tree.column("size", width=100, minwidth=80, anchor=tk.E)
        files_tree.column("extension", width=80, minwidth=50)
        
        # Scrollbars
        vsb = ttk.Scrollbar(files_frame, orient="vertical", command=files_tree.yview)
        hsb = ttk.Scrollbar(files_frame, orient="horizontal", command=files_tree.xview)
        files_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid layout
        files_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        files_frame.grid_rowconfigure(0, weight=1)
        files_frame.grid_columnconfigure(0, weight=1)
        
        # Populate files
        for file_info in analysis["file_data"]:
            lines_display = str(file_info["lines"]) if file_info["lines"] >= 0 else "N/A"
            size_display = str(file_info["size"]) if file_info["size"] >= 0 else "N/A"
            
            files_tree.insert("", tk.END, values=(
                file_info["name"],
                file_info["path"],
                lines_display,
                size_display,
                file_info["extension"]
            ))
        
        # Bind double click to show chart
        files_tree.bind("<Double-1>", lambda event: self.on_double_click_history(event, files_tree, analysis))
        
        # Close button
        close_btn = ttk.Button(main_frame, text="Close", command=details_window.destroy)
        close_btn.pack(pady=(10, 0))
        
    def on_double_click_history(self, event, files_tree: ttk.Treeview, analysis: Dict[str, Any]):
        """Handle double click on history files tree."""
        region = files_tree.identify("region", event.x, event.y)
        if region == "cell":
            item = files_tree.identify_row(event.y)
            if item:
                values = files_tree.item(item, 'values')
                file_name = values[0]
                file_path = values[1]
                
                # Find all entries in history for this file
                file_history = []
                for hist_analysis in self.history["analyses"]:
                    for file_info in hist_analysis["file_data"]:
                        if file_info["path"] == file_path and file_info["name"] == file_name:
                            file_history.append({
                                "timestamp": hist_analysis["timestamp"],
                                "lines": file_info["lines"],
                                "size": file_info["size"]
                            })
                            break
                
                if not file_history:
                    messagebox.showinfo("Info", f"No history data found for {file_name}")
                    return
                    
                self.show_history_chart(file_name, file_history)
        
    def export_to_csv(self):
        """Export the current data to a CSV file."""
        if not self.tree.get_children():
            messagebox.showwarning("Warning", "No data to export. Please analyze a folder first.")
            return
            
        csv_path = filedialog.asksaveasfilename(
            title="Save CSV File",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if not csv_path:
            return
            
        try:
            with open(csv_path, 'w', encoding='utf-8') as f:
                # Write header
                f.write("Name,Path,Lines,Size (bytes),Extension\n")
                
                # Write data
                for item in self.tree.get_children():
                    values = self.tree.item(item, 'values')
                    # Escape commas in values
                    escaped_values = [str(v).replace(',', '\\,') if ',' in str(v) else str(v) for v in values]
                    f.write(','.join(escaped_values) + '\n')
                    
            messagebox.showinfo("Success", f"Data exported to {csv_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export data: {str(e)}")


def main():
    """Main entry point for the application."""
    root = tk.Tk()
    app = FileAnalyzerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
