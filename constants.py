"""
Configuration constants for File Analyzer application.
"""

# Window configurations
WINDOW_GEOMETRY = {
    "main": "1100x700",
    "history": "1000x600",
    "details": "1100x700",
    "chart": "900x600"
}

# Window titles
WINDOW_TITLES = {
    "main": "File Analyzer",
    "history": "Analysis History",
    "details": "Analysis Details - {}",
    "chart": "File History: {}"
}

# Treeview column configurations
MAIN_TREE_COLUMNS = ("name", "path", "lines", "size", "extension")
MAIN_TREE_HEADINGS = {
    "name": "Name",
    "path": "Path",
    "lines": "Lines",
    "size": "Size (bytes)",
    "extension": "Extension"
}
MAIN_COLUMN_WIDTHS: dict[str, tuple[int, int]] = {
    "name": (200, 100),
    "path": (350, 150),
    "lines": (80, 50),
    "size": (100, 80),
    "extension": (80, 50)
}
MAIN_COLUMN_WIDTHS: dict[str, tuple[int, int]] = {
    "name": (200, 100),  # type: ignore
    "path": (350, 150),  # type: ignore
    "lines": (80, 50),  # type: ignore
    "size": (100, 80),  # type: ignore
    "extension": (80, 50)  # type: ignore
}

HISTORY_TREE_COLUMNS = ("timestamp", "folder", "files", "lines", "size")
HISTORY_TREE_HEADINGS = {
    "timestamp": "Date/Time",
    "folder": "Folder",
    "files": "Files",
    "lines": "Lines",
    "size": "Size"
}
HISTORY_COLUMN_WIDTHS = {
    "timestamp": 180,
    "folder": 400,
    "files": 80,
    "lines": 100,
    "size": 120
}

# Chart configurations
CHART_COLORS = {
    "lines": "tab:blue",
    "size": "tab:red"
}
CHART_MARKER_SIZE = 12
CHART_LINE_WIDTH = 2
CHART_ALPHA = 0.7
CHART_FIGURE_SIZE = (10, 6)

# Application limits
MAX_HISTORY_ANALYSES = 50
SORT_INDICATORS = {
    "asc": "↑",
    "desc": "↓"
}

# File display values
ERROR_VALUE = "N/A"

# Padding values
PADDING = {
    "main": "10",
    "label_frame": "5",
    "vertical": (0, 5),
    "horizontal": (0, 5),
    "left": (0, 5),
    "button": (0, 5)
}

# File names
SETTINGS_FILE = "settings.json"
HISTORY_FILE = "analysis_history.json"

# Default settings
DEFAULT_SETTINGS = {
    "last_folder": "",
    "filter_extensions": "",
    "filter_exclude": "",
    "exclude_folders": "",
    "include_subfolders": True,
    "sort_columns": []
}

# Default history
DEFAULT_HISTORY = {
    "analyses": []
}

# UI labels
UI_LABELS = {
    "folder": "Folder:",
    "browse": "Browse...",
    "analyze": "Analyze",
    "filters": "Filters",
    "include_extensions": "Include extensions:",
    "include_extensions_hint": "(e.g., .py,.txt,.md - leave empty for all)",
    "exclude_patterns": "Exclude file patterns:",
    "exclude_patterns_hint": "(e.g., *.log,temp* - file name patterns to exclude)",
    "exclude_folders": "Exclude folders:",
    "exclude_folders_hint": "(e.g., node_modules,.git,__pycache__,venv - folders to skip)",
    "include_subfolders": "Include subfolders",
    "sort_hint": "Sort hint: Click column header to sort, Shift+Click for multi-column sort",
    "clear_sort": "Clear Sort",
    "export_csv": "Export to CSV",
    "view_history": "View History",
    "close": "Close",
    "files": "Files (Double-click for chart)",
    "summary": "Summary",
    "history_hint": "Double-click on an analysis to view detailed information"
}

# Status messages
STATUS_MESSAGES = {
    "initial": "Select a folder to analyze",
    "no_files": "No files found matching the criteria.",
    "analyzing": "Analyzing {} files...",
    "complete": "Analysis complete. Found {} files.",
    "no_folder": "Please select a folder first.",
    "invalid_folder": "Selected path is not a valid folder.",
    "no_history": "No history data found for {}",
    "no_data_export": "No data to export. Please analyze a folder first.",
    "export_success": "Data exported to {}",
    "export_failed": "Failed to export data: {}"
}

# Summary format
SUMMARY_FORMAT = "Total: {} files | {:,} lines | {}"
