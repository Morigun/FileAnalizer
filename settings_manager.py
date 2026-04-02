"""
Settings management for File Analyzer.
"""

import json
from pathlib import Path
from typing import Dict, Any
from constants import DEFAULT_SETTINGS, SETTINGS_FILE


class SettingsManager:
    """Manages application settings."""
    
    def __init__(self, settings_dir: Path):
        self.settings_file = settings_dir / SETTINGS_FILE
    
    def load_settings(self) -> Dict[str, Any]:
        """Load settings from JSON file."""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    return {**DEFAULT_SETTINGS, **settings}
        except (json.JSONDecodeError, IOError):
            pass
        return DEFAULT_SETTINGS.copy()
    
    def save_settings(self, settings: Dict[str, Any]) -> bool:
        """Save settings to JSON file."""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2)
            return True
        except IOError as e:
            print(f"Warning: Could not save settings: {e}")
            return False
