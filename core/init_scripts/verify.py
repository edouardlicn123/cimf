# -*- coding: utf-8 -*-
"""
================================================================================
文件：verify.py
路径：/home/edo/cimf/core/init_scripts/verify.py
================================================================================

功能说明：
    初始化后的验证功能集合。
    
    提供多种验证函数，用于检查初始化结果是否符合预期：
    - 验证模块词汇表完整性
    - 验证 SMTP 相关表是否创建
    - 验证管理员用户是否创建
    - 验证词汇表数据是否完整
    
    这些函数在初始化完成后自动调用，也可单独调用用于诊断。

主要功能：
    - verify_module_taxonomies(): 验证所有已安装模块的词汇表
    - verify_smtp_tables(): 验证 SMTP 的 email_templates 和 email_logs 表
    - verify_admin_user(): 验证管理员用户是否存在
    - verify_taxonomies_count(): 验证词汇表数量是否达标（≥37个）

用法：
    1. 在初始化完成后自动验证：
       （已在 init_db.py 中自动调用）
    
    2. 单独调用验证：
       from core.init_scripts.verify import verify_smtp_tables
       success, errors = verify_smtp_tables()
       if not success:
           print(errors)

版本：
    - 1.0: 从 init_db.py 提取验证函数
    - 1.1: 新增 SMTP 表验证

依赖：
    - django.db.connection
    - core.models.Taxonomy, TaxonomyItem, User, Module
    - core.node.services.ModuleService
    - core.node.models.Module

注意：
    - 验证失败不会中断初始化流程，只会显示警告
    - 生产环境建议所有验证都通过后再投入使用
"""

from typing import List, Tuple


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


def verify_smtp_tables() -> Tuple[bool, str]:
    """
    验证 SMTP 相关表是否创建
    
    Returns:
        (success, message): 是否成功，消息
    """
    from django.db import connection
    
    tables = connection.introspection.table_names()
    required_tables = ['email_templates', 'email_logs']
    missing = [t for t in required_tables if t not in tables]
    
    if missing:
        return (False, f"SMTP 表缺失: {', '.join(missing)}")
    return (True, 'SMTP 表验证通过')


def verify_admin_user() -> Tuple[bool, str]:
    """
    验证管理员用户是否存在
    
    Returns:
        (success, message): 是否成功，消息
    """
    from core.models import User
    
    admin = User.objects.filter(is_admin=True).first()
    if admin:
        return (True, f"管理员用户存在: {admin.username}")
    return (False, "管理员用户不存在")


def verify_taxonomies_count() -> Tuple[bool, str]:
    """
    验证词汇表数量是否达标
    
    Returns:
        (success, message): 是否成功，消息
    """
    from core.models import Taxonomy
    
    count = Taxonomy.objects.count()
    if count >= 37:
        return (True, f"词汇表数量达标: {count} 个")
    return (False, f"词汇表数量不足: {count} 个（目标: ≥37个）")


def verify_all() -> List[str]:
    """
    执行所有验证
    
    Returns:
        list: 所有错误信息列表
    """
    errors = []
    
    # 验证模块词汇表
    module_errors = verify_module_taxonomies()
    errors.extend(module_errors)
    
    # 验证 SMTP 表
    smtp_success, smtp_msg = verify_smtp_tables()
    if not smtp_success:
        errors.append(smtp_msg)
    
    # 验证管理员
    admin_success, admin_msg = verify_admin_user()
    if not admin_success:
        errors.append(admin_msg)
    
    # 验证词汇表数量
    tax_success, tax_msg = verify_taxonomies_count()
    if not tax_success:
        errors.append(tax_msg)
    
    return errors
