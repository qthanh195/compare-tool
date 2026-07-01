# CompareTool — Phase 1 + Phase 2 (so sánh Excel/CSV/DXF)

Bản khung code theo đúng kiến trúc trong tài liệu kế hoạch. Đã test logic lõi
(comparator) chạy đúng, bao gồm cả DXF (Phase 2). Phần UI (Flet) đã chạy thử
thành công trên Windows.

Lịch sử phiên bản: xem [`CHANGELOG.md`](CHANGELOG.md). Hướng dẫn đóng gói ra
file `.exe`: xem [`BUILD.md`](BUILD.md).

## Cách chạy thử — dùng conda (khuyến khích, dự án đang dùng cách này)

```powershell
# 1. Tạo conda environment riêng cho project (chỉ cần làm 1 lần)
conda create -n compare_tool python=3.11 -y

# 2. Cài thư viện vào environment vừa tạo
conda run -n compare_tool pip install -r requirements.txt

# 3a. Chạy ứng dụng bằng conda run (không cần activate)
conda run -n compare_tool python -m app.main

# 3b. Hoặc activate environment rồi chạy như bình thường (có hot-reload
#     khi sửa code, tiện lúc phát triển)
conda activate compare_tool
flet run app/main.py
```

**Lưu ý về phiên bản `flet`:** `requirements.txt` ghim cứng `flet==0.28.3`.
Code hiện tại dùng API nằm giữa 2 thế hệ Flet (cần cả `ft.Colors`/`ft.Icons`
viết hoa và `ft.FilePickerResultEvent`) — các bản `flet` mới hơn (vd 0.85.x)
đã đổi/xóa API này và sẽ làm app crash khi khởi động. Không tự ý nâng cấp
`flet` lên bản mới hơn nếu chưa kiểm tra kỹ.

## Cách chạy thử — dùng venv (nếu không dùng conda)

```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux

pip install -r requirements.txt

flet run app/main.py
# Hoặc: python -m app.main
```

## Cách chạy unit test

```bash
# Với conda
conda run -n compare_tool pytest tests/ -v

# Với venv (sau khi activate)
pytest tests/ -v
```

## Test thử tính năng so sánh DXF

Thư mục `samples/` có sẵn 2 file DXF mẫu (`sample_a.dxf` / `sample_b.dxf`)
mô phỏng các trường hợp: entity dịch chuyển, đổi bán kính, đổi layer, thêm
mới, bị xóa. Chọn radio "So sánh DXF" trong app, chọn 2 file này làm File
A/File B rồi bấm "So sánh ngay" để xem kết quả.

## Đã làm được gì

**Phase 1:**
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

**Phase 2:**
- So sánh 2 file DXF (`dxf_comparator.py`, dùng `ezdxf`) — hỗ trợ LINE,
  CIRCLE, ARC, LWPOLYLINE, TEXT, MTEXT, INSERT ở modelspace
- Ghép cặp entity giữa 2 file theo loại + vị trí gần nhất (greedy
  nearest-neighbor), có dung sai tọa độ cấu hình được (`tolerance_mm`,
  mặc định `DEFAULT_DXF_TOLERANCE_MM` trong `app/config/settings.py`)
- Đã tích hợp vào Dashboard UI (radio "So sánh DXF")
- Có unit test cho phần lõi (DXF comparator) + file DXF mẫu trong `samples/`

## Việc cần làm tiếp theo

1. Test với file Excel/CSV/DXF thật của người dùng (không phải file mẫu tự tạo)
2. Trực quan hóa bản vẽ DXF trên canvas (hiện tại DXF chỉ hiển thị dạng bảng
   danh sách thay đổi, giống Excel/CSV)
3. Chỉnh lại bố cục UI theo mockup Claude Design
4. Đóng gói bằng `flet build windows` để ra file `.exe` — xem hướng dẫn chi
   tiết trong [`BUILD.md`](BUILD.md) (cần cài thêm Visual Studio C++
   workload trước khi build được)

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
samples/                    # file mẫu (DXF) để test thủ công trong app
```
