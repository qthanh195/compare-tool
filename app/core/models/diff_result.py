"""
Định nghĩa cấu trúc dữ liệu chuẩn hóa cho kết quả so sánh.

Mọi comparator (Excel, CSV, DXF, và sau này PDF/IFC...) đều phải trả về
kết quả dưới dạng DiffResult, để UI chỉ cần biết xử lý MỘT cấu trúc dữ liệu
duy nhất, không quan tâm dữ liệu gốc đến từ loại file nào.
"""

from dataclasses import dataclass, field
from enum import Enum


class ChangeType(str, Enum):
    """Loại thay đổi được phát hiện khi so sánh."""

    MODIFIED = "modified"   # Giá trị/đối tượng bị sửa
    ADDED = "added"         # Dòng/đối tượng mới xuất hiện ở file B
    REMOVED = "removed"     # Dòng/đối tượng có ở file A nhưng bị xóa ở file B


@dataclass
class DiffItem:
    """
    Một thay đổi đơn lẻ được phát hiện.

    location:   vị trí thay đổi, ví dụ "Dòng 15, cột 'Đơn giá'" (Excel/CSV)
                hoặc "Layer: KETCAU, Handle: 2F3" (DXF)
    change_type: loại thay đổi (MODIFIED / ADDED / REMOVED)
    old_value:  giá trị cũ (None nếu là ADDED)
    new_value:  giá trị mới (None nếu là REMOVED)
    """

    location: str
    change_type: ChangeType
    old_value: str | None = None
    new_value: str | None = None


@dataclass
class DiffResult:
    """
    Kết quả tổng hợp của một lần so sánh 2 file.

    file_a / file_b: đường dẫn 2 file gốc được so sánh
    items:           danh sách chi tiết từng thay đổi (DiffItem)
    summary:         số liệu tóm tắt, ví dụ {"modified": 3, "added": 1, "removed": 0}
    is_identical:    True nếu 2 file hoàn toàn giống nhau (không có thay đổi nào)
    """

    file_a: str
    file_b: str
    items: list[DiffItem] = field(default_factory=list)

    @property
    def summary(self) -> dict[str, int]:
        """Đếm số lượng thay đổi theo từng loại, dùng để hiển thị lên UI."""
        counts = {"modified": 0, "added": 0, "removed": 0}
        for item in self.items:
            counts[item.change_type.value] += 1
        return counts

    @property
    def is_identical(self) -> bool:
        """True nếu không phát hiện thay đổi nào giữa 2 file."""
        return len(self.items) == 0
