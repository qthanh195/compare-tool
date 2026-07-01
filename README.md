# CompareTool — Phase 1 (MVP so sánh Excel/CSV)

Bản khung code đầu tiên theo đúng kiến trúc trong tài liệu kế hoạch. Đã test
logic lõi (comparator) chạy đúng — phần UI (Flet) chưa test được trên môi
trường này (cần máy có giao diện), bạn cần tự chạy thử trên máy Windows/macOS.

## Cách chạy thử

```bash
# 1. Tạo virtual environment (khuyến khích)
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux

# 2. Cài thư viện
pip install -r requirements.txt

# 3. Chạy ứng dụng (có hot-reload khi sửa code, tiện lúc phát triển)
flet run app/main.py

# Hoặc chạy như 1 ứng dụng thường:
python -m app.main
```

## Cách chạy unit test

```bash
pytest tests/ -v
```

## Đã làm được gì trong bản này (Phase 1)

- So sánh 2 file CSV — phát hiện ô sửa (MODIFIED), dòng thêm (ADDED), dòng
  xóa (REMOVED)
- So sánh 2 file Excel — so theo từng sheet, từng ô, kể cả khi 2 file có
  số sheet khác nhau
- Xuất báo cáo Excel có tô màu theo loại thay đổi (vàng = sửa, xanh = thêm,
  đỏ = xóa)
- Giao diện Flet: chọn loại so sánh → chọn 2 file → bấm so sánh → xem bảng
  kết quả → mở file báo cáo
- Có log lỗi ghi vào `~/Documents/CompareTool_Reports/logs/app.log`
- Có unit test cho phần lõi (CSV comparator)

## Việc cần làm tiếp theo (Phase 2 trở đi)

1. Chạy thử UI trên Windows thật, chỉnh lại bố cục theo mockup Claude Design
2. Test với file Excel/CSV thật của người dùng (không phải file mẫu tự tạo)
3. Viết `dxf_comparator.py` (dùng thư viện `ezdxf`) — theo đúng interface
   `BaseComparator` đã có sẵn, không cần sửa gì code hiện tại
4. Đóng gói bằng `flet build windows` để ra file `.exe`

## Cấu trúc thư mục

Xem chi tiết giải thích trong tài liệu kế hoạch đã gửi. Tóm tắt:

```
app/
├── main.py              # điểm khởi chạy
├── ui/                   # toàn bộ giao diện (Flet)
├── core/
│   ├── comparators/      # logic so sánh, mỗi loại file 1 module
│   ├── models/            # cấu trúc dữ liệu kết quả (DiffResult)
│   └── report/            # xuất báo cáo Excel
├── utils/                 # logger...
└── config/                # cấu hình chung
tests/                      # unit test
```
