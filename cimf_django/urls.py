"""
URL configuration for cimf_django project.
"""

from django.contrib import admin
from django.urls import include, path

from core.importexport.urls import urlpatterns_all as importexport_urls

from .views import serve_media

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls", namespace="core")),
    # 模块管理（必须在 modules/ 之前，避免被动态路由匹配）
    path("modules/manage/", include(("core.module.urls", "module"), namespace="module")),
    path("modules/market/", include("core.marketplace.urls", namespace="market")),
    path("modules/", include("modules.urls", namespace="modules")),
    path("nodes/", include("core.node.urls", namespace="node")),
    # 导入导出
    path("importexport/", include((importexport_urls, "importexport"), namespace="importexport")),
    path("api/v1/", include("core.api_urls", namespace="api")),
    # 媒体文件静态服务（WhatsApp 媒体发送依赖 WABridge 拉取 /media/ 下的文件，
    # dev/prod 均无条件挂载，不受 DEBUG 开关影响）
    path("media/<path:path>", serve_media, name="media"),
]
