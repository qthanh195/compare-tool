# Changelog

Tất cả thay đổi đáng chú ý của CompareTool được ghi lại ở đây.

## v0.2.0
- Phase 2: thêm tính năng so sánh file DXF (`dxf_comparator.py`, dùng `ezdxf`)
  - Hỗ trợ LINE, CIRCLE, ARC, LWPOLYLINE, TEXT, MTEXT, INSERT ở modelspace
  - Ghép cặp entity theo loại + vị trí gần nhất, có dung sai tọa độ cấu hình được
  - Tích hợp vào Dashboard UI (radio "So sánh DXF")
  - File DXF mẫu trong `samples/` để test thủ công

## v0.1.0
- Phase 1: MVP so sánh file Excel/CSV
  - So sánh 2 file CSV — phát hiện ô sửa (MODIFIED), dòng thêm (ADDED), dòng xóa (REMOVED)
  - So sánh 2 file Excel — so theo từng sheet, từng ô
  - Xuất báo cáo Excel có tô màu theo loại thay đổi
  - Giao diện Flet: chọn loại so sánh → chọn file → so sánh → xem kết quả → mở báo cáo
  - Log lỗi ghi vào `~/Documents/CompareTool_Reports/logs/app.log`
  - Unit test cho comparator lõi
