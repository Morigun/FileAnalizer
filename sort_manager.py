"""
Sort management for File Analyzer.
"""

import tkinter as tk
import tkinter.ttk as ttk
from typing import List, Tuple, Dict, Any
from constants import SORT_INDICATORS


class SortManager:
    """Manages multi-column sorting functionality."""
    
    def __init__(self):
        self.sort_columns: List[Tuple[str, bool]] = []
    
    def sort_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort data by multiple columns.
        
        Args:
            data: List of data dictionaries to sort
        
        Returns:
            Sorted list of data
        """
        if not self.sort_columns:
            return data.copy()
        
        # For multi-column sort, sort in reverse order
        # Python's sort is stable, so we can sort by each column in reverse order
        result = data.copy()
        for col, reverse in reversed(self.sort_columns):
            result.sort(key=lambda item, c=col: self._make_sort_key(item, c), reverse=reverse)
        
        return result
    
    def _make_sort_key(self, item: Dict[str, Any], column: str):
        """Create sort key for a given column."""
        val = item.get(column)
        if column in ("lines", "size"):
            if val is None or val < 0:
                return float('inf')
            return val
        return str(val).lower() if val else ""
    
    def toggle_sort_column(self, col: str, shift_pressed: bool = False) -> bool:
        """Toggle sort for a column.
        
        Args:
            col: Column name to sort
            shift_pressed: Whether shift key was pressed (for multi-column sort)
        
        Returns:
            True if sort changed, False otherwise
        """
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
        
        return True
    
    def clear_sort(self) -> None:
        """Clear all sort columns."""
        self.sort_columns = []
    
    def update_sort_indicators(self, tree: ttk.Treeview, base_names: Dict[str, str]) -> None:
        """Update column heading text to show sort indicators.
        
        Args:
            tree: Treeview to update
            base_names: Dictionary mapping column names to base heading text
        """
        for col in base_names:
            text = base_names[col]
            # Find this column in sort list
            for i, (sort_col, reverse) in enumerate(self.sort_columns):
                if sort_col == col:
                    # Add sort indicator with priority number
                    indicator = SORT_INDICATORS["desc"] if reverse else SORT_INDICATORS["asc"]
                    priority = i + 1
                    if len(self.sort_columns) > 1:
                        text = f"{base_names[col]} {indicator}{priority}"
                    else:
                        text = f"{base_names[col]} {indicator}"
                    break
            tree.heading(col, text=text)
