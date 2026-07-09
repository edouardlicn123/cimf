import csv
from pathlib import Path

from django.http import HttpResponse, JsonResponse


def csv_response(headers: list[str], rows: list[list], filename: str, sanitize: bool = True) -> HttpResponse:
    response = HttpResponse(content_type="text/csv; charset=utf-8-sig")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    writer.writerow(headers)

    for row in rows:
        out_row = [_sanitize_csv_cell(cell) for cell in row] if sanitize else row
        writer.writerow(out_row)

    return response


def validate_upload(file_obj, allowed_mimes=None, max_size=None, allowed_exts=None) -> tuple[bool, str]:
    """验证上传文件，返回 (是否合法, 错误消息)"""
    if allowed_mimes is not None and file_obj.content_type not in allowed_mimes:
        return False, f"文件类型不合法，仅支持 {', '.join(allowed_mimes)}"

    if max_size is not None and file_obj.size > max_size:
        return False, f"文件大小不能超过 {max_size // (1024 * 1024)}MB"

    if allowed_exts is not None:
        ext = Path(file_obj.name).suffix.lower()
        if ext not in allowed_exts:
            return False, f"文件扩展名不合法，仅支持 {', '.join(allowed_exts)}"

    return True, ""


def _sanitize_csv_cell(value) -> str:
    s = str(value)
    if s and s[0] in ("=", "+", "-", "@"):
        return "\t" + s
    return s


def json_success(data=None, message=None, status=200, extra=None):
    resp = {"success": True}
    if data is not None:
        resp["data"] = data
    if message is not None:
        resp["message"] = message
    if extra is not None:
        resp.update(extra)
    return JsonResponse(resp, status=status)


def json_error(message, status=400, data=None):
    resp = {"success": False, "error": message}
    if data is not None:
        resp["data"] = data
    return JsonResponse(resp, status=status)


def no_cache_json_response(data, status=200):
    response = JsonResponse(data, status=status)
    response["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response["Pragma"] = "no-cache"
    response["Expires"] = "0"
    return response
