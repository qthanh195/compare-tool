"""
View màn hình chính (Dashboard): người dùng chọn loại so sánh (Excel/CSV)
và 2 file cần so sánh, rồi bấm nút "So sánh ngay".

Lưu ý: view này CHỈ xử lý UI (hiển thị, bắt sự kiện chọn file). Toàn bộ
logic so sánh thực sự nằm ở app/core/comparators/ — view chỉ gọi tới đó,
không tự viết logic so sánh ở đây.
"""

import flet as ft

from app.core.comparators.csv_comparator import CsvComparator
from app.core.comparators.dxf_comparator import DxfComparator
from app.core.comparators.excel_comparator import ExcelComparator
from app.core.report.report_generator import export_diff_report
from app.config.settings import DEFAULT_OUTPUT_DIR
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Đăng ký comparator theo loại - khi thêm PDF/IFC sau này, chỉ cần thêm dòng vào đây
_COMPARATORS = {
    "excel": ExcelComparator(),
    "csv": CsvComparator(),
    "dxf": DxfComparator(),
}


class DashboardView(ft.Column):
    """Component Dashboard chính, được nhúng vào main_window.py."""

    def __init__(self, page: ft.Page, on_result_ready):
        """
        page:            đối tượng Page của Flet, dùng để cập nhật giao diện
        on_result_ready: callback được gọi khi so sánh xong, nhận vào DiffResult
                         để main_window chuyển sang màn hình kết quả
        """
        super().__init__(expand=True, spacing=20)
        self.page = page
        self.on_result_ready = on_result_ready

        self.selected_type = "excel"
        self.file_a_path: str | None = None
        self.file_b_path: str | None = None

        self.file_a_text = ft.Text("Chưa chọn file A", italic=True, color=ft.Colors.GREY)
        self.file_b_text = ft.Text("Chưa chọn file B", italic=True, color=ft.Colors.GREY)
        self.status_text = ft.Text("", color=ft.Colors.RED)
        self.progress = ft.ProgressBar(visible=False, width=400)

        self.type_selector = ft.RadioGroup(
            value="excel",
            on_change=self._on_type_change,
            content=ft.Row([
                ft.Radio(value="excel", label="So sánh Excel"),
                ft.Radio(value="csv", label="So sánh CSV"),
                ft.Radio(value="dxf", label="So sánh DXF"),
            ]),
        )

        # File picker của Flet để mở hộp thoại chọn file hệ điều hành
        self.file_picker_a = ft.FilePicker(on_result=self._on_pick_file_a)
        self.file_picker_b = ft.FilePicker(on_result=self._on_pick_file_b)
        self.page.overlay.extend([self.file_picker_a, self.file_picker_b])

        self.controls = [
            ft.Text("So sánh file", size=24, weight=ft.FontWeight.BOLD),
            self.type_selector,
            ft.Row([
                ft.ElevatedButton(
                    "Chọn File A",
                    icon=ft.Icons.UPLOAD_FILE,
                    on_click=lambda _: self.file_picker_a.pick_files(allow_multiple=False),
                ),
                self.file_a_text,
            ]),
            ft.Row([
                ft.ElevatedButton(
                    "Chọn File B",
                    icon=ft.Icons.UPLOAD_FILE,
                    on_click=lambda _: self.file_picker_b.pick_files(allow_multiple=False),
                ),
                self.file_b_text,
            ]),
            ft.ElevatedButton(
                "So sánh ngay",
                icon=ft.Icons.COMPARE_ARROWS,
                bgcolor=ft.Colors.BLUE,
                color=ft.Colors.WHITE,
                on_click=self._on_compare_click,
            ),
            self.progress,
            self.status_text,
        ]

    def _on_type_change(self, e: ft.ControlEvent) -> None:
        self.selected_type = e.control.value

    def _on_pick_file_a(self, e: ft.FilePickerResultEvent) -> None:
        if e.files:
            self.file_a_path = e.files[0].path
            self.file_a_text.value = self.file_a_path
            self.file_a_text.color = ft.Colors.BLACK
            self.page.update()

    def _on_pick_file_b(self, e: ft.FilePickerResultEvent) -> None:
        if e.files:
            self.file_b_path = e.files[0].path
            self.file_b_text.value = self.file_b_path
            self.file_b_text.color = ft.Colors.BLACK
            self.page.update()

    def _on_compare_click(self, e: ft.ControlEvent) -> None:
        self.status_text.value = ""

        if not self.file_a_path or not self.file_b_path:
            self.status_text.value = "Vui lòng chọn đầy đủ File A và File B."
            self.page.update()
            return

        comparator = _COMPARATORS[self.selected_type]

        is_valid, error_message = comparator.validate_files(self.file_a_path, self.file_b_path)
        if not is_valid:
            self.status_text.value = error_message
            self.page.update()
            return

        self.progress.visible = True
        self.page.update()

        try:
            result = comparator.compare(self.file_a_path, self.file_b_path)

            DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            report_path = DEFAULT_OUTPUT_DIR / "bao_cao_so_sanh_moi_nhat.xlsx"
            export_diff_report(result, str(report_path))

            logger.info(
                "So sánh xong: %s vs %s -> %d thay đổi, báo cáo: %s",
                self.file_a_path, self.file_b_path, len(result.items), report_path,
            )

            # Chuyển sang màn hình kết quả - view này sẽ bị gỡ khỏi trang ngay
            # sau lệnh gọi bên dưới (main_window thay thế bằng ResultView), nên
            # KHÔNG được tự ý update() cho self ở dưới nữa (self.page lúc đó
            # đã là None vì Flet tự gỡ tham chiếu page khi control rời cây UI).
            self.progress.visible = False
            self.on_result_ready(result, str(report_path))

        except Exception as ex:  # noqa: BLE001 - cố ý bắt mọi lỗi để hiển thị cho người dùng
            logger.exception("Lỗi khi so sánh file")
            self.status_text.value = f"Có lỗi xảy ra: {ex}"
            self.progress.visible = False
            self.page.update()
