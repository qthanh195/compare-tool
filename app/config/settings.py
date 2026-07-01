"""
Cấu hình chung của ứng dụng.

Để riêng file này giúp sau này chỉnh sửa các giá trị mặc định (đường dẫn
lưu báo cáo, tên app, dung sai DXF...) mà không phải lục tìm trong code UI.
"""

from pathlib import Path

APP_NAME = "CompareTool"
APP_VERSION = "0.1.0"  # Phase 1 - MVP so sánh Excel/CSV

# Thư mục mặc định để lưu báo cáo xuất ra (tự tạo trong thư mục Documents của người dùng)
DEFAULT_OUTPUT_DIR = Path.home() / "Documents" / "CompareTool_Reports"

# Dung sai mặc định khi so sánh tọa độ trong DXF (đơn vị: mm) - dùng ở Phase 2
DEFAULT_DXF_TOLERANCE_MM = 1.0

# Các định dạng file được hỗ trợ cho từng loại so sánh
SUPPORTED_EXTENSIONS = {
    "excel": [".xlsx", ".xlsm"],
    "csv": [".csv"],
    "dxf": [".dxf"],
}
