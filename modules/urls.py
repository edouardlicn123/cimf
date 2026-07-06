"""
模块 URL 路由配置 - 动态加载

使用动态安全加载机制，当模块文件夹不存在时自动忽略，
确保系统可以在没有任何模块的情况下启动。
"""

from importlib import import_module

from django.core.cache import cache
from django.urls import include, path

from core.module.models import Module
from core.node import views as node_views

app_name = "modules"


def try_include_module(module_slug, prefix=""):
    """尝试动态导入模块 URL，失败则返回空列表"""
    try:
        import_module(f"modules.{module_slug}.urls")
        return [path(f"{prefix}{module_slug}/", include(f"modules.{module_slug}.urls"))]
    except (ImportError, ModuleNotFoundError, AttributeError):
        return []


def get_installed_module_slugs():
    """动态获取所有已安装模块的信息"""
    cache_key = "modules.installed_slugs"
    slugs = cache.get(cache_key)
    if slugs is not None:
        return slugs
    try:
        modules = Module.objects.filter(is_installed=True, is_active=True)
        slugs = [(m.module_id, m.module_type) for m in modules]
    except Exception:
        slugs = []
    cache.set(cache_key, slugs, 300)
    return slugs


def get_dynamic_routes():
    """根据模块类型分前缀动态挂载模块路由"""
    modules = get_installed_module_slugs()
    routes = []
    for mod_slug, mod_type in modules:
        if mod_type == "node":
            # node 类型由 core/node/urls.py 分发，跳过
            continue
        elif mod_type == "tool":
            # tool 类型挂载到 modules/<slug>/ 供 API 和子页面访问
            routes.extend(try_include_module(mod_slug))
        elif mod_type == "system":
            # system 类型挂载到 system/<slug>/
            routes.extend(try_include_module(mod_slug, prefix="system/"))
        else:
            # 其它类型（已挂载在 modules/ 下）
            routes.extend(try_include_module(mod_slug))
    return routes


urlpatterns = [
    *get_dynamic_routes(),
    path("api/taxonomy-items/", node_views.taxonomy_items_api, name="taxonomy_items_api"),
]
