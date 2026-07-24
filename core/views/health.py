"""
健康检查视图模块
"""

import logging
import os
import time
from pathlib import Path

from django.core.cache import cache
from django.db import connection
from django.utils import timezone

from core.constants import VERSION_MAJOR, VERSION_MINOR
from core.decorators import login_required_json
from core.services import SettingsService, UserService, VersionService
from core.utils.response import json_success

logger = logging.getLogger(__name__)


def _run_check(checks, name, fn, overall_status=None):
    try:
        fn()
        checks[name] = "ok"
    except Exception as e:
        logger.warning("健康检查失败: %s — %s", name, e, exc_info=True)
        checks[name] = f"error: {e!s}"
        if overall_status is not None:
            overall_status[0] = "error"


def _build_check_base():
    return {
        "status": "ok",
        "version": f"{VERSION_MAJOR}.{VERSION_MINOR:03d}",
        "timestamp": timezone.now().isoformat(),
    }


def _finalize_check(checks, start_time, overall_status):
    checks["uptime_ms"] = round((time.time() - start_time) * 1000, 2)
    checks["status"] = overall_status[0]
    status_code = 200 if overall_status[0] == "ok" else 503
    return json_success(data=checks, status=status_code)


@login_required_json
def health_check(request):  # noqa: ARG001
    start_time = time.time()
    checks = _build_check_base()
    overall_status = ["ok"]

    _run_check(checks, "database", connection.ensure_connection, overall_status)

    def _check_cache():
        cache.set("_health_check", "ok", 10)
        if cache.get("_health_check") != "ok":
            raise RuntimeError("degraded")

    _run_check(checks, "cache", _check_cache, overall_status)

    def _check_storage():
        storage_path = Path(__file__).parent.parent / "storage"
        if not storage_path.exists():
            raise RuntimeError("missing")

    _run_check(checks, "storage", _check_storage, overall_status)

    return _finalize_check(checks, start_time, overall_status)


@login_required_json
def detailed_health_check(request):  # noqa: ARG001
    start_time = time.time()
    checks = _build_check_base()
    overall_status = ["ok"]

    def _check_db():
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")

    _run_check(checks, "database", _check_db, overall_status)

    def _check_tables():
        checks["tables"] = {
            "users": UserService.get_count(),
            "settings": SettingsService.get_count(),
        }

    _run_check(checks, "tables", _check_tables, overall_status)

    def _check_modules():
        from core.node.services import NodeService, NodeTypeService  # noqa: PLC0415

        checks["modules"] = {
            "node_types": NodeTypeService.get_count(),
            "nodes": NodeService.get_count(),
        }

    _run_check(checks, "modules", _check_modules, overall_status)

    def _check_storage():
        storage_path = Path(__file__).parent.parent / "storage"
        if not storage_path.exists():
            raise RuntimeError("missing")
        try:
            stat = os.statvfs(str(storage_path))
            free_space = stat.f_bavail * stat.f_frsize / (1024**3)
            checks["disk_free_gb"] = round(free_space, 2)
        except Exception:  # noqa: S110 — health check best-effort
            pass

    _run_check(checks, "storage", _check_storage, overall_status)

    return _finalize_check(checks, start_time, overall_status)


@login_required_json
def api_version(request):  # noqa: ARG001
    """API 版本信息"""
    return json_success(data=VersionService.get_info())
