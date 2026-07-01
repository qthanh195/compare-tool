"""
Điểm khởi chạy ứng dụng CompareTool.

Chạy bằng lệnh:  python -m app.main
(hoặc "flet run app/main.py" khi phát triển để có hot-reload)
"""

import flet as ft

from app.ui.main_window import build_main_window


def main() -> None:
    ft.app(target=build_main_window)


if __name__ == "__main__":
    main()
