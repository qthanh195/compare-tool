"""
Comparator dùng để so sánh 2 file DXF (bản vẽ CAD).

Cách hoạt động:
1. Đọc 2 file DXF bằng ezdxf, lấy toàn bộ entity ở modelspace thuộc các loại
   được hỗ trợ (LINE, CIRCLE, ARC, LWPOLYLINE, TEXT, MTEXT, INSERT).
2. Khác với CSV/Excel (có số dòng, tọa độ ô cố định để so khớp), DXF không
   có ID cố định nào để biết entity nào ở file A tương ứng với entity nào ở
   file B -> phải "ghép cặp" (matching) trước khi kết luận thêm/xóa/sửa.
3. Thuật toán ghép cặp (xem _match_entities): ghép theo LOẠI entity trước
   (không ghép kèm layer, vì đổi layer cũng cần báo là MODIFIED chứ không
   phải xóa+thêm), sau đó ghép tham lam theo khoảng cách vị trí gần nhau
   nhất trong cùng loại, có giới hạn khoảng cách tối đa để tránh ghép nhầm
   2 entity ở 2 khu vực khác nhau của bản vẽ.
4. Cặp đã ghép được so sánh chi tiết theo tolerance_mm để quyết định là
   MODIFIED hay giống nhau; entity không ghép được thì là ADDED/REMOVED.
"""

import math
import os
from typing import Any

import ezdxf

from app.config.settings import DEFAULT_DXF_TOLERANCE_MM
from app.core.comparators.base_comparator import BaseComparator
from app.core.models.diff_result import ChangeType, DiffItem, DiffResult

# Các loại entity được hỗ trợ so sánh ở Phase 2 - đủ dùng cho bản vẽ xây dựng
# cơ bản (đường thẳng, hình tròn, cung tròn, đa tuyến, chữ, block tham chiếu)
_SUPPORTED_DXFTYPES = ("LINE", "CIRCLE", "ARC", "LWPOLYLINE", "TEXT", "MTEXT", "INSERT")

# Ngưỡng khoảng cách tối đa để 2 entity còn được coi là "cùng 1 đối tượng bị
# dịch chuyển" khi ghép cặp = 1000 x tolerance_mm (mặc định 1000mm = 1m):
# đủ lớn để bắt được các trường hợp dịch chuyển thực tế trong bản vẽ xây dựng,
# nhưng vẫn tránh ghép nhầm 2 entity ở 2 khu vực khác nhau của bản vẽ thành
# một cặp "bị sửa" trong khi thực ra đó là 2 đối tượng độc lập.
_MAX_MATCH_DISTANCE_FACTOR = 1000

# Dung sai góc (độ) khi so sánh start_angle/end_angle của ARC - không dùng
# chung tolerance_mm vì góc không cùng đơn vị với tọa độ/bán kính (mm)
_ANGLE_TOLERANCE_DEG = 0.01


def _point2d(point: Any) -> tuple[float, float]:
    """Chuyển 1 điểm (Vec3 của ezdxf hoặc tuple từ get_points()) về (x, y) thuần."""
    return (float(point[0]), float(point[1]))


def _euclidean(p1: tuple[float, float], p2: tuple[float, float]) -> float:
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])


def _fmt_point(point: tuple[float, float]) -> str:
    return f"({point[0]:.1f}, {point[1]:.1f})"


class DxfComparator(BaseComparator):
    """So sánh 2 file DXF theo từng entity ở modelspace (ghép cặp theo vị trí gần nhất)."""

    def __init__(self, tolerance_mm: float | None = None):
        self.tolerance_mm = DEFAULT_DXF_TOLERANCE_MM if tolerance_mm is None else tolerance_mm

    def validate_files(self, file_a: str, file_b: str) -> tuple[bool, str]:
        for path in (file_a, file_b):
            if not os.path.exists(path):
                return False, f"Không tìm thấy file: {path}"
            if not path.lower().endswith(".dxf"):
                return False, f"File không đúng định dạng .dxf: {path}"
            try:
                ezdxf.readfile(path)
            except Exception as ex:  # noqa: BLE001 - ezdxf ném nhiều loại lỗi khác nhau khi file hỏng
                return False, f"Không mở được file DXF (file có thể bị hỏng): {path} ({ex})"
        return True, ""

    def compare(self, file_a: str, file_b: str) -> DiffResult:
        result = DiffResult(file_a=file_a, file_b=file_b)

        doc_a = ezdxf.readfile(file_a)
        doc_b = ezdxf.readfile(file_b)

        entities_a = self._collect_entities(doc_a)
        entities_b = self._collect_entities(doc_b)

        # So sánh riêng theo từng loại (LINE chỉ ghép với LINE, CIRCLE chỉ
        # ghép với CIRCLE...) vì 2 loại entity khác nhau về bản chất không
        # thể coi là "cùng 1 đối tượng bị đổi loại".
        for dxftype in _SUPPORTED_DXFTYPES:
            group_a = [e for e in entities_a if e.dxftype() == dxftype]
            group_b = [e for e in entities_b if e.dxftype() == dxftype]
            self._compare_group(dxftype, group_a, group_b, result)

        return result

    @staticmethod
    def _collect_entities(doc) -> list:
        """Lấy toàn bộ entity thuộc các loại được hỗ trợ ở modelspace."""
        return [e for e in doc.modelspace() if e.dxftype() in _SUPPORTED_DXFTYPES]

    def _compare_group(self, dxftype: str, group_a: list, group_b: list, result: DiffResult) -> None:
        matches, unmatched_a, unmatched_b = self._match_entities(group_a, group_b)

        for entity_a in unmatched_a:
            props = self._extract_props(entity_a)
            result.items.append(
                DiffItem(
                    location=self._location(dxftype, props),
                    change_type=ChangeType.REMOVED,
                    old_value=self._describe(props),
                    new_value=None,
                )
            )

        for entity_b in unmatched_b:
            props = self._extract_props(entity_b)
            result.items.append(
                DiffItem(
                    location=self._location(dxftype, props),
                    change_type=ChangeType.ADDED,
                    old_value=None,
                    new_value=self._describe(props),
                )
            )

        for entity_a, entity_b in matches:
            props_a = self._extract_props(entity_a)
            props_b = self._extract_props(entity_b)
            old_desc, new_desc = self._diff_props(props_a, props_b)
            if old_desc is None:
                continue  # khác biệt (nếu có) đều trong phạm vi tolerance -> coi là giống nhau
            result.items.append(
                DiffItem(
                    location=self._location(dxftype, props_a),
                    change_type=ChangeType.MODIFIED,
                    old_value=old_desc,
                    new_value=new_desc,
                )
            )

    def _match_entities(
        self, group_a: list, group_b: list
    ) -> tuple[list[tuple[Any, Any]], list[Any], list[Any]]:
        """
        Ghép cặp entity giữa 2 file trong cùng 1 loại (LINE, CIRCLE...).

        Thuật toán tham lam (greedy nearest-neighbor):
        1. Tính khoảng cách vị trí đại diện giữa MỌI cặp (entity_a, entity_b).
        2. Sắp xếp toàn bộ các cặp theo khoảng cách tăng dần.
        3. Duyệt lần lượt, ghép cặp nếu cả 2 entity chưa được ghép và khoảng
           cách không vượt ngưỡng an toàn (_MAX_MATCH_DISTANCE_FACTOR x tolerance).

        Chọn cách này vì đơn giản, không cần thư viện tối ưu hóa (vd. thuật
        toán Hungarian cho bài toán ghép cặp tối ưu toàn cục), và cho kết quả
        đủ tốt với quy mô bản vẽ xây dựng thông thường: phần lớn thay đổi giữa
        2 lần vẽ là entity bị dịch chuyển một chút hoặc thêm/bớt vài entity,
        nên ghép "gần nhất trước" thường ra đúng cặp tương ứng thực tế.
        """
        max_distance = self.tolerance_mm * _MAX_MATCH_DISTANCE_FACTOR

        candidates: list[tuple[float, int, int]] = []
        for idx_a, entity_a in enumerate(group_a):
            pos_a = self._position(entity_a)
            for idx_b, entity_b in enumerate(group_b):
                pos_b = self._position(entity_b)
                distance = _euclidean(pos_a, pos_b)
                if distance <= max_distance:
                    candidates.append((distance, idx_a, idx_b))

        candidates.sort(key=lambda c: c[0])

        matched_a: set[int] = set()
        matched_b: set[int] = set()
        matches: list[tuple[Any, Any]] = []
        for _distance, idx_a, idx_b in candidates:
            if idx_a in matched_a or idx_b in matched_b:
                continue
            matched_a.add(idx_a)
            matched_b.add(idx_b)
            matches.append((group_a[idx_a], group_b[idx_b]))

        unmatched_a = [e for i, e in enumerate(group_a) if i not in matched_a]
        unmatched_b = [e for i, e in enumerate(group_b) if i not in matched_b]
        return matches, unmatched_a, unmatched_b

    @staticmethod
    def _position(entity: Any) -> tuple[float, float]:
        """Tọa độ (x, y) đại diện cho vị trí của entity, dùng để ghép cặp."""
        dxftype = entity.dxftype()
        if dxftype == "LINE":
            start = entity.dxf.start
            end = entity.dxf.end
            return ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2)
        if dxftype in ("CIRCLE", "ARC"):
            return _point2d(entity.dxf.center)
        if dxftype == "LWPOLYLINE":
            points = list(entity.get_points())
            if not points:
                return (0.0, 0.0)
            avg_x = sum(p[0] for p in points) / len(points)
            avg_y = sum(p[1] for p in points) / len(points)
            return (float(avg_x), float(avg_y))
        # TEXT, MTEXT, INSERT đều có điểm chèn (insertion point)
        return _point2d(entity.dxf.insert)

    @staticmethod
    def _extract_props(entity: Any) -> dict[str, Any]:
        """Trích các thuộc tính cần so sánh của entity, tùy theo loại."""
        dxftype = entity.dxftype()
        props: dict[str, Any] = {"layer": entity.dxf.layer}

        if dxftype == "LINE":
            props["start"] = _point2d(entity.dxf.start)
            props["end"] = _point2d(entity.dxf.end)
        elif dxftype == "CIRCLE":
            props["center"] = _point2d(entity.dxf.center)
            props["radius"] = float(entity.dxf.radius)
        elif dxftype == "ARC":
            props["center"] = _point2d(entity.dxf.center)
            props["radius"] = float(entity.dxf.radius)
            props["start_angle"] = float(entity.dxf.start_angle)
            props["end_angle"] = float(entity.dxf.end_angle)
        elif dxftype == "LWPOLYLINE":
            props["points"] = [_point2d(p) for p in entity.get_points()]
        elif dxftype == "TEXT":
            props["insert"] = _point2d(entity.dxf.insert)
            props["text"] = entity.dxf.text
        elif dxftype == "MTEXT":
            props["insert"] = _point2d(entity.dxf.insert)
            props["text"] = entity.text
        elif dxftype == "INSERT":
            props["insert"] = _point2d(entity.dxf.insert)
            props["block"] = entity.dxf.name

        return props

    def _diff_props(self, props_a: dict, props_b: dict) -> tuple[str | None, str | None]:
        """
        So sánh chi tiết 2 entity đã ghép cặp, trả về mô tả khác biệt (nếu có).

        - Toạ độ/bán kính: chỉ coi là thay đổi khi lệch nhau quá tolerance_mm.
        - Góc (ARC): chỉ coi là thay đổi khi lệch nhau quá _ANGLE_TOLERANCE_DEG.
        - Layer/nội dung text/tên block: so sánh đúng bằng (không áp dụng
          tolerance vì đây không phải giá trị số đo tọa độ).
        """
        old_parts: list[str] = []
        new_parts: list[str] = []

        if props_a["layer"] != props_b["layer"]:
            old_parts.append(f"layer '{props_a['layer']}'")
            new_parts.append(f"layer '{props_b['layer']}'")

        for key in ("start", "end", "center", "insert"):
            if key in props_a and _euclidean(props_a[key], props_b[key]) > self.tolerance_mm:
                old_parts.append(f"{key} {_fmt_point(props_a[key])}")
                new_parts.append(f"{key} {_fmt_point(props_b[key])}")

        if "radius" in props_a and abs(props_a["radius"] - props_b["radius"]) > self.tolerance_mm:
            old_parts.append(f"bán kính {props_a['radius']:.2f}")
            new_parts.append(f"bán kính {props_b['radius']:.2f}")

        for key in ("start_angle", "end_angle"):
            if key in props_a and abs(props_a[key] - props_b[key]) > _ANGLE_TOLERANCE_DEG:
                old_parts.append(f"{key} {props_a[key]:.2f}°")
                new_parts.append(f"{key} {props_b[key]:.2f}°")

        if "text" in props_a and props_a["text"] != props_b["text"]:
            old_parts.append(f"nội dung '{props_a['text']}'")
            new_parts.append(f"nội dung '{props_b['text']}'")

        if "block" in props_a and props_a["block"] != props_b["block"]:
            old_parts.append(f"block '{props_a['block']}'")
            new_parts.append(f"block '{props_b['block']}'")

        if "points" in props_a:
            points_a, points_b = props_a["points"], props_b["points"]
            if len(points_a) != len(points_b):
                old_parts.append(f"{len(points_a)} đỉnh")
                new_parts.append(f"{len(points_b)} đỉnh")
            elif any(_euclidean(pa, pb) > self.tolerance_mm for pa, pb in zip(points_a, points_b)):
                old_parts.append(f"tọa độ đỉnh {[_fmt_point(p) for p in points_a]}")
                new_parts.append(f"tọa độ đỉnh {[_fmt_point(p) for p in points_b]}")

        if not old_parts:
            return None, None
        return "; ".join(old_parts), "; ".join(new_parts)

    @staticmethod
    def _location(dxftype: str, props: dict) -> str:
        """Mô tả vị trí dễ hiểu, ví dụ: "Layer 'KETCAU', LINE tại (120.5, 340.2)"."""
        pos = props.get("start") or props.get("center") or props.get("insert")
        if pos is None and props.get("points"):
            pos = props["points"][0]
        pos_str = _fmt_point(pos) if pos else "(?)"
        return f"Layer '{props['layer']}', {dxftype} tại {pos_str}"

    @staticmethod
    def _describe(props: dict) -> str:
        """Mô tả đầy đủ 1 entity, dùng cho old_value/new_value của ADDED/REMOVED."""
        parts = [f"layer '{props['layer']}'"]
        if "start" in props:
            parts.append(f"start {_fmt_point(props['start'])}")
            parts.append(f"end {_fmt_point(props['end'])}")
        if "center" in props:
            parts.append(f"center {_fmt_point(props['center'])}")
        if "radius" in props:
            parts.append(f"bán kính {props['radius']:.2f}")
        if "start_angle" in props:
            parts.append(f"góc {props['start_angle']:.2f}°-{props['end_angle']:.2f}°")
        if "points" in props:
            parts.append(f"{len(props['points'])} đỉnh")
        if "insert" in props:
            parts.append(f"vị trí {_fmt_point(props['insert'])}")
        if "text" in props:
            parts.append(f"nội dung '{props['text']}'")
        if "block" in props:
            parts.append(f"block '{props['block']}'")
        return ", ".join(parts)
