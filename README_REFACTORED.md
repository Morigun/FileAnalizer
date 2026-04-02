# File Analyzer - Refactored Version

## Overview
File Analyzer is a desktop application for analyzing files in a folder and displaying information about them, including line counts, file sizes, and analysis history.

## Refactoring Completed

The original monolithic `file_analyzer.py` (905 lines) has been refactored into a modular architecture following SOLID principles.

## Project Structure

```
FileAnalizer/
├── app.py                    # Main FileAnalyzerApp class
├── constants.py              # Configuration constants
├── settings_manager.py       # Settings persistence
├── history_manager.py        # Analysis history management
├── file_scanner.py          # File scanning and analysis logic
├── chart_manager.py         # Chart rendering with matplotlib
├── treeview_builder.py     # Treeview UI component
├── data_formatter.py        # Data display formatting
├── sort_manager.py          # Sorting logic
├── main.py                 # Entry point
├── run.bat                 # Windows launcher script
├── requirements.txt          # Python dependencies
└── file_analyzer_old.py    # Original version (backup)
```

## Module Descriptions

### app.py
Contains the main `FileAnalyzerApp` class that coordinates all components and handles UI events.

### constants.py
Centralized configuration including:
- Window geometries and titles
- Treeview column configurations
- Chart settings
- UI labels and messages
- Application limits

### settings_manager.py
Handles loading and saving application settings to `settings.json`.

### history_manager.py
Manages analysis history including:
- Loading/saving history from `analysis_history.json`
- Adding new analysis entries
- Retrieving file history across multiple analyses
- Maintaining history size limit (50 analyses)

### file_scanner.py
Contains the `FileAnalyzer` class for file operations:
- Directory scanning (with/without subfolders)
- File filtering by extensions and patterns
- Line counting
- File metadata extraction

### chart_manager.py
Creates matplotlib charts with dual Y-axis:
- Left axis: Line counts (blue)
- Right axis: File sizes (red)
- Support for overlapping data points

### treeview_builder.py
Builder for creating consistent Treeview widgets with:
- Scrollbars
- Column configuration
- Sortable headers
- Data population

### data_formatter.py
Handles formatting of data for display:
- Line count formatting
- Size formatting (human-readable)
- File info formatting for treeview
- Timestamp formatting
- Number formatting with separators

### sort_manager.py
Manages multi-column sorting:
- Single column sort
- Multi-column sort (Shift+Click)
- Sort indicators in column headers
- Sort direction toggling

## Usage

### Running the Application

**Windows:**
```batch
run.bat
```

**Direct Python:**
```bash
python main.py
```

## Features

1. **Folder Analysis**
   - Select a folder and analyze all files
   - Support for subfolder traversal
   - Filter by file extensions
   - Exclude specific files and folders

2. **File Information Display**
   - File name, path, extension
   - Line count
   - File size in bytes
   - Sortable columns
   - Multi-column sort support (Shift+Click)

3. **Analysis History**
   - Automatic saving of each analysis
   - Maintains last 50 analyses
   - View history in separate window
   - Detailed analysis review

4. **File History Charts**
   - Double-click any file to view its history
   - Charts show line count and size changes over time
   - Dual Y-axis for different scales
   - Visual indicators for trends

5. **Data Export**
   - Export current analysis to CSV
   - Includes all file information

6. **Settings Persistence**
   - Remembers last analyzed folder
   - Saves filter preferences
   - Preserves sort configuration

## Refactoring Benefits

### Maintainability
- Smaller, focused classes are easier to understand
- Changes to one concern don't affect others
- Clear separation of responsibilities

### Testability
- Each module can be tested independently
- Mock dependencies for unit testing
- Clear interfaces between components

### Extensibility
- Easy to add new file analysis features
- Simple to add new chart types
- New filters or sort options straightforward

### Code Quality
- Reduced duplication (DRY principle)
- Better organization
- Follows SOLID principles
- Type hints throughout

## Dependencies

- Python 3.8+
- matplotlib (for charts)
- tkinter (included with Python)

## Development

### Adding New Features

1. **New analysis metric:** Update `file_scanner.py` and extend data structures
2. **New chart type:** Add method to `chart_manager.py`
3. **New filter option:** Update constants and UI setup
4. **New export format:** Add method to `app.py`

## Notes

- The original `file_analyzer.py` is preserved as `file_analyzer_old.py`
- Settings and history files are JSON format for easy inspection
- Application works on Windows, Linux, and macOS
