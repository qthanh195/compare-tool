"""
Cửa sổ chính của ứng dụng - điều phối việc chuyển đổi giữa các view
(Dashboard <-> Result). Đây là nơi DUY NHẤT biết về "luồng màn hình",
từng view riêng lẻ không cần biết view khác tồn tại.
"""

import flet as ft

from app.config.settings import APP_NAME
from app.core.models.diff_result import DiffResult
from app.ui.views.dashboard_view import DashboardView
from app.ui.views.result_view import ResultView


def build_main_window(page: ft.Page) -> None:
    """Điểm khởi tạo giao diện chính, được gọi từ app/main.py."""
    page.title = APP_NAME
    page.window.width = 1000
    page.window.height = 700
    page.padding = 24

    content_area = ft.Column(expand=True)
    page.add(content_area)

    def show_dashboard() -> None:
        content_area.controls = [DashboardView(page, on_result_ready=show_result)]
        page.update()

    def show_result(result: DiffResult, report_path: str) -> None:
        content_area.controls = [ResultView(result, report_path, on_back=show_dashboard)]
        page.update()

    show_dashboard()
