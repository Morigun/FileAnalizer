"""
Chart management for File Analyzer.
"""

import tkinter as tk
import tkinter.ttk as ttk
from typing import List, Dict, Any
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from constants import CHART_COLORS, CHART_MARKER_SIZE, CHART_LINE_WIDTH, CHART_ALPHA, CHART_FIGURE_SIZE


class ChartManager:
    """Manages chart creation and display."""
    
    @staticmethod
    def create_history_chart(parent_window: tk.Tk | tk.Toplevel, file_name: str, 
                          file_history: List[Dict[str, Any]]) -> None:
        """Create and display a chart with file history."""
        chart_window = tk.Toplevel(parent_window)
        chart_window.title(f"File History: {file_name}")
        chart_window.geometry("900x600")
        
        fig, ax1 = plt.subplots(figsize=CHART_FIGURE_SIZE)
        
        # Sort by timestamp
        file_history_sorted = sorted(file_history, key=lambda x: x["timestamp"])
        
        timestamps = [datetime.fromisoformat(h["timestamp"]) for h in file_history_sorted]
        lines = [h["lines"] if h["lines"] >= 0 else 0 for h in file_history_sorted]
        sizes = [h["size"] if h["size"] >= 0 else 0 for h in file_history_sorted]
        
        # Plot lines on left axis
        color1 = CHART_COLORS["lines"]
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Lines', color=color1, fontweight='bold')
        
        line1 = ax1.plot(timestamps, lines, color=color1, marker='o', 
                         markersize=CHART_MARKER_SIZE, label='Lines', 
                         linewidth=CHART_LINE_WIDTH, zorder=5, alpha=CHART_ALPHA)
        
        ax1.tick_params(axis='y', labelcolor=color1)
        ax1.grid(True, alpha=0.3)
        
        # Set y-axis limits
        ChartManager._set_axis_limits(ax1, lines)
        
        # Create second y-axis for size
        ax2 = ax1.twinx()
        color2 = CHART_COLORS["size"]
        ax2.set_ylabel('Size (bytes)', color=color2, fontweight='bold')
        
        line2 = ax2.plot(timestamps, sizes, color=color2, marker='s', 
                         markersize=CHART_MARKER_SIZE, label='Size (bytes)', 
                         linewidth=CHART_LINE_WIDTH, zorder=4, alpha=CHART_ALPHA)
        
        ax2.tick_params(axis='y', labelcolor=color2)
        
        # Set y-axis limits
        ChartManager._set_axis_limits(ax2, sizes)
        
        # Format x-axis dates
        fig.autofmt_xdate()
        
        # Add title
        plt.title(f'File History: {file_name}', fontweight='bold')
        
        # Add legend
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', framealpha=1.0)
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, master=chart_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add close button
        close_btn = ttk.Button(chart_window, text="Close", command=chart_window.destroy)
        close_btn.pack(pady=10)
    
    @staticmethod
    def _set_axis_limits(ax, data: List[int]) -> None:
        """Set axis limits to ensure data is visible."""
        if data:
            min_val = min(data)
            max_val = max(data)
            if min_val == max_val:
                # If all values are same, set range around them
                margin = max(10, min_val * 0.1)
                ax.set_ylim(max(0, min_val - margin), min_val + margin)
            else:
                margin = max(1, (max_val - min_val) * 0.2)
                ax.set_ylim(max(0, min_val - margin), max_val + margin)
