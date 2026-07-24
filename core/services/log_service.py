"""
日志读取服务
"""

import logging
from pathlib import Path

from django.conf import settings

from core.services.mixins import error_response, safe_execute

logger = logging.getLogger(__name__)


class LogService:
    """日志读取服务"""

    LOG_DIR = Path(settings.BASE_DIR) / "storage" / "logs"

    LOG_FILES = {
        "cimf": "cimf.log",
        "error": "error.log",
        "security": "security.log",
    }

    # ===== 读日志功能 =====

    @classmethod
    def get_log_files(cls) -> list[dict]:
        """获取日志文件列表及基本信息"""
        files = []
        for key, filename in cls.LOG_FILES.items():
            filepath = cls.LOG_DIR / filename
            info = {
                "key": key,
                "name": filename,
                "exists": filepath.exists(),
                "size": filepath.stat().st_size if filepath.exists() else 0,
            }
            if info["exists"]:
                try:
                    info["size"] = filepath.stat().st_size
                except OSError:
                    info["size"] = 0
            files.append(info)
        return files

    @classmethod
    def read_log(cls, log_type: str, page: int = 1, page_size: int = 100, level: str | None = None) -> dict:
        """读取日志，支持分页和级别筛选"""
        all_lines = cls._read_log_file(log_type)
        if all_lines is None:
            return error_response("无法读取日志", lines=[], total=0, page=page, page_size=page_size)

        if level and level != "all":
            all_lines = [line for line in all_lines if level.upper() in line.upper()]

        total_filtered = len(all_lines)

        start = (page - 1) * page_size
        end = start + page_size
        page_lines = all_lines[start:end]

        parsed_lines = [
            {"line_num": i, "content": line.rstrip("\n")} for i, line in enumerate(page_lines, start=start + 1)
        ]

        return {
            "success": True,
            "lines": parsed_lines,
            "total": total_filtered,
            "page": page,
            "page_size": page_size,
            "total_pages": (total_filtered + page_size - 1) // page_size,
        }

    @classmethod
    def _read_log_file(cls, log_type: str) -> list[str] | None:
        """读取日志文件的原始行列表；文件不存在或读取失败时返回 None"""
        filename = cls.LOG_FILES.get(log_type)
        if not filename:
            return None

        filepath = cls.LOG_DIR / filename
        if not filepath.exists():
            return None

        lines = safe_execute(
            lambda: filepath.open(encoding="utf-8", errors="replace").readlines(),
            error_return=None,
            log_msg="读取日志文件失败",
            logger=logger,
        )
        return lines

    @classmethod
    def get_log_stats(cls, log_type: str) -> dict:
        """获取日志统计（总行数、各级别数量）"""
        lines = cls._read_log_file(log_type)
        if lines is None:
            return {"total": 0, "levels": {}}

        total = len(lines)
        levels = {"DEBUG": 0, "INFO": 0, "WARNING": 0, "ERROR": 0}

        for line in lines:
            for lvl in levels:
                if lvl in line.upper():
                    levels[lvl] += 1
                    break

        return {"total": total, "levels": levels}


