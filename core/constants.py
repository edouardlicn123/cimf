"""
================================================================================================================================================
文件：constants.py
路径：/home/edo/cimf-v2/core/constants.py
================================================================================================================================================

功能说明：
    项目全局常量定义，包含版本号、角色、主题、模块类型、语言等。

    该文件不导入任何项目内部模块，避免循环导入问题。

版本：
    - 2.0: 重构为集中化常量

版本历史：
    - 1.000: 初始版本（仅版本号）
    - 2.000: 2026-05-02 - 集中化常量定义
    - 2.151: 2026-08-01
"""

# ============================================================
# 系统版本
# ============================================================

VERSION_MAJOR = "2"
VERSION_MINOR = 159


def get_version_display():
    return f"v{VERSION_MAJOR}.{VERSION_MINOR:03d}"


# ============================================================
# 用户角色
# ============================================================


class UserRole:
    """用户角色常量"""

    MANAGER = "manager"
    LEADER = "leader"
    EMPLOYEE = "employee"

    CHOICES = [
        (MANAGER, "一类用户"),
        (LEADER, "二类用户"),
        (EMPLOYEE, "三类用户"),
    ]

    LABELS = {
        MANAGER: "一类用户",
        LEADER: "二类用户",
        EMPLOYEE: "三类用户",
    }

    BADGE_CLASSES = {
        MANAGER: "bg-danger",
        LEADER: "bg-warning text-dark",
        EMPLOYEE: "bg-secondary",
    }


# ============================================================
# 用户主题
# ============================================================


class UserTheme:
    """用户主题常量"""

    DEFAULT = "default"
    GOV = "gov"
    INDIGO = "indigo"
    MACARON = "macaron"
    SAVAWOKU = "savawoku"
    KAJIMA = "kajima"
    ODOGU = "odoru"
    TAIS = "tais"

    CHOICES = [
        (DEFAULT, "默认"),
        (GOV, "中国红"),
        (INDIGO, "靛蓝"),
        (MACARON, "马卡龙"),
        (SAVAWOKU, "橙红"),
        (KAJIMA, "绿岛森林"),
        (ODOGU, "踊"),
        (TAIS, "梵紫"),
    ]

    LABELS = {
        DEFAULT: "默认",
        GOV: "中国红",
        INDIGO: "靛蓝",
        MACARON: "马卡龙",
        SAVAWOKU: "橙红",
        KAJIMA: "绿岛森林",
        ODOGU: "踊",
        TAIS: "梵紫",
    }

    DISPLAY_LABELS = LABELS.copy()


# ============================================================
# 模块类型
# ============================================================


class ModuleType:
    """模块类型常量"""

    NODE = "node"
    SYSTEM = "system"
    TOOL = "tool"

    CHOICES = [
        (NODE, "节点模块"),
        (SYSTEM, "系统模块"),
        (TOOL, "工具模块"),
    ]


# ============================================================
# 语言
# ============================================================


class Language:
    """语言常量"""

    ZH = "zh"
    EN = "en"

    CHOICES = [
        (ZH, "中文（简体）"),
        (EN, "English"),
    ]


# ============================================================
# URL 名称常量
# ============================================================


class URLName:
    """URL 名称常量 — 集中管理，消除魔法字符串"""

    LOGIN = "core:login"
    DASHBOARD = "core:dashboard"
    SYSTEM_SETTINGS = "core:system_settings"
    SYSTEM_USERS = "core:system_users"
    SYSTEM_PERMISSIONS = "core:system_permissions"
    TAXONOMIES = "core:taxonomies"
    TAXONOMY_CREATE = "core:taxonomy_create"
    TAXONOMY_VIEW = "core:taxonomy_view"
    TAXONOMY_EDIT = "core:taxonomy_edit"
    PROFILE_SETTINGS = "core:profile_settings"
    PROFILE_VIEW = "core:profile_view"
    LOGS_INDEX = "core:logs_index"
    CRON_MANAGER = "core:cron_manager"
    TOOLS_INDEX = "core:tools_index"
    IMPORTEXPORT_DASHBOARD = "core:importexport_dashboard"
    MODULE_LIST = "core:module_list"
    MARKET_INDEX = "core:market_index"
    HOMEPAGE_SETTINGS = "core:homepage_settings"
    NAVIGATION_SETTINGS = "core:navigation_settings"
    PERMISSION_CHECK = "core:permission_check"


# ============================================================
# 权限
# ============================================================


class Perm:
    """权限标识符常量 — 集中管理，消除魔法字符串"""

    IMPORTEXPORT_VIEW = "importexport.view"
    SYSTEM_SETTINGS_VIEW = "system.settings.view"
    SYSTEM_SETTINGS_MODIFY = "system.settings.modify"
    PERMISSIONS_VIEW = "permissions.view"
    PERMISSIONS_MODIFY = "permissions.modify"
    USER_CREATE = "user.create"
    USER_READ = "user.read"
    USER_UPDATE = "user.update"
    USER_DELETE = "user.delete"
    USER_MANAGE = "user.manage"
    LOG_VIEW = "log.view"

    NODE_CUSTOMER_VIEW_OTHERS = "node.customer.view_others"
    NODE_CUSTOMER_EDIT_OTHERS = "node.customer.edit_others"
    NODE_CUSTOMER_DELETE_OTHERS = "node.customer.delete_others"


# ============================================================
# 默认导航卡片
# ============================================================

DEFAULT_NAV_CARDS = [
    {
        "id": "default-1",
        "name": "必应搜索",
        "url": "https://www.bing.com",
        "bg_color": "#3584e4",
        "position": 1,
    },
    {
        "id": "default-2",
        "name": "豆包",
        "url": "https://www.doubao.com",
        "bg_color": "#2ec27e",
        "position": 2,
    },
    {
        "id": "default-3",
        "name": "千问",
        "url": "https://tongyi.aliyun.com",
        "bg_color": "#9141ac",
        "position": 3,
    },
    {
        "id": "default-4",
        "name": "百度地图",
        "url": "https://map.baidu.com",
        "bg_color": "#2932e1",
        "position": 4,
    },
    {
        "id": "default-5",
        "name": "哔哩哔哩",
        "url": "https://www.bilibili.com",
        "bg_color": "#00a1d6",
        "position": 5,
    },
    {
        "id": "default-6",
        "name": "36氪",
        "url": "https://36kr.com",
        "bg_color": "#f85959",
        "position": 6,
    },
]

# ============================================================
# 活动区块 URL 映射
# ============================================================
URL_SECTION_MAPPING = {
    "system_settings": "settings",
    "system_users": "users",
    "system_permissions": "permissions",
    "cron_manager": "cron",
    "permission_check": "permission_check",
    "smtp_config": "smtp",
    "logs_index": "logs",
    "logs_view": "logs",
    "structure_dashboard": "dashboard",
    "node_types_list": "node_types",
    "taxonomies": "taxonomies",
    "taxonomy_create": "taxonomies",
    "taxonomy_view": "taxonomies",
    "taxonomy_edit": "taxonomies",
    "tools_index": "dashboard",
    "importexport_dashboard": "dashboard",
    "export_list": "export",
    "import_list": "import",
    "module_list": "modules_manage",
    "market_index": "market",
    "profile_view": "profile",
    "profile_settings": "preferences",
    "homepage_settings": "homepage",
    "navigation_settings": "nav_cards",
}
