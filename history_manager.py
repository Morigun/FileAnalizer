"""
History management for File Analyzer.
"""

import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
from constants import DEFAULT_HISTORY, HISTORY_FILE, MAX_HISTORY_ANALYSES


class HistoryManager:
    """Manages analysis history."""
    
    def __init__(self, settings_dir: Path):
        self.history_file = settings_dir / HISTORY_FILE
        self.history = self._load_history()
    
    def _load_history(self) -> Dict[str, Any]:
        """Load analysis history from JSON file."""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
        return DEFAULT_HISTORY.copy()
    
    def save_history(self) -> bool:
        """Save current history to JSON file."""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2)
            return True
        except IOError as e:
            print(f"Warning: Could not save history: {e}")
            return False
    
    def add_analysis(self, folder_path: str, total_files: int, 
                   total_lines: int, total_size: int, 
                   file_data: List[Dict[str, Any]]) -> bool:
        """Add current analysis to history."""
        analysis_entry = {
            "timestamp": datetime.now().isoformat(),
            "folder": folder_path,
            "total_files": total_files,
            "total_lines": total_lines,
            "total_size": total_size,
            "file_data": file_data
        }
        
        # Add to history
        self.history["analyses"].append(analysis_entry)
        
        # Cleanup old analyses
        self._cleanup_old_analyses()
        
        return self.save_history()
    
    def _cleanup_old_analyses(self, max_count: int = MAX_HISTORY_ANALYSES):
        """Remove old analyses to maintain history size limit."""
        if len(self.history["analyses"]) > max_count:
            self.history["analyses"] = self.history["analyses"][-max_count:]
    
    def get_file_history(self, file_name: str, file_path: str) -> List[Dict[str, Any]]:
        """Get all history entries for a specific file."""
        file_history = []
        
        # Normalize file_path to use forward slashes for comparison
        normalized_search_path = file_path.replace("\\", "/")
        
        for analysis in self.history["analyses"]:
            for file_info in analysis["file_data"]:
                # Normalize stored path for comparison
                stored_path = file_info["path"].replace("\\", "/")
                if stored_path == normalized_search_path and file_info["name"] == file_name:
                    file_history.append({
                        "timestamp": analysis["timestamp"],
                        "lines": file_info["lines"],
                        "size": file_info["size"]
                    })
                    break
        return file_history
    
    def get_analyses(self) -> List[Dict[str, Any]]:
        """Get all analyses (most recent first)."""
        return list(reversed(self.history["analyses"]))
    
    def get_analysis_by_index(self, index: int) -> Dict[str, Any] | None:
        """Get analysis by index from original order (not reversed)."""
        analyses = self.history["analyses"]
        if 0 <= index < len(analyses):
            return analyses[index]
        return None
