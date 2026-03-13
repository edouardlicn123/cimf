# 文件路径：app/services/core/__init__.py
# 更新日期：2026-02-17
# 功能说明：服务层模块统一入口文件，便于路由层或其他模块以简洁方式导入所有服务类/函数，避免长路径导入，提高代码可读性和维护性

"""
服务层入口模块
使用方式示例：
    from app.services import UserService, SettingsService, login_attempt, safe_logout
    # 或
    from app.services import user_service, settings_service
"""

# 导入所有核心服务类 / 函数，便于 from app.services import XXX 直接使用

# 认证相关常用函数（直接导入，避免假设模块级 auth_service 对象）
from app.services.core.auth_service import login_attempt, get_post_login_redirect, safe_logout

# 用户管理服务
from app.services.core.user_service import UserService

# 系统设置服务
from app.services.core.settings_service import SettingsService

# 权限服务
from app.services.core.permission_service import PermissionService, UserRole

# 计算相关服务（按需导入子模块）
from app.services.core.calc import shipping
from app.services.core.calc import volume_kd

# 如果 calc 目录下未来有更多计算服务，可以在这里统一暴露
# 示例：from app.services.core.calc.volume_kd import VolumeKDService  # 如果改为类形式

# 可选：定义一个服务注册字典，便于未来动态加载或依赖注入（目前可选）
SERVICES = {
    'user': UserService,
    'settings': SettingsService,
    # 'auth': {  # 如果未来想包装 auth 函数为对象，可在此添加
    #     'login_attempt': login_attempt,
    #     'get_post_login_redirect': get_post_login_redirect,
    #     'safe_logout': safe_logout,
    # },
    # 'shipping_calc': shipping,
    # 'volume_kd_calc': volume_kd,
}

# 如果项目规模继续扩大，可考虑在这里添加服务初始化逻辑
# 例如：
# def init_services(app):
#     """服务层初始化（可选，用于绑定 app 或其他依赖）"""
#     pass
