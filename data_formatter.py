"""
Data formatting utilities for File Analyzer.
"""

from typing import Any, Dict
from constants import ERROR_VALUE


class DataFormatter:
    """Handles formatting of data for display."""
    
    @staticmethod
    def format_lines(lines: int) -> str:
        """Format lines count for display."""
        return str(lines) if lines >= 0 else ERROR_VALUE
    
    @staticmethod
    def format_size(size: int) -> str:
        """Format size in bytes to human readable format."""
        if size < 0:
            return ERROR_VALUE
        
        size_bytes = float(size)
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"
    
    @staticmethod
    def format_file_info(file_info: Dict[str, Any]) -> tuple:
        """Format file info for treeview display."""
        lines_display = DataFormatter.format_lines(file_info.get("lines", -1))
        size_display = DataFormatter.format_size(file_info.get("size", -1))
        
        return (
            file_info.get("name", ""),
            file_info.get("path", ""),
            lines_display,
            size_display,
            file_info.get("extension", "")
        )
    
    @staticmethod
    def format_timestamp(timestamp: str) -> str:
        """Format ISO timestamp for display."""
        from datetime import datetime
        try:
            dt = datetime.fromisoformat(timestamp)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            return timestamp
    
    @staticmethod
    def format_number(number: int) -> str:
        """Format number with thousands separator."""
        return f"{number:,}"
