# Hướng dẫn đóng gói CompareTool thành file .exe (Windows)

## Đã build thành công (2026-07-01)

Đã build thử ngay trên máy này và ra được file `.exe` chạy được — các bước
dưới đây là quy trình đã kiểm chứng thực tế (không phải suy đoán từ tài
liệu flet), kèm toàn bộ lỗi gặp phải và cách đã fix, để lần sau build lại
(ví dụ khi ra bản mới) không mất công dò lại từ đầu.

## Bước 1: Cài môi trường Python + dependencies

Dự án đang dùng conda env tên `compare_tool` (xem `README.md`). Nếu chưa có:

```powershell
conda create -n compare_tool python=3.11 -y
conda activate compare_tool
pip install -r requirements.txt
```

**Không nâng cấp `flet` lên bản mới hơn `0.28.3`** — code hiện tại dùng API
nằm giữa 2 thế hệ Flet, các bản mới hơn (vd 0.85.x) sẽ làm app crash khi
khởi động (xem lưu ý trong `README.md`). Bản `flet==0.28.3` đã có sẵn lệnh
`flet build`, không cần cài thêm package nào khác cho việc đóng gói.

`pandas` đã được ghim cứng về `3.0.3` trong `requirements.txt` — đây đúng
là bản mà `flet build` thực tế đã tải và bundle vào exe, đã chạy lại toàn
bộ unit test với bản này và pass. Không cần lo lỗi tương thích, nhưng cũng
đừng tự ý đổi version pandas mà không chạy lại test.

## Bước 2: Cài công cụ build Windows (Flutter + Visual Studio)

`flet build windows` build ứng dụng qua Flutter, nên cần:

1. **Flutter SDK** — chỉ cần để `flutter doctor` nhận diện được Visual
   Studio đúng cách; bản thân `flet build` sẽ **tự tải riêng một bản
   Flutter khác** vào cache của nó (xem lưu ý ở Bước 3), nên không bắt
   buộc phải có sẵn `C:\flutter`. Nếu muốn cài để chạy `flutter doctor`
   kiểm tra trước, tải tại flutter.dev và thêm `C:\flutter\bin` vào `PATH`.

2. **Visual Studio 2022** (Community bản miễn phí là đủ) với workload
   **"Desktop development with C++"**:

   > ⚠️ **Lưu ý quan trọng — dễ nhầm:** Nếu máy bạn có cài **SQL Server
   > Management Studio (SSMS)**, nó cũng dùng chung hạ tầng "Visual Studio
   > Installer" nên sẽ xuất hiện trong danh sách "Modify" như thể là một
   > bản Visual Studio. **SSMS không phải Visual Studio IDE** và **không
   > thể thêm workload "Desktop development with C++" vào SSMS được** —
   > nếu Visual Studio Installer chỉ cho bạn "Modify" một mục tên "SQL
   > Server Management Studio", nghĩa là máy bạn chưa có Visual Studio IDE
   > thật, cần **cài mới** (không phải "Modify") theo hướng dẫn dưới đây.
   > Cách kiểm tra chắc chắn: chạy `flutter doctor -v`, dòng "Visual
   > Studio - develop Windows apps" nếu ghi tên "SQL Server Management
   > Studio ..." trong ngoặc thì đúng là chưa có Visual Studio IDE.

   - Tải **Visual Studio Community 2022** (bản IDE đầy đủ, miễn phí) tại
     https://visualstudio.microsoft.com/downloads/ — mục "Visual Studio
     Community 2022", nút "Free download". Chạy file cài đặt tải về.
     (Có thể cài nhanh qua dòng lệnh:
     `winget install --id Microsoft.VisualStudio.2022.Community --exact --override "--wait --quiet --add Microsoft.VisualStudio.Workload.NativeDesktop --includeRecommended"`)
   - Ở màn hình chọn workload của trình cài đặt, tick chọn
     **"Desktop development with C++"**
   - Đảm bảo các component sau được tick trong phần chi tiết bên phải
     (thường được tick sẵn khi chọn workload trên):
     - MSVC v143 (hoặc mới hơn) - VS 2022 C++ x64/x86 build tools
     - C++ CMake tools for Windows
     - Windows 10 SDK (hoặc Windows 11 SDK)
   - Cài xong, chờ vài phút — có thể mất 15-30 phút tùy tốc độ mạng, cần
     khoảng 5-7 GB dung lượng ổ đĩa

3. Kiểm tra lại bằng lệnh:

   ```powershell
   flutter doctor -v
   ```

   Khi mục "Visual Studio - develop Windows apps" hiện dấu `[√]` (kèm tên
   "Visual Studio Community 2022...", không phải "SQL Server Management
   Studio") là đã sẵn sàng để build.

## Bước 3: Chạy lệnh build

Project có cấu trúc package (`app/main.py`, `app/ui/...`, `app/core/...`)
chứ không phải 1 file `main.py` đơn ở gốc — `flet build` mặc định chỉ tìm
`main.py` ngay tại thư mục gốc. Vì vậy đã có sẵn file `main.py` ở gốc
project (chỉ 3 dòng, gọi sang `app/main.py`, không cần đụng vào nữa):

```python
from app.main import main
main()
```

Lệnh build đã chạy thành công (trong PowerShell, tại thư mục gốc project,
với conda env `compare_tool` đã activate):

```powershell
$env:PYTHONUTF8 = "1"
flet build windows --project "CompareTool" --description "Cong cu so sanh file Excel/CSV/DXF" --exclude ".git,venv,.venv,tests,.pytest_cache,.claude,samples"
```

Giải thích 2 phần khác với lệnh gốc ban đầu:

- **`$env:PYTHONUTF8 = "1"`** — bắt buộc trên máy này, nếu không sẽ bị
  crash giữa chừng với lỗi `UnicodeEncodeError: 'charmap' codec can't
  encode character '●'...` (thư viện `rich` mà flet dùng để vẽ
  progress bar cố in ký tự `●` ra console đang ở bảng mã `cp1252` thay vì
  UTF-8). Set biến môi trường này trước khi chạy `flet build` là đủ.
- **`--exclude ...`** — mặc định `flet build` chỉ tự loại trừ thư mục
  `build`, nó sẽ đóng gói **toàn bộ** thư mục gốc project vào file `.exe`
  (kể cả `.git`, `venv`, `tests`...) nếu không chỉ định exclude, làm file
  nặng lên vô ích. Danh sách trên đã loại các thư mục không cần thiết cho
  app chạy thực tế (file mẫu DXF trong `samples/` không cần bundle vào
  exe vì người dùng tự chọn file bất kỳ qua dialog, không phải file có
  sẵn trong app).

Lệnh này cần internet để tải Flutter/Dart packages **vào cache riêng của
flet** (không dùng `C:\flutter` có sẵn — flet tự tải bản nó cần, ví dụ đã
tải Flutter 3.29.2 dù máy có sẵn 3.19.6) trong lần build đầu tiên (~800MB-1GB,
các lần build sau nhanh hơn nhiều nhờ cache). Nếu bị rớt mạng giữa chừng
(lỗi `ConnectionAbortedError: [WinError 10053]`) — đã gặp lỗi này 1 lần
trên máy này, chỉ cần chạy lại lệnh, nó tự tải tiếp/tải lại thành công ở
lần sau.

Nếu muốn gắn icon riêng: đặt file `assets/icon.ico` (đã khai báo sẵn
đường dẫn ở `app/config/settings.py` qua hằng `APP_ICON_PATH`), sau đó
chạy `flet build windows --help` để xem tên flag/cấu hình icon đúng với
bản `flet` đang cài (một số bản dùng flag `--icon`, một số bản mới hơn
cấu hình icon qua `pyproject.toml`). Nếu không có icon, `flet build` sẽ
tự dùng icon mặc định của Flet, không lỗi (đã xác nhận thực tế).

## Bước 4: Vị trí file .exe sau khi build

Sau khi build thành công, file thực thi nằm ở:

```
build\windows\comparetool.exe
```

**Lưu ý:** tên file exe là `comparetool.exe` viết thường, KHÔNG phải
`CompareTool.exe` — `flet build` tự chuyển tên project (`--project`
"CompareTool") thành chữ thường khi đặt tên file thực thi.

(Toàn bộ thư mục `build\windows\` — khoảng 170MB, chứa file `.exe`, các
DLL runtime của Flutter/Python, và `site-packages/` với `pandas`,
`openpyxl`, `ezdxf`, `flet` đã bundle sẵn — khi gửi cho người dùng thử
nghiệm, nén/gửi **cả thư mục `build\windows\`**, không chỉ riêng file
`.exe`, nếu không app sẽ báo thiếu DLL khi chạy trên máy khác.)

## Bước 5: Test nhanh file .exe

Đã tự chạy thử `comparetool.exe` ngay sau khi build (mở lên bình thường,
không crash) — nhưng vẫn cần bạn tự kiểm tra đầy đủ luồng chức năng:

1. Copy cả thư mục `build\windows\` sang một máy Windows khác (hoặc một
   thư mục khác trên cùng máy, để chắc chắn không "ăn may" nhờ Python đã
   cài sẵn) rồi chạy `comparetool.exe`.
2. Kiểm tra cửa sổ app mở lên đúng tiêu đề "CompareTool", không crash.
3. Chọn radio "So sánh CSV" hoặc "So sánh Excel", bấm chọn File A / File B
   — kiểm tra dialog chọn file của Windows mở lên bình thường (đây là
   phần hay lỗi nhất khi đóng gói vì cần đúng plugin file_picker của
   Flutter).
4. Chọn 2 file mẫu trong `samples/` (`sample_a.dxf` / `sample_b.dxf`) với
   radio "So sánh DXF", bấm "So sánh ngay" — kiểm tra bảng kết quả hiện ra
   đúng, có phân loại Thêm mới / Đã xóa / Thay đổi.
5. Bấm nút mở báo cáo — kiểm tra file Excel báo cáo được tạo ra trong
   `Documents\CompareTool_Reports\` và mở lên đúng, có tô màu theo loại
   thay đổi.
6. Kiểm tra file log `Documents\CompareTool_Reports\logs\app.log` có được
   tạo ra không (để sau này người dùng thử nghiệm gửi lại log nếu gặp lỗi).

Nếu cả 6 bước trên đều ổn thì file `.exe` đã sẵn sàng gửi cho người dùng
thử nghiệm.

## Sự cố thường gặp

- **"flutter: command not found" / "flet: command not found"** — chưa
  activate đúng conda env, hoặc chưa thêm `C:\flutter\bin` vào `PATH`.
- **`main.py not found in the root of Flet app directory`** — file
  `main.py` ở gốc project bị xóa/đổi tên nhầm. File này bắt buộc phải tồn
  tại (xem Bước 3), đừng xóa.
- **`UnicodeEncodeError: 'charmap' codec can't encode character '●'`**
  — quên set `$env:PYTHONUTF8 = "1"` trước khi chạy `flet build` (xem
  Bước 3).
- **`ConnectionAbortedError: [WinError 10053]` giữa chừng lúc tải
  Flutter** — mạng chập chờn lúc tải file ~1GB, chạy lại lệnh build là
  được, không cần đổi gì.
- **Lỗi liên quan tới CMake / MSVC khi build** — chưa cài đủ component ở
  Bước 2, chạy lại `flutter doctor -v` để xem còn thiếu gì (phải thấy tên
  "Visual Studio Community 2022", không phải "SQL Server Management
  Studio").
- **Build treo lâu ở bước tải gói lần đầu** — do mạng chậm/bị chặn tới
  `pub.dev`, thử lại ở mạng khác hoặc dùng VPN.
- **App mở lên rồi crash ngay / báo lỗi `AttributeError` liên quan
  `ft.Colors` hoặc `ft.Icons`** — có ai đó đã lỡ nâng cấp `flet` lên bản
  mới hơn `0.28.3`. Chạy `pip show flet` để kiểm tra, hạ lại bản đúng bằng
  `pip install flet==0.28.3`.
