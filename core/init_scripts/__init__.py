# -*- coding: utf-8 -*-
"""
================================================================================
文件：__init__.py
路径：/home/edo/cimf/core/init_scripts/__init__.py
================================================================================

功能说明：
    初始化脚本包的主入口，导出所有阶段执行函数和公共工具函数。
    
    该包实现了初始化流程的四阶段分离架构：
    - 阶段1：数据库结构（migrations）
    - 阶段2：系统配置（设置、权限、词汇表、模板）
    - 阶段3：用户管理（管理员创建）
    - 阶段4：业务模块（扫描、注册、安装）
    
    支持通过 --stage 参数单独执行某个阶段，便于调试和运维。

主要功能：
    - 导出 run_stage1, run_stage2, run_stage3, run_stage4 函数
    - 导出公共工具函数（colored, print_section, print_step）
    - 提供统一的包接口

用法：
    1. 通过 init_db.py 调用（推荐）：
       python init_db.py --stage 2 --with-data
    
    2. 直接导入使用：
       from core.init_scripts import run_stage2
       run_stage2(dry_run=False)

版本：
    - 1.0: 从 init_db.py 拆分，实现多阶段分文件架构

依赖：
    - core.init_scripts.stage1_migrations
    - core.init_scripts.stage2_config
    - core.init_scripts.stage3_users
    - core.init_scripts.stage4_modules
    - core.init_scripts.common
"""

from .stage1_migrations import run_stage1
from .stage2_config import run_stage2
from .stage3_users import run_stage3
from .stage4_modules import run_stage4, print_module_results
from .common import print_section, print_step, colored, verify_module_taxonomies

__all__ = [
    'run_stage1', 'run_stage2', 'run_stage3', 'run_stage4',
    'print_module_results',
    'print_section', 'print_step', 'colored', 'verify_module_taxonomies'
]
