# -*- coding: utf-8 -*-
"""
================================================================================
文件：common.py
路径：/home/edo/cimf/core/init_scripts/common.py
================================================================================

功能说明：
    初始化脚本的公共工具函数库，提供各阶段通用的辅助功能。
    
    包含终端颜色输出、进度显示、迁移检测、数据库操作等通用功能，
    避免代码重复，统一各阶段的输出风格和错误处理逻辑。

主要功能：
    - colored(): 终端颜色输出辅助函数
    - print_section(): 打印阶段标题（带分隔线）
    - print_step(): 打印步骤信息
    - ask_reset_mode(): 交互式询问用户初始化模式（删除重建/增量）
    - _has_pending_migrations(): 检查是否有待执行的迁移（带缓存优化）
    - verify_module_taxonomies(): 验证所有已安装模块的词汇表
    - verify_smtp_tables(): 验证 SMTP 相关表是否创建

用法：
    1. 在阶段文件中导入：
       from .common import print_section, print_step, colored
    
    2. 打印格式化的阶段信息：
       print_section("阶段1：数据库结构")
       print_step("1.1", "执行 Django migrations")

版本：
    - 1.0: 从 init_db.py 提取公共函数

依赖：
    - django.core.management.call_command
    - django.db
    - core.node.services.ModuleService
    - core.models（Taxonomy, TaxonomyItem, Module）
"""

from typing import Dict, Any, List


def colored(text: str, color: str = "white") -> str:
    """终端颜色辅助函数"""
    colors = {
        "green": "\033[92m",
        "yellow": "\033[93m",
        "red": "\033[91m",
        "cyan": "\033[96m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "white": "\033[97m",
        "reset": "\033[0m",
        "bold": "\033[1m",
    }
    return f"{colors.get(color, colors['white'])}{text}{colors['reset']}"


def print_section(title: str):
    """打印阶段标题"""
    print()
    bold_cyan = f"\033[1m\033[96m【{title}】\033[0m"
    print(bold_cyan)
    print(colored("=" * 60, "cyan"))


def print_step(step_num: str, description: str):
    """打印步骤"""
    print(colored(f"  {step_num}. {description}", "blue"))


def ask_reset_mode(db_path: str) -> bool:
    """
    交互式询问用户初始化模式
    
    Args:
        db_path: 数据库路径描述
        
    Returns:
        bool: True 表示删除重建，False 表示增量式
    """
    print(colored(f"检测到已存在的数据库: {db_path}", "yellow"))
    print(colored("请选择初始化模式：", "cyan"))
    print(colored("  [1] 删除原有数据库并重新初始化（会丢失所有数据）", "white"))
    print(colored("  [2] 增量式初始化（保留现有数据，仅更新结构）", "white"))
    
    while True:
        try:
            choice = input(colored("请选择 (1/2): ", "cyan")).strip()
            if choice == '1':
                return True
            elif choice == '2':
                return False
            else:
                print(colored("无效选择，请输入 1 或 2", "red"))
        except (KeyboardInterrupt, EOFError):
            print(colored("\n用户取消操作", "yellow"))
            import sys
            sys.exit(0)


def _has_pending_migrations() -> bool:
    """检查是否有待执行的迁移（带缓存优化）"""
    if hasattr(_has_pending_migrations, '_cached_result'):
        return _has_pending_migrations._cached_result
    
    from django.core.management import call_command
    from io import StringIO
    
    out = StringIO()
    call_command('showmigrations', '--plan', stdout=out)
    lines = out.getvalue().strip().split('\n')
    result = any(line.startswith('[ ]') for line in lines)
    
    # 缓存结果（本次执行期间有效）
    _has_pending_migrations._cached_result = result
    return result


def verify_module_taxonomies() -> List[str]:
    """
    验证所有已安装模块的词汇表是否正确创建
    
    Returns:
        list: 错误信息列表，空列表表示验证通过
    """
    from core.module.services import ModuleService
    from core.module.models import Module
    from core.models import Taxonomy, TaxonomyItem
    
    errors = []
    modules = Module.objects.filter(is_installed=True)
    
    for module in modules:
        module_info = ModuleService._load_module_info(module.path)
        if not module_info:
            continue
        
        taxonomies_config = module_info.get('taxonomies', [])
        if not taxonomies_config:
            continue
        
        for tax_data in taxonomies_config:
            slug = tax_data.get('slug')
            name = tax_data.get('name', '')
            items = tax_data.get('items', [])
            
            if not slug:
                continue
            
            # 验证词汇表是否存在
            taxonomy = Taxonomy.objects.filter(slug=slug).first()
            if not taxonomy:
                errors.append(f"模块 '{module.name}': 词汇表 '{slug}' ({name}) 不存在")
                continue
            
            # 验证词汇项是否完整
            existing_items = set(taxonomy.items.values_list('name', flat=True))
            expected_items = set(items)
            missing_items = expected_items - existing_items
            
            if missing_items:
                errors.append(f"模块 '{module.name}': 词汇表 '{slug}' 缺少 {len(missing_items)} 个词汇项: {', '.join(sorted(missing_items))}")
    
    return errors


def verify_smtp_tables() -> bool:
    """
    验证 SMTP 相关表是否创建
    
    Returns:
        bool: True 表示表已创建，False 表示缺失
    """
    from django.db import connection
    
    tables = connection.introspection.table_names()
    required_tables = ['email_templates', 'email_logs']
    missing = [t for t in required_tables if t not in tables]
    
    if missing:
        return False
    return True
