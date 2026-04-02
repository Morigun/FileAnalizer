"""
Main entry point for File Analyzer application.
"""

import tkinter as tk
from app import FileAnalyzerApp


def main():
    """Main entry point for the application."""
    root = tk.Tk()
    app = FileAnalyzerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
