# -*- coding: UTF-8 -*-
"""
@file main.py
@author f-hy (friend0@qq.com)
@date 2026-05-22
@version 0.1
@brief DeltaForceTool entry point
@github https://github.com/f-hy
@copyright Copyright (c) 2026
"""

import tkinter as tk

from deltaforcetool import TimeClockUI, TimeConfig, OCRTool


def main():
    """Run the time clock UI."""
    config = TimeConfig(
        timezone="Asia/Shanghai",
        update_interval_ms=100
    )
    clock_ui = TimeClockUI(config)
    clock_ui.create_ui()

    # Register Alt+S shortcut for OCR tool
    clock_ui.root.bind('<Alt-s>', lambda event: run_ocr_tool())

    # Create a separate window for the main app
    main_window = tk.Tk()
    main_window.title("DeltaForceTool")
    main_window.geometry("800x600")

    label = tk.Label(main_window, text="DeltaForceTool\nPress Alt+S for OCR Float Detection")
    label.pack(pady=20)

    main_window.mainloop()


def run_ocr_tool():
    """Run the OCR tool."""
    ocr_tool = OCRTool()
    ocr_tool.run()


if __name__ == "__main__":
    main()
