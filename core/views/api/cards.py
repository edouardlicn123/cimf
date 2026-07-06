"""
卡片 API 模块
"""

import json
import logging
from importlib import import_module

from django.shortcuts import render
from django.template import engines

from core.decorators import api_get_view, api_post_view
from core.module.models import Module
from core.services import SettingsService, UserService
from core.utils.response import json_error, json_success, no_cache_json_response

logger = logging.getLogger(__name__)


@api_get_view
def api_dashboard_cards(request):  # noqa: ARG001
    """获取功能卡片布局"""
    setting_value = SettingsService.get_setting("user_dashboard_card_positions")
    positions = {}
    if setting_value:
        try:
            positions = json.loads(setting_value)
        except Exception:
            positions = {}
    else:
        logger.warning("配置未找到: user_dashboard_card_positions")

    default_positions = {str(i): {"module": None, "size": "medium", "config": {}} for i in range(1, 7)} | positions

    available_modules = []
    module_stats = {}
    module_contents = {}
    module_types = {}
    module_clickable = {}
    try:
        jinja2_engine = engines["jinja2"]

        active_modules = Module.objects.filter(is_active=True)
        for node_module in active_modules:
            module_path = node_module.path
            if module_path:
                try:
                    from core.module.services.module_service import ModuleService  # noqa: PLC0415

                    mod_info = ModuleService.load_module_info(module_path)
                    if mod_info and mod_info.get("frontpage_card", False) and "dashboard_cards" in mod_info:
                        available_modules.append(node_module.module_id)
                        module_types[node_module.module_id] = node_module.module_type
                        module_clickable[node_module.module_id] = mod_info.get("frontpage_card_clickable", True)

                        cards = mod_info["dashboard_cards"]
                        if cards and isinstance(cards, list):
                            for card in cards:
                                if "template" in card:
                                    template_path = card["template"]
                                    try:
                                        template = jinja2_engine.get_template(template_path)
                                        render_context = {
                                            "module_id": node_module.module_id,
                                            "module_card_color_start": card.get("color_start", "#0d6efd"),
                                            "module_card_color_end": card.get("color_end", "#0a58ca"),
                                        }
                                        if mod_info.get("dashboard_stats", False):
                                            service_mod = import_module(f"modules.{module_path}.services")
                                            for attr_name in dir(service_mod):
                                                attr = getattr(service_mod, attr_name)
                                                if attr_name.endswith("Service") and hasattr(attr, "get_count"):
                                                    render_context["total"] = attr.get_count()
                                                    render_context["recent"] = getattr(
                                                        attr, "get_recent_count", lambda _=7: 0
                                                    )(7)
                                                    module_stats[node_module.module_id] = {
                                                        "total": attr.get_count(),
                                                        "recent": getattr(attr, "get_recent_count", lambda _=7: 0)(7),
                                                    }
                                                    break
                                        if module_path == "whatsapp":
                                            try:
                                                wa_mod = import_module(f"modules.{module_path}.services")
                                                if hasattr(wa_mod, "WhatsAppService"):
                                                    wa_status = wa_mod.WhatsAppService.get_status()
                                                    render_context["wa_connected"] = wa_status.get("connected", False)
                                            except Exception:
                                                logger.warning("WhatsApp 状态加载失败", exc_info=True)
                                        module_contents[node_module.module_id] = template.render(render_context)
                                    except Exception as e:
                                        logger.warning(
                                            f"卡片模板渲染失败: module={node_module.module_id}, error={e}",
                                            exc_info=True,
                                        )
                                    break
                except Exception as e:
                    logger.warning(f"模块处理失败: module={node_module.module_id}, error={e}", exc_info=True)
    except Exception as e:
        logger.error(f"仪表盘卡片加载失败: {e}", exc_info=True)

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
def api_dashboard_cards_save(request):
    """保存功能卡片布局"""
    try:
        data = json.loads(request.body)
        positions = data.get("positions", {})

        SettingsService.save_setting(
            key="user_dashboard_card_positions",
            value=json.dumps(positions),
            description="用户首页功能卡片布局",
        )

        return json_success(message="布局已保存")
    except Exception as e:
        return json_error(str(e), 400)


@api_get_view
def api_nav_cards(request):
    """获取用户导航卡片"""
    try:
        cards = UserService.get_navigation_cards(request.user.id)
        return json_success(extra={"cards": cards, "max": 12})
    except Exception as e:
        return json_error(str(e), 400)


@api_post_view
def api_nav_cards_save(request):
    """保存用户导航卡片"""
    try:
        data = json.loads(request.body)
        cards = data.get("cards", [])

        if len(cards) > 12:
            return json_error("最多只能添加12个导航卡片", 400)

        UserService.save_navigation_cards(request.user.id, cards)
        return json_success(message="导航卡片已保存")
    except Exception as e:
        return json_error(str(e), 400)


@api_get_view
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
