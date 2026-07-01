"""
Entry point bắt buộc ở gốc project cho `flet build` (flet CLI chỉ tìm
main.py ngay tại thư mục gốc, không tìm trong app/). Logic thật nằm ở
app/main.py — file này chỉ gọi sang đó để không phải đổi cấu trúc code.
"""

from app.main import main

main()
