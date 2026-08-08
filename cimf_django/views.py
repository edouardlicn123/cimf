"""项目级视图

serve_media：媒体文件静态服务。dev/prod 均无条件挂载，
WABridge 拉取 /media/ 下的文件依赖此路由，不受 DEBUG 开关影响。
"""

from django.conf import settings
from django.http import FileResponse, Http404

from core.utils.response import json_error


def serve_media(request, path: str):
    """流式返回 MEDIA_ROOT 下的文件，带路径穿越防护

    /media/ 已在 GlobalLoginRequiredMiddleware 白名单中，
    WABridge 无 session 即可拉取媒体文件。
    """
    root = settings.MEDIA_ROOT.resolve()
    target = (root / path).resolve()
    if not target.is_relative_to(root) or not target.is_file():
        if "application/json" in request.headers.get("Accept", ""):
            return json_error("文件不存在", 404)
        raise Http404("文件不存在")
    return FileResponse(target.open("rb"))
