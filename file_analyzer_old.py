"""
File analysis utilities for File Analyzer.
"""

import os
from pathlib import Path
from typing import List, Tuple, Dict, Any
from data_formatter import DataFormatter


class FileAnalyzer:
    """Handles file scanning and analysis operations."""
    
    @staticmethod
    def scan_directory(folder: str, include_subfolders: bool, 
                     exclude_folders: List[str]) -> List[str]:
        """Scan directory for files."""
        all_files: List[str] = []
        
        if include_subfolders:
            for root_dir, dirs, files in os.walk(folder):
                # Filter out excluded folders (modifies dirs in-place to skip them)
                dirs[:] = [d for d in dirs if not FileAnalyzer._should_skip_folder(
                    os.path.join(root_dir, d), exclude_folders
                )]
                
                for file in files:
                    file_path = os.path.join(root_dir, file)
                    all_files.append(file_path)
        else:
            for item in os.listdir(folder):
                item_path = os.path.join(folder, item)
                if os.path.isfile(item_path):
                    all_files.append(item_path)
        
        return all_files
    
    @staticmethod
    def _should_skip_folder(folder_path: str, exclude_folders: List[str]) -> bool:
        """Check if a folder should be skipped during traversal."""
        folder_name = os.path.basename(folder_path).lower()
        return folder_name in exclude_folders
    
    @staticmethod
    def filter_files(files: List[str], include_extensions: List[str], 
                   exclude_patterns: List[str]) -> List[str]:
        """Filter files based on extensions and patterns."""
        filtered_files = []
        for file_path in files:
            if FileAnalyzer._should_include_file(file_path, include_extensions, exclude_patterns):
                filtered_files.append(file_path)
        return filtered_files
    
    @staticmethod
    def _should_include_file(file_path: str, include_extensions: List[str], 
                           exclude_patterns: List[str]) -> bool:
        """Check if a file should be included based on filters."""
        path = Path(file_path)
        file_name = path.name.lower()
        file_ext = path.suffix.lower() if path.suffix else "no extension"
        
        # Check exclude patterns
        for pattern in exclude_patterns:
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
    
    @staticmethod
    def count_lines(file_path: str) -> int:
        """Count the number of lines in a file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return sum(1 for _ in f)
        except (IOError, OSError, PermissionError):
            return -1  # Indicates error reading file
    
    @staticmethod
    def get_file_info(file_path: str) -> Dict[str, Any]:
        """Get information about a single file."""
        path = Path(file_path)
        try:
            size = path.stat().st_size
        except (OSError, PermissionError):
            size = -1
        
        lines = FileAnalyzer.count_lines(file_path)
        extension = path.suffix.lower() if path.suffix else "no extension"
        
        return {
            "name": path.name,
            "path": str(path.parent),
            "lines": lines,
            "size": size,
            "extension": extension
        }
    
    @staticmethod
    def parse_filter_patterns(filter_text: str) -> List[str]:
        """Parse comma-separated filter patterns."""
        if not filter_text:
            return []
        return [p.strip().lower() for p in filter_text.split(',') if p.strip()]
    
    @staticmethod
    def parse_extensions(extensions_text: str) -> List[str]:
        """Parse comma-separated file extensions."""
        if not extensions_text:
            return []
        extensions = [ext.strip().lower() for ext in extensions_text.split(',') if ext.strip()]
        # Ensure all start with dot
        return [ext if ext.startswith('.') else f'.{ext}' for ext in extensions]
