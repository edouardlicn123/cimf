"""
ReaderService - 文件读取服务

提供通用的文件读取功能，支持 CSV/Excel 格式和编码检测
"""

import csv
import io
import logging

from openpyxl import load_workbook

logger = logging.getLogger(__name__)

try:
    import chardet
except ImportError:
    chardet = None

FORMAT_CSV = "csv"
FORMAT_XLSX = "xlsx"
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


def validate_file_size(file):
    """验证文件大小不超过限制"""
    if hasattr(file, "size") and file.size > MAX_FILE_SIZE:
        raise ValueError(
            f"文件过大（{file.size / 1024 / 1024:.1f}MB），最大允许 {MAX_FILE_SIZE / 1024 / 1024:.0f}MB"
        )


def detect_encoding(raw: bytes) -> str:
    """检测文件编码"""
    if chardet:
        try:
            result = chardet.detect(raw)
            encoding = result.get("encoding", "") or ""
            if encoding.lower().replace("-", "") in ("utf8", "utf8sig", "ascii"):
                return "utf-8"
            if encoding:
                return encoding
        except Exception:  # noqa: S110 — encoding detection best-effort
            pass
    # 回退：尝试常见编码
    for enc in ("utf-8-sig", "utf-8", "gbk", "gb2312", "latin-1"):
        try:
            raw.decode(enc)
            return enc
        except (UnicodeDecodeError, LookupError):
            continue
    return "utf-8"


def read_csv(file) -> tuple[list[str], list[list[str]]]:
    """读取 CSV 文件，含编码检测"""

    file_content = file.read()
    if hasattr(file, "seek"):
        file.seek(0)
    if not file_content:
        return [], []
    encoding = detect_encoding(file_content)
    try:
        decoded_file = file_content.decode(encoding)
    except (UnicodeDecodeError, LookupError):
        decoded_file = file_content.decode("utf-8", errors="replace")
    reader = csv.reader(decoded_file.splitlines())
    rows = list(reader)

    if not rows:
        return [], []

    headers = rows[0] if rows else []
    data_rows = rows[1:] if len(rows) > 1 else []

    return headers, data_rows


def read_xlsx(file) -> tuple[list[str], list[list[str]]]:
    """读取 XLSX 文件"""

    file_content = file.read()
    if hasattr(file, "seek"):
        file.seek(0)
    wb = load_workbook(filename=io.BytesIO(file_content), data_only=True)
    ws = wb.active

    rows = list(ws.values)

    if not rows:
        return [], []

    headers = [str(h) if h is not None else "" for h in rows[0]]
    data_rows = [[str(cell) if cell is not None else "" for cell in row] for row in rows[1:]]

    return headers, data_rows


def read_file(file, format: str) -> tuple[list[str], list[list[str]]]:
    """读取文件内容，含大小检查"""
    validate_file_size(file)
    if format == FORMAT_CSV:
        return read_csv(file)
    else:
        return read_xlsx(file)
