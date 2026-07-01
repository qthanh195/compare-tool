"""
Logger dùng chung cho toàn bộ ứng dụng.

Ghi log ra file (trong thư mục Documents/CompareTool_Reports/logs) để khi
người dùng báo lỗi, có thể xin họ gửi file log thay vì phải chụp màn hình
traceback khó đọc.
"""

import logging
from pathlib import Path

from app.config.settings import DEFAULT_OUTPUT_DIR


def get_logger(name: str) -> logging.Logger:
    """Trả về logger đã cấu hình sẵn, dùng chung format cho toàn bộ app."""
    log_dir = DEFAULT_OUTPUT_DIR / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)
    if logger.handlers:
        # Tránh add handler trùng lặp nếu get_logger được gọi nhiều lần
        return logger

    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler(log_dir / "app.log", encoding="utf-8")
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
