"""
健康检查视图模块
"""

import os
import time
from pathlib import Path

from django.core.cache import cache
from django.db import connection
from django.http import JsonResponse
from django.utils import timezone

from core.constants import VERSION_MAJOR, VERSION_MINOR
from core.decorators import login_required
from core.services import VersionService


def _run_check(checks, name, fn, on_error_status="degraded"):
    overall = "ok"
    try:
        fn()
        checks[name] = "ok"
    except Exception as e:
        checks[name] = f"error: {e!s}"
        overall = on_error_status
    return overall


@login_required
def health_check(request):  # noqa: ARG001
    start_time = time.time()

    checks = {
        "status": "ok",
        "version": f"{VERSION_MAJOR}.{VERSION_MINOR:03d}",
        "timestamp": timezone.now().isoformat(),
    }
    overall_status = "ok"

    def _check_db():
        connection.ensure_connection()

    result = _run_check(checks, "database", _check_db, "error")
    if result != "ok":
        overall_status = result

    def _check_cache():
        cache.set("_health_check", "ok", 10)
        if cache.get("_health_check") != "ok":
            raise RuntimeError("degraded")

    result = _run_check(checks, "cache", _check_cache)
    if result != "ok":
        overall_status = result

    def _check_storage():
        storage_path = Path(__file__).parent.parent / "storage"
        if not storage_path.exists():
            raise RuntimeError("missing")

    result = _run_check(checks, "storage", _check_storage)
    if result != "ok":
        overall_status = result

    checks["uptime_ms"] = round((time.time() - start_time) * 1000, 2)
    checks["status"] = overall_status

    status_code = 200 if overall_status == "ok" else 503
    return JsonResponse(checks, status=status_code)


@login_required
def detailed_health_check(request):  # noqa: ARG001
    start_time = time.time()

    checks = {
        "status": "ok",
        "version": f"{VERSION_MAJOR}.{VERSION_MINOR:03d}",
    }
    overall_status = "ok"

    def _check_db():
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")

    result = _run_check(checks, "database", _check_db, "error")
    if result != "ok":
        overall_status = result

    def _check_tables():
        from core.models import SystemSetting, User  # noqa: PLC0415

        checks["tables"] = {
            "users": User.objects.count(),
            "settings": SystemSetting.objects.count(),
        }

    result = _run_check(checks, "tables", _check_tables)
    if result != "ok":
        overall_status = result

    def _check_modules():
        from core.node.models import Node, NodeType  # noqa: PLC0415

        checks["modules"] = {
            "node_types": NodeType.objects.count(),
            "nodes": Node.objects.count(),
        }

    _run_check(checks, "modules", _check_modules)

    def _check_storage():
        storage_path = Path(__file__).parent.parent / "storage"
        if not storage_path.exists():
            raise RuntimeError("missing")
        try:
            stat = os.statvfs(str(storage_path))
            free_space = stat.f_bavail * stat.f_frsize / (1024**3)
            checks["disk_free_gb"] = round(free_space, 2)
        except Exception:
            pass

    result = _run_check(checks, "storage", _check_storage)
    if result != "ok":
        overall_status = result

    checks["uptime_ms"] = round((time.time() - start_time) * 1000, 2)
    checks["status"] = overall_status

    status_code = 200 if overall_status == "ok" else 503
    return JsonResponse(checks, status=status_code)


@login_required
def api_version(request):  # noqa: ARG001
    """API 版本信息"""
    return JsonResponse(VersionService.get_info())
