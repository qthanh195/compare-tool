"""
Lớp cơ sở (interface chung) cho mọi loại so sánh file.

QUY TẮC QUAN TRỌNG:
Mọi comparator mới (Excel, CSV, DXF, và sau này nếu thêm PDF/IFC...) đều
PHẢI kế thừa lớp BaseComparator và triển khai đầy đủ 2 phương thức bên dưới.

Nhờ chuẩn hóa này, UI (main_window.py) chỉ cần gọi comparator theo đúng
1 cách duy nhất (validate_files() rồi compare()), không cần biết bên trong
xử lý Excel hay DXF khác nhau thế nào. Khi thêm loại file mới, chỉ cần viết
thêm 1 file comparator mới — không phải sửa code cũ đang chạy ổn định.
"""

from abc import ABC, abstractmethod

from app.core.models.diff_result import DiffResult


class BaseComparator(ABC):
    """Interface chung mà mọi comparator phải tuân theo."""

    @abstractmethod
    def validate_files(self, file_a: str, file_b: str) -> tuple[bool, str]:
        """
        Kiểm tra 2 file có hợp lệ để so sánh hay không (đúng định dạng,
        mở được, không rỗng...).

        Trả về:
            (True, "")               nếu hợp lệ
            (False, "lý do lỗi cụ thể")  nếu không hợp lệ, để hiển thị lên UI
        """
        raise NotImplementedError

    @abstractmethod
    def compare(self, file_a: str, file_b: str) -> DiffResult:
        """
        Thực hiện so sánh 2 file và trả về kết quả dạng chuẩn hóa DiffResult.

        Lưu ý: nên gọi validate_files() trước khi gọi compare() để tránh
        lỗi khi file không hợp lệ.
        """
        raise NotImplementedError
