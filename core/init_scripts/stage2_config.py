# -*- coding: utf-8 -*-
"""
================================================================================
文件：stage2_config.py
路径：/home/edo/cimf/core/init_scripts/stage2_config.py
================================================================================

功能说明：
    初始化流程的阶段2：系统配置初始化。
    
    负责初始化系统运行所需的基础数据，包含4个独立的子任务：
    1. 系统设置（SettingsService.reset_to_default）
    2. 角色权限（PermissionService.init_default_role_permissions）
    3. 词汇表（TaxonomyService.init_default_taxonomies）
    4. 邮件模板（TemplateService.init_default_templates）
    
    优化说明：
    - 词汇表初始化使用 fixture 快速加载（core/fixtures/initial_taxonomies.json）
    - 如果 fixture 加载失败，自动回退到代码初始化（bulk_create）
    - 系统设置使用批量插入，避免逐条插入的性能问题

主要功能：
    - run_stage2(): 执行阶段2的主函数
    - 串行执行4个子任务（SQLite 不支持并发写入）
    - 返回各子任务的执行结果（成功/失败、创建数量等）

用法：
    1. 通过 init_db.py 调用：
       python init_db.py --stage 2 --with-data
    
    2. 直接调用：
       from core.init_scripts.stage2_config import run_stage2
       results = run_stage2(dry_run=False)
       # results = {'settings': {...}, 'permissions': {...}, 
       #            'taxonomies': {...}, 'templates': {...}}

性能目标：
    - 使用 fixture 加载：< 1秒
    - 回退到代码初始化：< 3秒

版本：
    - 1.0: 从 init_db.py 拆分，独立为阶段文件
    - 1.1: 添加 fixture 加载支持

依赖：
    - core.services.SettingsService
    - core.services.PermissionService
    - core.services.taxonomy_service.TaxonomyService
    - core.smtp.services.template_service.TemplateService
    - core.init_scripts.common

注意：
    - 必须指定 --with-data 参数才会执行此阶段
    - 如果某子任务失败，不会中断其他任务（容错设计）
    - 词汇表 fixture 文件位置：core/fixtures/initial_taxonomies.json
"""

from typing import Dict, Any
from core.init_scripts.common import print_section, print_step, colored


def run_stage2(dry_run: bool) -> Dict[str, Any]:
    """
    执行阶段2：系统配置初始化
    
    Args:
        dry_run: 是否模拟执行
    
    Returns:
        dict: 各子任务执行结果
    """
    print_section("阶段2：系统配置")
    print_step("2.1-2.4", "初始化系统配置（设置、权限、词汇表、邮件模板）")
    
    results = {
        'settings': {'count': 0, 'success': False, 'error': None},
        'permissions': {'success': False, 'error': None},
        'taxonomies': {'count': 0, 'success': False, 'error': None},
        'templates': {'count': 0, 'success': False, 'error': None},
    }
    
    if dry_run:
        return results
    
    try:
        # 2.1 系统设置
        from core.services import SettingsService
        results['settings'] = {'count': SettingsService.reset_to_default(), 'success': True}
    except Exception as e:
        results['settings'] = {'error': str(e)}
    
    try:
        # 2.2 角色权限
        from core.services import PermissionService
        PermissionService.init_default_role_permissions()
        results['permissions'] = {'success': True}
    except Exception as e:
        results['permissions'] = {'error': str(e)}
    
    try:
        # 2.3 词汇表
        from core.services.taxonomy_service import TaxonomyService
        results['taxonomies'] = {'count': TaxonomyService.init_default_taxonomies(), 'success': True}
    except Exception as e:
        results['taxonomies'] = {'error': str(e)}
    
    try:
        # 2.4 邮件模板
        from core.smtp.services.template_service import TemplateService
        results['templates'] = {'count': TemplateService.init_default_templates(), 'success': True}
    except Exception as e:
        results['templates'] = {'error': str(e)}
    
    # 输出结果
    if results.get('settings', {}).get('success'):
        count = results.get('settings', {}).get('count', 0)
        print(colored(f"    ✓ 系统设置默认值已重置/插入，共 {count} 项", "green"))
    
    if results.get('permissions', {}).get('success'):
        print(colored("    ✓ 角色权限初始化完成", "green"))
    
    if results.get('taxonomies', {}).get('success'):
        count = results.get('taxonomies', {}).get('count', 0)
        print(colored(f"    ✓ 词汇表数据初始化完成，共创建 {count} 个词汇表", "green"))
    
    if results.get('templates', {}).get('success'):
        count = results.get('templates', {}).get('count', 0)
        print(colored(f"    ✓ 邮件模板初始化完成，共创建 {count} 个模板", "green"))
    
    errors = [f"{k}: {v.get('error')}" for k, v in results.items() if v.get('error')]
    if errors:
        print(colored(f"    ⚠ 部分任务执行异常: {'; '.join(errors)}", "yellow"))
    
    return results
