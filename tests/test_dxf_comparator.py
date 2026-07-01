"""
Unit test cho DxfComparator.

Chạy bằng lệnh: pytest tests/
"""

from pathlib import Path

import ezdxf
import pytest

from app.core.comparators.dxf_comparator import DxfComparator
from app.core.models.diff_result import ChangeType


def _new_doc():
    return ezdxf.new(dxfversion="R2010")


@pytest.fixture
def comparator() -> DxfComparator:
    return DxfComparator(tolerance_mm=1.0)


def test_identical_files_have_no_diff(tmp_path: Path, comparator: DxfComparator) -> None:
    doc_a = _new_doc()
    msp_a = doc_a.modelspace()
    msp_a.add_line((0, 0), (100, 0), dxfattribs={"layer": "KETCAU"})
    msp_a.add_circle((50, 50), radius=10, dxfattribs={"layer": "KETCAU"})

    doc_b = _new_doc()
    msp_b = doc_b.modelspace()
    msp_b.add_line((0, 0), (100, 0), dxfattribs={"layer": "KETCAU"})
    msp_b.add_circle((50, 50), radius=10, dxfattribs={"layer": "KETCAU"})

    file_a = tmp_path / "a.dxf"
    file_b = tmp_path / "b.dxf"
    doc_a.saveas(str(file_a))
    doc_b.saveas(str(file_b))

    result = comparator.compare(str(file_a), str(file_b))

    assert result.is_identical
    assert len(result.items) == 0


def test_detects_moved_entity(tmp_path: Path, comparator: DxfComparator) -> None:
    doc_a = _new_doc()
    doc_a.modelspace().add_line((0, 0), (100, 0), dxfattribs={"layer": "KETCAU"})

    doc_b = _new_doc()
    # Dịch chuyển cả 2 đầu đoạn thẳng 5mm (> tolerance 1mm của comparator)
    doc_b.modelspace().add_line((5, 0), (105, 0), dxfattribs={"layer": "KETCAU"})

    file_a = tmp_path / "a.dxf"
    file_b = tmp_path / "b.dxf"
    doc_a.saveas(str(file_a))
    doc_b.saveas(str(file_b))

    result = comparator.compare(str(file_a), str(file_b))

    assert len(result.items) == 1
    assert result.items[0].change_type == ChangeType.MODIFIED


def test_detects_added_entity(tmp_path: Path, comparator: DxfComparator) -> None:
    doc_a = _new_doc()
    doc_a.modelspace().add_line((0, 0), (100, 0), dxfattribs={"layer": "KETCAU"})

    doc_b = _new_doc()
    doc_b.modelspace().add_line((0, 0), (100, 0), dxfattribs={"layer": "KETCAU"})
    doc_b.modelspace().add_circle((200, 200), radius=20, dxfattribs={"layer": "KETCAU"})

    file_a = tmp_path / "a.dxf"
    file_b = tmp_path / "b.dxf"
    doc_a.saveas(str(file_a))
    doc_b.saveas(str(file_b))

    result = comparator.compare(str(file_a), str(file_b))

    assert len(result.items) == 1
    assert result.items[0].change_type == ChangeType.ADDED


def test_detects_removed_entity(tmp_path: Path, comparator: DxfComparator) -> None:
    doc_a = _new_doc()
    doc_a.modelspace().add_line((0, 0), (100, 0), dxfattribs={"layer": "KETCAU"})
    doc_a.modelspace().add_circle((200, 200), radius=20, dxfattribs={"layer": "KETCAU"})

    doc_b = _new_doc()
    doc_b.modelspace().add_line((0, 0), (100, 0), dxfattribs={"layer": "KETCAU"})

    file_a = tmp_path / "a.dxf"
    file_b = tmp_path / "b.dxf"
    doc_a.saveas(str(file_a))
    doc_b.saveas(str(file_b))

    result = comparator.compare(str(file_a), str(file_b))

    assert len(result.items) == 1
    assert result.items[0].change_type == ChangeType.REMOVED


def test_within_tolerance_not_reported(tmp_path: Path, comparator: DxfComparator) -> None:
    doc_a = _new_doc()
    doc_a.modelspace().add_line((0, 0), (100, 0), dxfattribs={"layer": "KETCAU"})

    doc_b = _new_doc()
    # Lệch 0.3mm - trong phạm vi tolerance 1.0mm -> KHÔNG được báo là thay đổi
    doc_b.modelspace().add_line((0.3, 0), (100.3, 0), dxfattribs={"layer": "KETCAU"})

    file_a = tmp_path / "a.dxf"
    file_b = tmp_path / "b.dxf"
    doc_a.saveas(str(file_a))
    doc_b.saveas(str(file_b))

    result = comparator.compare(str(file_a), str(file_b))

    assert result.is_identical


def test_validate_rejects_missing_file(tmp_path: Path, comparator: DxfComparator) -> None:
    doc_a = _new_doc()
    doc_a.modelspace().add_line((0, 0), (10, 0))
    file_a = tmp_path / "a.dxf"
    doc_a.saveas(str(file_a))

    is_valid, message = comparator.validate_files(str(file_a), str(tmp_path / "khong_ton_tai.dxf"))

    assert not is_valid
    assert "Không tìm thấy file" in message


def test_validate_rejects_corrupt_file(tmp_path: Path, comparator: DxfComparator) -> None:
    doc_a = _new_doc()
    doc_a.modelspace().add_line((0, 0), (10, 0))
    file_a = tmp_path / "a.dxf"
    doc_a.saveas(str(file_a))

    corrupt_file = tmp_path / "corrupt.dxf"
    corrupt_file.write_text("day khong phai la file DXF hop le", encoding="utf-8")

    is_valid, message = comparator.validate_files(str(file_a), str(corrupt_file))

    assert not is_valid
    assert message != ""
