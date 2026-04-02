"""
Main application class for File Analyzer.
Refactored to use separate manager classes.
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from typing import List, Dict, Any, Callable

from constants import (
    WINDOW_GEOMETRY, MAIN_TREE_COLUMNS, MAIN_TREE_HEADINGS,
    MAIN_COLUMN_WIDTHS, HISTORY_TREE_COLUMNS, HISTORY_TREE_HEADINGS,
    HISTORY_COLUMN_WIDTHS, PADDING, UI_LABELS, STATUS_MESSAGES,
    SUMMARY_FORMAT, WINDOW_TITLES
)
from settings_manager import SettingsManager
from history_manager import HistoryManager
from file_scanner import FileAnalyzer
from chart_manager import ChartManager
from treeview_builder import TreeviewBuilder
from data_formatter import DataFormatter
from sort_manager import SortManager


class FileAnalyzerApp:
    """Main application class for File Analyzer."""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(WINDOW_TITLES["main"])
        self.root.geometry(WINDOW_GEOMETRY["main"])
        self.root.minsize(900, 500)
        
        # Initialize managers
        settings_dir = Path(__file__).parent
        self.settings_manager = SettingsManager(settings_dir)
        self.history_manager = HistoryManager(settings_dir)
        self.sort_manager = SortManager()
        self.data_formatter = DataFormatter()
        
        # Load settings
        self.settings = self.settings_manager.load_settings()
        
        # Store file data for filtering/sorting
        self.file_data: List[Dict[str, Any]] = []
        
        # Setup UI components
        self._setup_variables()
        self._setup_ui()
        self._load_saved_settings()
    
    def _setup_variables(self):
        """Setup UI variables."""
        self.folder_path_var = tk.StringVar()
        self.filter_extensions_var = tk.StringVar()
        self.filter_exclude_var = tk.StringVar()
        self.exclude_folders_var = tk.StringVar()
        self.include_subfolders_var = tk.BooleanVar(value=True)
        self.status_var = tk.StringVar(value=STATUS_MESSAGES["initial"])
        self.summary_var = tk.StringVar(value="")
        self.progress_var = tk.DoubleVar()
    
    def _setup_ui(self):
        """Setup the user interface components."""
        main_frame = ttk.Frame(self.root, padding=PADDING["main"])
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Top frame for folder selection
        self._setup_top_panel(main_frame)
        
        # Filter frame
        self._setup_filters_panel(main_frame)
        
        # Status and progress
        self._setup_status_panel(main_frame)
        
        # Treeview for file information
        self._setup_treeview(main_frame)
        
        # Bottom frame for summary and buttons
        self._setup_bottom_panel(main_frame)
        
        # Save settings on close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def _setup_top_panel(self, parent: ttk.Frame):
        """Setup top panel with folder selection."""
        top_frame = ttk.Frame(parent)
        top_frame.pack(fill=tk.X, pady=PADDING["vertical"])
        
        ttk.Label(top_frame, text=UI_LABELS["folder"]).pack(side=tk.LEFT, padx=PADDING["left"])
        
        folder_entry = ttk.Entry(top_frame, textvariable=self.folder_path_var, width=60)
        folder_entry.pack(side=tk.LEFT, padx=PADDING["horizontal"], fill=tk.X, expand=True)
        
        browse_btn = ttk.Button(top_frame, text=UI_LABELS["browse"], command=self.browse_folder)
        browse_btn.pack(side=tk.LEFT, padx=PADDING["button"])
        
        analyze_btn = ttk.Button(top_frame, text=UI_LABELS["analyze"], command=self.analyze_files)
        analyze_btn.pack(side=tk.LEFT)
    
    def _setup_filters_panel(self, parent: ttk.Frame):
        """Setup filters panel."""
        filter_frame = ttk.LabelFrame(parent, text=UI_LABELS["filters"], padding=PADDING["label_frame"])
        filter_frame.pack(fill=tk.X, pady=PADDING["vertical"])
        
        # Row 1: Extensions
        filter_row1 = ttk.Frame(filter_frame)
        filter_row1.pack(fill=tk.X, pady=2)
        
        ttk.Label(filter_row1, text=UI_LABELS["include_extensions"]).pack(side=tk.LEFT, padx=PADDING["left"])
        extensions_entry = ttk.Entry(filter_row1, textvariable=self.filter_extensions_var, width=30)
        extensions_entry.pack(side=tk.LEFT, padx=PADDING["horizontal"])
        ttk.Label(filter_row1, text=UI_LABELS["include_extensions_hint"]).pack(side=tk.LEFT)
        
        # Row 2: Exclude patterns
        filter_row2 = ttk.Frame(filter_frame)
        filter_row2.pack(fill=tk.X, pady=2)
        
        ttk.Label(filter_row2, text=UI_LABELS["exclude_patterns"]).pack(side=tk.LEFT, padx=PADDING["left"])
        exclude_entry = ttk.Entry(filter_row2, textvariable=self.filter_exclude_var, width=30)
        exclude_entry.pack(side=tk.LEFT, padx=PADDING["horizontal"])
        ttk.Label(filter_row2, text=UI_LABELS["exclude_patterns_hint"]).pack(side=tk.LEFT)
        
        # Row 3: Exclude folders
        filter_row3 = ttk.Frame(filter_frame)
        filter_row3.pack(fill=tk.X, pady=2)
        
        ttk.Label(filter_row3, text=UI_LABELS["exclude_folders"]).pack(side=tk.LEFT, padx=PADDING["left"])
        exclude_folders_entry = ttk.Entry(filter_row3, textvariable=self.exclude_folders_var, width=30)
        exclude_folders_entry.pack(side=tk.LEFT, padx=PADDING["horizontal"])
        ttk.Label(filter_row3, text=UI_LABELS["exclude_folders_hint"]).pack(side=tk.LEFT)
        
        # Row 4: Options
        filter_row4 = ttk.Frame(filter_frame)
        filter_row4.pack(fill=tk.X, pady=2)
        
        subfolders_check = ttk.Checkbutton(filter_row4, text=UI_LABELS["include_subfolders"], 
                                       variable=self.include_subfolders_var)
        subfolders_check.pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Label(filter_row4, text=UI_LABELS["sort_hint"]).pack(side=tk.LEFT)
    
    def _setup_status_panel(self, parent: ttk.Frame):
        """Setup status and progress bar."""
        status_label = ttk.Label(parent, textvariable=self.status_var)
        status_label.pack(fill=tk.X, pady=PADDING["vertical"])
        
        progress_bar = ttk.Progressbar(parent, variable=self.progress_var, maximum=100)
        progress_bar.pack(fill=tk.X, pady=(0, 10))
    
    def _setup_treeview(self, parent: ttk.Frame):
        """Setup main treeview for file information."""
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview
        self.tree = TreeviewBuilder.create_scrolled_tree(
            tree_frame,
            MAIN_TREE_COLUMNS,
            MAIN_TREE_HEADINGS,
            MAIN_COLUMN_WIDTHS
        )
        
        # Setup sort handlers
        def on_sort(col: str, shift_pressed: bool = False):
            if self.file_data and self.sort_manager.toggle_sort_column(col, shift_pressed):
                self._update_sort_indicators()
                self._display_filtered_data()
        
        TreeviewBuilder.setup_sortable_tree(self.tree, on_sort)
        
        # Bind keyboard events
        self.tree.bind("<Button-1>", self._on_tree_click)
        self.tree.bind("<Double-1>", self.on_double_click)
    
    def _setup_bottom_panel(self, parent: ttk.Frame):
        """Setup bottom panel with summary and buttons."""
        bottom_frame = ttk.Frame(parent)
        bottom_frame.pack(fill=tk.X, pady=(10, 0))
        
        summary_label = ttk.Label(bottom_frame, textvariable=self.summary_var)
        summary_label.pack(side=tk.LEFT)
        
        btn_frame = ttk.Frame(bottom_frame)
        btn_frame.pack(side=tk.RIGHT)
        
        clear_sort_btn = ttk.Button(btn_frame, text=UI_LABELS["clear_sort"], command=self.clear_sort)
        clear_sort_btn.pack(side=tk.LEFT, padx=PADDING["button"])
        
        export_btn = ttk.Button(btn_frame, text=UI_LABELS["export_csv"], command=self.export_to_csv)
        export_btn.pack(side=tk.LEFT, padx=PADDING["button"])
        
        history_btn = ttk.Button(btn_frame, text=UI_LABELS["view_history"], command=self.show_history_window)
        history_btn.pack(side=tk.LEFT)
    
    def _load_saved_settings(self):
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
            self.sort_manager.sort_columns = [tuple(col) for col in self.settings["sort_columns"]]
            self._update_sort_indicators()
    
    def _save_settings(self):
        """Save current settings."""
        settings = {
            "last_folder": self.folder_path_var.get(),
            "filter_extensions": self.filter_extensions_var.get(),
            "filter_exclude": self.filter_exclude_var.get(),
            "exclude_folders": self.exclude_folders_var.get(),
            "include_subfolders": self.include_subfolders_var.get(),
            "sort_columns": self.sort_manager.sort_columns
        }
        self.settings_manager.save_settings(settings)
    
    def _on_tree_click(self, event):
        """Handle click on tree to detect Shift key for multi-column sort."""
        region = self.tree.identify("region", event.x, event.y)
        if region == "heading":
            column = self.tree.identify_column(event.x)
            if column:
                col_name = self.tree.column(column, "id")
                if self.file_data and self.sort_manager.toggle_sort_column(col_name, 
                                                                    shift_pressed=(event.state & 0x1) != 0):
                    self._update_sort_indicators()
                    self._display_filtered_data()
                return "break"
        return None
    
    def on_double_click(self, event):
        """Handle double click on tree to show chart."""
        region = self.tree.identify("region", event.x, event.y)
        if region == "cell":
            item = self.tree.identify_row(event.y)
            if item:
                self._show_chart_for_selected_file(item)
    
    def on_close(self):
        """Handle window close - save settings."""
        self._save_settings()
        self.root.destroy()
    
    def browse_folder(self):
        """Open folder selection dialog."""
        initial_dir = self.folder_path_var.get() or None
        folder = filedialog.askdirectory(title="Select Folder to Analyze", initialdir=initial_dir)
        if folder:
            self.folder_path_var.set(folder)
    
    def clear_sort(self):
        """Clear all sort columns."""
        self.sort_manager.clear_sort()
        self._update_sort_indicators()
        self._display_filtered_data()
    
    def analyze_files(self):
        """Analyze all files in the selected folder."""
        folder = self.folder_path_var.get()
        
        if not folder:
            messagebox.showwarning("Warning", STATUS_MESSAGES["no_folder"])
            return
        
        if not os.path.isdir(folder):
            messagebox.showerror("Error", STATUS_MESSAGES["invalid_folder"])
            return
        
        # Save settings
        self._save_settings()
        
        # Clear existing data
        self.file_data = []
        
        # Get filter patterns
        include_extensions = FileAnalyzer.parse_extensions(self.filter_extensions_var.get())
        exclude_patterns = FileAnalyzer.parse_filter_patterns(self.filter_exclude_var.get())
        exclude_folders = FileAnalyzer.parse_filter_patterns(self.exclude_folders_var.get())
        include_subfolders = self.include_subfolders_var.get()
        
        # Scan directory
        all_files = FileAnalyzer.scan_directory(folder, include_subfolders, exclude_folders)
        
        # Filter files
        filtered_files = FileAnalyzer.filter_files(all_files, include_extensions, exclude_patterns)
        
        total_files = len(filtered_files)
        if total_files == 0:
            self.status_var.set(STATUS_MESSAGES["no_files"])
            TreeviewBuilder.populate_tree(self.tree, [])
            self.summary_var.set("Total: 0 files")
            return
        
        self.status_var.set(STATUS_MESSAGES["analyzing"].format(total_files))
        self.progress_var.set(0)
        
        # Analyze files
        total_lines = 0
        total_size = 0
        
        for i, file_path in enumerate(filtered_files):
            info = FileAnalyzer.get_file_info(file_path)
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
        self._display_filtered_data()
        
        # Save to history
        self.history_manager.add_analysis(folder, total_files, total_lines, total_size, self.file_data)
        
        self.status_var.set(STATUS_MESSAGES["complete"].format(total_files))
        self.summary_var.set(SUMMARY_FORMAT.format(
            total_files,
            total_lines,
            self.data_formatter.format_size(total_size)
        ))
    
    def _display_filtered_data(self):
        """Display file data in the tree, applying current sort."""
        sorted_data = self.sort_manager.sort_data(self.file_data)
        TreeviewBuilder.populate_tree(
            self.tree,
            sorted_data,
            formatter=self.data_formatter.format_file_info
        )
    
    def _update_sort_indicators(self):
        """Update column heading text to show sort indicators."""
        self.sort_manager.update_sort_indicators(self.tree, MAIN_TREE_HEADINGS)
    
    def _show_chart_for_selected_file(self, item_id: str):
        """Show chart with history for selected file."""
        values = self.tree.item(item_id, 'values')
        if not values:
            return
        
        file_name = values[0]
        folder_path = values[1]
        
        # Get file history - use folder_path only, not full file path
        file_history = self.history_manager.get_file_history(file_name, folder_path)
        
        if not file_history:
            messagebox.showinfo("Info", STATUS_MESSAGES["no_history"].format(file_name))
            return
        
        ChartManager.create_history_chart(self.root, file_name, file_history)
    
    def show_history_window(self):
        """Show window with analysis history."""
        history_window = tk.Toplevel(self.root)
        history_window.title(WINDOW_TITLES["history"])
        history_window.geometry(WINDOW_GEOMETRY["history"])
        
        main_frame = ttk.Frame(history_window, padding=PADDING["main"])
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Instructions
        ttk.Label(main_frame, text=UI_LABELS["history_hint"]).pack(pady=(0, 10))
        
        # Create treeview for history
        history_tree = TreeviewBuilder.create_scrolled_tree(
            main_frame,
            HISTORY_TREE_COLUMNS,
            HISTORY_TREE_HEADINGS,
            HISTORY_COLUMN_WIDTHS
        )
        
        # Populate history
        analyses = self.history_manager.get_analyses()
        for i, analysis in enumerate(analyses):
            # Get original index
            original_index = len(analyses) - 1 - i
            timestamp_str = self.data_formatter.format_timestamp(analysis["timestamp"])
            
            history_tree.insert("", tk.END, values=(
                timestamp_str,
                analysis["folder"],
                analysis["total_files"],
                self.data_formatter.format_number(analysis["total_lines"]),
                self.data_formatter.format_size(analysis["total_size"])
            ), tags=(str(original_index),))
        
        # Bind double click to show details
        history_tree.bind("<Double-1>", lambda e: self._show_analysis_details(history_window, history_tree))
        
        # Close button
        close_btn = ttk.Button(main_frame, text=UI_LABELS["close"], command=history_window.destroy)
        close_btn.grid(row=2, column=0, columnspan=2, pady=(10, 0))
    
    def _show_analysis_details(self, parent_window: tk.Toplevel, history_tree: ttk.Treeview):
        """Show details for selected analysis."""
        selection = history_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        tags = history_tree.item(item, 'tags')
        if not tags:
            return
        
        index = int(tags[0])
        analysis = self.history_manager.get_analysis_by_index(index)
        if not analysis:
            return
        
        # Create details window
        details_window = tk.Toplevel(parent_window)
        title = WINDOW_TITLES["details"].format(
            self.data_formatter.format_timestamp(analysis["timestamp"])
        )
        details_window.title(title)
        details_window.geometry(WINDOW_GEOMETRY["details"])
        
        main_frame = ttk.Frame(details_window, padding=PADDING["main"])
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Summary info
        summary_frame = ttk.LabelFrame(main_frame, text=UI_LABELS["summary"], padding=PADDING["label_frame"])
        summary_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(summary_frame, text=f"Folder: {analysis['folder']}").pack(anchor=tk.W)
        ttk.Label(summary_frame, text=f"Total Files: {analysis['total_files']}").pack(anchor=tk.W)
        ttk.Label(summary_frame, text=f"Total Lines: {self.data_formatter.format_number(analysis['total_lines'])}").pack(anchor=tk.W)
        ttk.Label(summary_frame, text=f"Total Size: {self.data_formatter.format_size(analysis['total_size'])}").pack(anchor=tk.W)
        
        # Files tree
        files_frame = ttk.LabelFrame(main_frame, text=UI_LABELS["files"], padding=PADDING["label_frame"])
        files_frame.pack(fill=tk.BOTH, expand=True)
        
        files_tree = TreeviewBuilder.create_scrolled_tree(
            files_frame,
            MAIN_TREE_COLUMNS,
            MAIN_TREE_HEADINGS,
            MAIN_COLUMN_WIDTHS
        )
        
        # Populate files
        TreeviewBuilder.populate_tree(
            files_tree,
            analysis["file_data"],
            formatter=self.data_formatter.format_file_info
        )
        
        # Bind double click to show chart
        files_tree.bind("<Double-1>", lambda e: self._on_double_click_history(e, files_tree, analysis))
        
        # Close button
        close_btn = ttk.Button(main_frame, text=UI_LABELS["close"], command=details_window.destroy)
        close_btn.pack(pady=(10, 0))
    
    def _on_double_click_history(self, event, files_tree: ttk.Treeview, analysis: Dict[str, Any]):
        """Handle double click on history files tree."""
        region = files_tree.identify("region", event.x, event.y)
        if region == "cell":
            item = files_tree.identify_row(event.y)
            if item:
                values = files_tree.item(item, 'values')
                file_name = values[0]
                file_path = values[1]
                
                # Get file history
                file_history = self.history_manager.get_file_history(file_name, file_path)
                
                if not file_history:
                    messagebox.showinfo("Info", STATUS_MESSAGES["no_history"].format(file_name))
                    return
                
                ChartManager.create_history_chart(self.root, file_name, file_history)
    
    def export_to_csv(self):
        """Export current data to a CSV file."""
        if not self.tree.get_children():
            messagebox.showwarning("Warning", STATUS_MESSAGES["no_data_export"])
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
                    escaped_values = [str(v).replace(',', '\\,') if ',' in str(v) else str(v) for v in values]
                    f.write(','.join(escaped_values) + '\n')
            
            messagebox.showinfo("Success", STATUS_MESSAGES["export_success"].format(csv_path))
        except Exception as e:
            messagebox.showerror("Error", STATUS_MESSAGES["export_failed"].format(str(e)))
