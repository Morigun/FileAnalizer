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


# Settings file path
SETTINGS_FILE = Path(__file__).parent / "settings.json"

# Default settings
DEFAULT_SETTINGS = {
    "last_folder": "",
    "filter_extensions": "",
    "filter_exclude": "",
    "exclude_folders": "",
    "include_subfolders": True,
    "sort_columns": []  # List of (column, reverse) tuples for multi-column sort
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
        export_btn.pack(side=tk.LEFT)
        
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
    
    def format_size(self, size_bytes: int) -> str:
        """Format size in bytes to human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"
        
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
