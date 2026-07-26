"""
卡片 API 模块
"""

import json
import logging

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.template import engines
from django.views.decorators.http import require_GET

from core.constants import DEFAULT_NAV_CARDS
from core.decorators import api_get_view, api_post_view, json_body
from core.module.services.module_query_service import ModuleQueryService
from core.module.services.module_registry_service import ModuleRegistryService
from core.services import SettingsService, UserService
from core.utils.response import json_error, json_success, no_cache_json_response

logger = logging.getLogger(__name__)


def _load_active_card_modules():
    """加载启用了 frontpage_card 的模块信息列表"""
    from core.module.services.module_service import ModuleService  # noqa: PLC0415

    results = []
    active_modules = ModuleQueryService.get_active()
    for node_module in active_modules:
        if not node_module.path:
            continue
        try:
            mod_info = ModuleService.load_module_info(node_module.path)
            if mod_info and mod_info.get("frontpage_card", False) and "dashboard_cards" in mod_info:
                results.append(
                    {
                        "module": node_module,
                        "mod_info": mod_info,
                        "cards": mod_info["dashboard_cards"],
                    }
                )
        except Exception as e:
            logger.warning("模块信息加载失败: module=%s, error=%s", node_module.module_id, e, exc_info=True)
    return results


def _collect_module_stats(module_path: str) -> dict:
    """收集模块统计数据"""
    try:
        service_mod = ModuleRegistryService.import_module_sub(module_path, "services")
        for attr_name in dir(service_mod):
            attr = getattr(service_mod, attr_name)
            if attr_name.endswith("Service") and hasattr(attr, "get_count") and getattr(attr, "model_class", None) is not None:
                return {
                    "total": attr.get_count(),
                    "recent": getattr(attr, "get_recent_count", lambda _=7: 0)(7),
                }
    except Exception:
        logger.warning(f"模块统计加载失败: module={module_path}", exc_info=True)
    return {}


def _get_extra_card_context(module_path: str) -> dict:
    """获取额外的卡片上下文（如连接状态等）"""
    context = {}
    try:
        service_mod = ModuleRegistryService.import_module_sub(module_path, "services")
        for attr_name in dir(service_mod):
            attr = getattr(service_mod, attr_name)
            if attr_name.endswith("Service") and hasattr(attr, "get_status"):
                status = attr.get_status()
                if isinstance(status, dict):
                    context.update(status)
    except Exception as e:
        logger.warning("模块卡片上下文加载失败: module=%s, error=%s", module_path, e, exc_info=True)
    return context


@api_get_view
def api_dashboard_cards(request):  # noqa: ARG001
    """获取功能卡片布局"""
    setting_value = SettingsService.get_setting("user_dashboard_card_positions")
    positions = {}
    if setting_value:
        try:
            positions = json.loads(setting_value)
        except Exception as e:
            logger.warning(f"解析卡片位置配置失败: {e}", exc_info=True)
    else:
        logger.warning("配置未找到: user_dashboard_card_positions")

    default_positions = {str(i): {"module": None, "size": "medium", "config": {}} for i in range(1, 7)} | positions

    available_modules = []
    module_stats = {}
    module_contents = {}
    module_types = {}
    module_clickable = {}
    jinja2_engine = engines["jinja2"]

    for entry in _load_active_card_modules():
        node_module = entry["module"]
        mod_info = entry["mod_info"]
        module_id = node_module.module_id
        module_path = node_module.path

        available_modules.append(module_id)
        module_types[module_id] = node_module.module_type
        module_clickable[module_id] = mod_info.get("frontpage_card_clickable", True)

        if mod_info.get("dashboard_stats", False):
            stats = _collect_module_stats(module_path)
            if stats:
                module_stats[module_id] = stats

        extra_context = _get_extra_card_context(module_path)

        for card in entry["cards"]:
            if "template" not in card:
                continue
            try:
                template = jinja2_engine.get_template(card["template"])
                render_context = {
                    "module_id": module_id,
                    "module_card_color_start": card.get("color_start", "#0d6efd"),
                    "module_card_color_end": card.get("color_end", "#0a58ca"),
                }
                stats = module_stats.get(module_id, {})
                if stats:
                    render_context["total"] = stats.get("total", 0)
                    render_context["recent"] = stats.get("recent", 0)
                render_context.update(extra_context)

                rendered = template.render(render_context)
                if module_id in module_contents:
                    module_contents[module_id] += rendered
                else:
                    module_contents[module_id] = rendered
            except Exception as e:
                logger.warning(f"卡片模板渲染失败: module={module_id}, error={e}", exc_info=True)
            # 收集所有卡片，不下拉列表

    return no_cache_json_response(
        {
            "success": True,
            "data": {
                "positions": default_positions,
                "available_modules": available_modules,
                "module_types": module_types,
                "module_stats": module_stats,
                "module_contents": module_contents,
                "module_clickable": module_clickable,
            },
        }
    )


@api_post_view
@json_body
def api_dashboard_cards_save(request):
    """保存功能卡片布局"""
    try:
        positions = request.json_data.get("positions", {})

        SettingsService.save_setting(
            key="user_dashboard_card_positions",
            value=json.dumps(positions),
            description="用户首页功能卡片布局",
        )

        return json_success(message="布局已保存")
    except Exception as e:
        logger.error("保存卡片布局失败: %s", e, exc_info=True)
        return json_error("保存布局失败", 400)


@api_get_view
def api_nav_cards(request):
    """获取用户导航卡片"""
    try:
        cards = UserService.get_navigation_cards(request.user.id)
        if not cards:
            cards = DEFAULT_NAV_CARDS
        return json_success(extra={"cards": cards, "max": 12})
    except Exception as e:
        logger.error("获取导航卡片失败: %s", e, exc_info=True)
        return json_error("获取导航卡片失败", 400)


@api_post_view
@json_body
def api_nav_cards_save(request):
    """保存用户导航卡片"""
    try:
        cards = request.json_data.get("cards", [])

        if len(cards) > 12:
            return json_error("最多只能添加12个导航卡片", 400)

        UserService.save_navigation_cards(request.user.id, cards)
        return json_success(message="导航卡片已保存")
    except Exception as e:
        logger.error("保存导航卡片失败: %s", e, exc_info=True)
        return json_error("保存导航卡片失败", 400)


@login_required
@require_GET
def navigation_settings(request):
    """导航卡片设置页面"""
    cards = UserService.get_navigation_cards(request.user.id)

    return render(
        request,
        "nav_cards/settings.html",
        {
            "cards": cards,
            "max_cards": 12,
        },
    )
