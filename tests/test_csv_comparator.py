"""
Unit test cho CsvComparator.

Chạy bằng lệnh: pytest tests/
"""

import csv
from pathlib import Path

import pytest

from app.core.comparators.csv_comparator import CsvComparator
from app.core.models.diff_result import ChangeType


def _write_csv(path: Path, rows: list[list[str]]) -> None:
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerows(rows)


@pytest.fixture
def comparator() -> CsvComparator:
    return CsvComparator()


def test_identical_files_have_no_diff(tmp_path: Path, comparator: CsvComparator) -> None:
    rows = [["ten", "gia"], ["Xi mang", "100000"]]
    file_a = tmp_path / "a.csv"
    file_b = tmp_path / "b.csv"
    _write_csv(file_a, rows)
    _write_csv(file_b, rows)

    result = comparator.compare(str(file_a), str(file_b))

    assert result.is_identical
    assert len(result.items) == 0


def test_detects_modified_cell(tmp_path: Path, comparator: CsvComparator) -> None:
    file_a = tmp_path / "a.csv"
    file_b = tmp_path / "b.csv"
    _write_csv(file_a, [["ten", "gia"], ["Xi mang", "100000"]])
    _write_csv(file_b, [["ten", "gia"], ["Xi mang", "120000"]])

    result = comparator.compare(str(file_a), str(file_b))

    assert len(result.items) == 1
    assert result.items[0].change_type == ChangeType.MODIFIED
    assert result.items[0].old_value == "100000"
    assert result.items[0].new_value == "120000"


def test_detects_added_row(tmp_path: Path, comparator: CsvComparator) -> None:
    file_a = tmp_path / "a.csv"
    file_b = tmp_path / "b.csv"
    _write_csv(file_a, [["ten", "gia"], ["Xi mang", "100000"]])
    _write_csv(file_b, [["ten", "gia"], ["Xi mang", "100000"], ["Cat", "50000"]])

    result = comparator.compare(str(file_a), str(file_b))

    assert len(result.items) == 1
    assert result.items[0].change_type == ChangeType.ADDED


def test_validate_rejects_missing_file(tmp_path: Path, comparator: CsvComparator) -> None:
    file_a = tmp_path / "a.csv"
    _write_csv(file_a, [["ten"], ["Xi mang"]])

    is_valid, message = comparator.validate_files(str(file_a), str(tmp_path / "khong_ton_tai.csv"))

    assert not is_valid
    assert "Không tìm thấy file" in message
