"""
Comparator dùng để so sánh 2 file CSV.

Cách hoạt động:
1. Đọc 2 file CSV bằng pandas
2. Nếu số dòng/cột khác nhau -> báo các dòng thừa/thiếu (ADDED/REMOVED)
3. Với các dòng có cùng vị trí -> so từng ô một, ô nào khác giá trị thì
   ghi nhận là MODIFIED
"""

import os

import pandas as pd

from app.core.comparators.base_comparator import BaseComparator
from app.core.models.diff_result import ChangeType, DiffItem, DiffResult


class CsvComparator(BaseComparator):
    """So sánh 2 file CSV theo từng dòng, từng cột."""

    def validate_files(self, file_a: str, file_b: str) -> tuple[bool, str]:
        for path in (file_a, file_b):
            if not os.path.exists(path):
                return False, f"Không tìm thấy file: {path}"
            if not path.lower().endswith(".csv"):
                return False, f"File không đúng định dạng .csv: {path}"
        return True, ""

    def compare(self, file_a: str, file_b: str) -> DiffResult:
        result = DiffResult(file_a=file_a, file_b=file_b)

        # encoding="utf-8-sig" để đọc đúng file CSV xuất từ Excel tiếng Việt
        df_a = pd.read_csv(file_a, dtype=str, encoding="utf-8-sig").fillna("")
        df_b = pd.read_csv(file_b, dtype=str, encoding="utf-8-sig").fillna("")

        max_rows = max(len(df_a), len(df_b))

        # Trường hợp file B có nhiều dòng hơn -> các dòng thừa là ADDED
        # Trường hợp file A có nhiều dòng hơn -> các dòng thừa là REMOVED
        for row_idx in range(max_rows):
            row_in_a = row_idx < len(df_a)
            row_in_b = row_idx < len(df_b)

            if row_in_a and not row_in_b:
                result.items.append(
                    DiffItem(
                        location=f"Dòng {row_idx + 2}",  # +2: bù cho header + index từ 0
                        change_type=ChangeType.REMOVED,
                        old_value=str(df_a.iloc[row_idx].to_dict()),
                        new_value=None,
                    )
                )
                continue

            if row_in_b and not row_in_a:
                result.items.append(
                    DiffItem(
                        location=f"Dòng {row_idx + 2}",
                        change_type=ChangeType.ADDED,
                        old_value=None,
                        new_value=str(df_b.iloc[row_idx].to_dict()),
                    )
                )
                continue

            # Cả 2 file đều có dòng này -> so từng cột
            common_columns = [c for c in df_a.columns if c in df_b.columns]
            for col in common_columns:
                val_a = df_a.iloc[row_idx][col]
                val_b = df_b.iloc[row_idx][col]
                if val_a != val_b:
                    result.items.append(
                        DiffItem(
                            location=f"Dòng {row_idx + 2}, cột '{col}'",
                            change_type=ChangeType.MODIFIED,
                            old_value=val_a,
                            new_value=val_b,
                        )
                    )

        return result
