# -*- coding: utf-8 -*-
"""
================================================================================
文件：app/modules/core/cron/__init__.py
路径：/home/edo/cimf-v2/app/modules/core/cron/__init__.py
================================================================================

功能说明：
    Cron 任务调度模块初始化文件
    
    此模块包含：
    - API 路由（routes.py）：提供任务管理的 HTTP API
    - 管理后台路由（admin_routes.py）：提供 Web 管理界面
    
导出内容：
    - cron_bp: API 蓝图
    
    注意：admin_cron_bp 在 routes/__init__.py 中单独注册

版本：
    - 1.0: 初始版本
"""

# API 路由蓝图
from app.modules.core.cron.routes import cron_bp

# 模块导出清单
__all__ = ['cron_bp']
