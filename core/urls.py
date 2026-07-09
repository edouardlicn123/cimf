"""核心应用 URL 路由配置"""

from django.urls import include, path, re_path
from django.views.generic.base import RedirectView

from core.node import views as node_views
from core.node.views import field_types, field_types_api
from core.smtp import views as smtp_views

from . import views

app_name = "core"

_structure_urls = [
    path("dashboard/", views.structure_dashboard, name="structure_dashboard"),
    path("types/", node_views.node_types_list, name="node_types_list"),
    path("types/<int:node_type_id>/toggle/", node_views.node_type_toggle, name="node_type_toggle"),
    path("types/<int:node_type_id>/delete/", node_views.node_type_delete, name="node_type_delete"),
    path("fieldtypes/", field_types, name="field_types"),
    path("api/fieldtypes/", field_types_api, name="field_types_api"),
    path("taxonomies/", views.taxonomies, name="taxonomies"),
    path("taxonomy/<int:taxonomy_id>/", views.taxonomy_view, name="taxonomy_view"),
    path("taxonomy/<int:taxonomy_id>/edit/", views.taxonomy_edit, name="taxonomy_edit"),
    path("taxonomy/create/", views.taxonomy_create, name="taxonomy_create"),
    path("taxonomy/<int:taxonomy_id>/delete/", views.taxonomy_delete, name="taxonomy_delete"),
    path("taxonomy/<int:taxonomy_id>/item/create/", views.taxonomy_item_create, name="taxonomy_item_create"),
    path(
        "taxonomy/<int:taxonomy_id>/item/<int:item_id>/edit/",
        views.taxonomy_item_update,
        name="taxonomy_item_update",
    ),
    path(
        "taxonomy/<int:taxonomy_id>/item/<int:item_id>/delete/",
        views.taxonomy_item_delete,
        name="taxonomy_item_delete",
    ),
]

_system_urls = [
    path("", views.admin_dashboard, name="admin_dashboard"),
    path("users/", views.system_users, name="system_users"),
    path("user/create/", views.user_create, name="user_create"),
    path("user/<int:user_id>/edit/", views.user_edit, name="user_edit"),
    path("user/<int:user_id>/delete/", views.user_delete, name="user_delete"),
    path("settings/", views.system_settings, name="system_settings"),
    path("permissions/", views.system_permissions, name="system_permissions"),
    path("cron/", views.cron_manager, name="cron_manager"),
    path("permission-check/", views.permission_check, name="permission_check"),
    path("smtp/", smtp_views.smtp_config, name="smtp_config"),
    path("smtp/test/", smtp_views.smtp_test, name="smtp_test"),
    path("smtp/history/", smtp_views.smtp_history, name="smtp_history"),
    path("smtp/cleanup/", smtp_views.smtp_cleanup_logs, name="smtp_cleanup_logs"),
    path("smtp/process/", smtp_views.smtp_process_queue, name="smtp_process_queue"),
    path("logs/", views.logs_index, name="logs_index"),
    path("logs/<str:log_type>/", views.logs_view, name="logs_view"),
]

urlpatterns = [
    # 认证
    path("accounts/login/", views.login_view, name="login"),
    path("accounts/logout/", views.logout_view, name="logout"),
    # 仪表盘
    path("", views.dashboard, name="dashboard"),
    # 内容结构
    path("structure/", include(_structure_urls)),
    # 协作工具
    path("tools/dashboard/", views.tools_index, name="tools_index"),
    re_path(r"^tools/(?P<tool_slug>[\w-]+)/$", views.tools_page, name="tools_page"),
    # 系统管理
    path("system/", include(_system_urls)),
    # 个人中心
    path("user/profile/", views.profile_view, name="profile_view"),
    path("user/settings/", views.profile_settings, name="profile_settings"),
    path("settings/change-password/", views.change_password, name="change_password"),
    path("profile/", views.profile, name="profile"),
    path("user/functioncards/", views.homepage_settings, name="homepage_settings"),
    path("user/navcards/", views.navigation_settings, name="navigation_settings"),
    # 健康检查
    path("health/", views.health_check, name="health_check"),
    path("health/detailed/", views.detailed_health_check, name="detailed_health_check"),
    # 旧路径重定向（向后兼容）
]

_old_redirects = [
    ("structure/", "/structure/dashboard/", "structure_old_redirect"),
    ("taxonomies/", "/structure/taxonomies/", "taxonomies_old_redirect"),
    ("taxonomy/", "/structure/taxonomies/", "taxonomy_old_redirect"),
]
urlpatterns += [
    path(old_path, RedirectView.as_view(url=new_url, permanent=False), name=name)
    for old_path, new_url, name in _old_redirects
]
