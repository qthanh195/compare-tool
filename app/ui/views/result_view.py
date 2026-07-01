"""
View hiển thị kết quả so sánh dưới dạng bảng, có tô màu theo loại thay đổi
và nút quay lại / mở file báo cáo đã xuất.
"""

import os
import subprocess
import sys

import flet as ft

from app.core.models.diff_result import ChangeType, DiffResult

_COLOR_BY_CHANGE_TYPE = {
    ChangeType.MODIFIED: ft.Colors.AMBER_100,
    ChangeType.ADDED: ft.Colors.GREEN_100,
    ChangeType.REMOVED: ft.Colors.RED_100,
}

_LABEL_BY_CHANGE_TYPE = {
    ChangeType.MODIFIED: "Thay đổi",
    ChangeType.ADDED: "Thêm mới",
    ChangeType.REMOVED: "Đã xóa",
}


class ResultView(ft.Column):
    """Component hiển thị kết quả so sánh, được nhúng vào main_window.py."""

    def __init__(self, result: DiffResult, report_path: str, on_back):
        super().__init__(expand=True, spacing=16)

        summary = result.summary

        header = ft.Row([
            ft.Text("Kết quả so sánh", size=24, weight=ft.FontWeight.BOLD),
        ])

        summary_text = ft.Text(
            f"Tổng số thay đổi: {len(result.items)}  |  "
            f"Thay đổi: {summary['modified']}  |  "
            f"Thêm mới: {summary['added']}  |  "
            f"Đã xóa: {summary['removed']}",
            size=14,
        )

        if result.is_identical:
            summary_text = ft.Text("Hai file hoàn toàn giống nhau.", size=16, color=ft.Colors.GREEN)

        rows = []
        for item in result.items:
            rows.append(
                ft.DataRow(
                    color=_COLOR_BY_CHANGE_TYPE[item.change_type],
                    cells=[
                        ft.DataCell(ft.Text(item.location)),
                        ft.DataCell(ft.Text(_LABEL_BY_CHANGE_TYPE[item.change_type])),
                        ft.DataCell(ft.Text(item.old_value or "")),
                        ft.DataCell(ft.Text(item.new_value or "")),
                    ],
                )
            )

        table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Vị trí")),
                ft.DataColumn(ft.Text("Loại thay đổi")),
                ft.DataColumn(ft.Text("Giá trị cũ")),
                ft.DataColumn(ft.Text("Giá trị mới")),
            ],
            rows=rows,
        )

        table_container = ft.Container(
            content=ft.Column([table], scroll=ft.ScrollMode.AUTO),
            expand=True,
        )

        actions = ft.Row([
            ft.ElevatedButton("Quay lại", icon=ft.Icons.ARROW_BACK, on_click=lambda _: on_back()),
            ft.ElevatedButton(
                "Mở file báo cáo",
                icon=ft.Icons.FILE_OPEN,
                on_click=lambda _: self._open_report(report_path),
            ),
        ])

        self.controls = [header, summary_text, actions, table_container]

    @staticmethod
    def _open_report(report_path: str) -> None:
        """Mở file báo cáo Excel bằng ứng dụng mặc định của hệ điều hành."""
        if sys.platform == "win32":
            os.startfile(report_path)  # noqa: S606
        elif sys.platform == "darwin":
            subprocess.run(["open", report_path], check=False)
        else:
            subprocess.run(["xdg-open", report_path], check=False)
