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

from deltaforcetool import TimeClockUI, TimeConfig


def main():
    """Run the time clock UI."""
    config = TimeConfig(
        timezone="Asia/Shanghai",
        update_interval_ms=100
    )
    clock_ui = TimeClockUI(config)
    clock_ui.create_ui()


if __name__ == "__main__":
    main()
