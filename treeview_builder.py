"""
Treeview builder utilities for File Analyzer.
"""

import tkinter as tk
import tkinter.ttk as ttk
from typing import List, Dict, Any, Tuple, Callable, Optional, Literal


class TreeviewBuilder:
    """Builder for creating consistent Treeview widgets."""
    
    @staticmethod
    def create_scrolled_tree(parent: tk.Widget, columns: tuple, headings: Dict[str, str], 
                          widths: Dict[str, Tuple[int, int]] | None = None,
                          selectmode: Literal['extended', 'browse', 'none'] = 'browse') -> ttk.Treeview:
        """Create a Treeview with scrollbars.
        
        Args:
            parent: Parent widget
            columns: Tuple of column names
            headings: Dictionary mapping column names to heading text
            widths: Dictionary mapping column names to (width, minwidth) tuples
            selectmode: Selection mode for the tree
        
        Returns:
            Configured Treeview widget
        """
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview
        tree = ttk.Treeview(frame, columns=columns, show="headings", selectmode=selectmode)
        
        # Set headings
        for col in columns:
            anchor = tk.W if col not in ("lines", "size") else tk.E
            tree.heading(col, text=headings.get(col, col), anchor=anchor)
        
        # Set column widths
        if widths:
            for col in columns:
                if col in widths:
                    width, minwidth = widths[col]
                    anchor = tk.E if col in ("lines", "size") else tk.W
                    tree.column(col, width=width, minwidth=minwidth, anchor=anchor)
        
        # Create scrollbars
        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid layout
        tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        return tree
    
    @staticmethod
    def populate_tree(tree: ttk.Treeview, data: List[Dict[str, Any]], 
                   formatter: Optional[Callable] = None, tags: List[str] | None = None) -> None:
        """Populate tree with data.
        
        Args:
            tree: Treeview to populate
            data: List of data dictionaries
            formatter: Optional function to format data for display
            tags: Optional tags to apply to all items
        """
        # Clear existing data
        for item in tree.get_children():
            tree.delete(item)
        
        # Insert data
        for item_data in data:
            if formatter:
                values = formatter(item_data)
            else:
                values = tuple(item_data.values())
            
            if tags:
                tree.insert("", tk.END, values=values, tags=tags)
            else:
                tree.insert("", tk.END, values=values)
    
    @staticmethod
    def setup_sortable_tree(tree: ttk.Treeview, sort_handler: Callable) -> None:
        """Setup tree for sortable columns.
        
        Args:
            tree: Treeview to configure
            sort_handler: Callback function for sort events (column_name, shift_pressed)
        """
        columns = tree["columns"]
        for col in columns:
            tree.heading(col, command=lambda c=col: sort_handler(c))
