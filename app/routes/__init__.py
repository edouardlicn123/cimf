# 文件路径：app/routes/__init__.py
# 功能说明：所有蓝图（Blueprint）的统一注册入口文件

from flask import Blueprint

# 从新模块目录导入
from app.modules.core.auth import auth_bp
from app.modules.core.admin import admin_bp
from app.modules.core.workspace import workspace_bp
from app.modules.core.profile import profile_bp
from app.modules.core.export import export_bp
from app.modules.core.taxonomy import taxonomy_bp
from app.modules.core.node import node_bp
from app.modules.core.time import time_bp
from app.modules.core.cron import cron_bp
from app.modules.core.cron.admin_routes import admin_cron_bp
from app.modules.nodes.customer import customer_bp


def register_blueprints(app):
    """统一注册所有蓝图的入口函数"""
    
    # 工作台/仪表盘（根路径）
    app.register_blueprint(workspace_bp)

    # 认证路由
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # 个人中心
    app.register_blueprint(profile_bp, url_prefix='/profile')

    # 管理后台
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # 导出模块
    app.register_blueprint(export_bp, url_prefix='/export')

    # 词汇表模块
    app.register_blueprint(taxonomy_bp)

    # 节点模块
    app.register_blueprint(node_bp, url_prefix='/nodes')

    # 客户节点
    app.register_blueprint(customer_bp, url_prefix='/nodes/customer')

    # 时间API模块
    app.register_blueprint(time_bp)

    # Cron调度模块
    app.register_blueprint(cron_bp)

    # Cron管理后台
    app.register_blueprint(admin_cron_bp, url_prefix='/admin')

    app.logger.info("所有蓝图注册完成：workspace, auth, profile, admin, export, taxonomy, node, customer, time, cron, admin_cron 已加载")
