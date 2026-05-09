# -*- coding: utf-8 -*-
"""
================================================================================
文件：stage1_migrations.py
路径：/home/edo/cimf/core/init_scripts/stage1_migrations.py
================================================================================

功能说明：
    初始化流程的阶段1：数据库结构迁移。
    
    负责执行 Django 的 migrate 命令，创建或更新所有已注册应用的数据库表结构。
    包括核心应用（core, auth, contenttypes 等）和动态加载的模块应用。
    
    支持三种执行模式：
    - 完整迁移：执行所有待执行的迁移
    - 增量迁移：仅执行新增的迁移（通过 --incremental 参数）
    - 跳过迁移：由外部脚本执行（通过 --skip-migrate 参数）

主要功能：
    - run_stage1(): 执行阶段1的主函数
    - 支持增量初始化检测（_has_pending_migrations）
    - 自动处理 core.0004_import_china_regions 等特殊迁移
    - 提供详细的执行进度输出

用法：
    1. 通过 init_db.py 调用：
       python init_db.py --stage 1
    
    2. 直接调用：
       from core.init_scripts.stage1_migrations import run_stage1
       run_stage1(skip_migrate=False, incremental=False, 
                     db_exists=True, dry_run=False)

性能目标：
    - 首次执行：< 3秒
    - 增量执行（无pending）：< 0.5秒
    - 增量执行（有pending）：< 2秒

版本：
    - 1.0: 从 init_db.py 拆分，独立为阶段文件

依赖：
    - django.core.management.call_command
    - django.conf.settings
    - core.init_scripts.common（print_section, print_step, colored）
    - cimf_django.database（database_exists, drop_database）

注意：
    - SMTP 模块已在 settings.INSTALLED_APPS 中，会自动迁移
    - 如果迁移失败，会直接 sys.exit(1) 退出
    - 默认数据库为 SQLite，不支持并发写入
"""

from core.init_scripts.common import print_section, print_step, colored


def run_stage1(skip_migrate: bool, incremental: bool, db_exists: bool, 
                dry_run: bool) -> bool:
    """
    执行阶段1：数据库结构迁移
    
    Args:
        skip_migrate: 是否跳过迁移（外部已执行时使用）
        incremental: 是否增量式初始化
        db_exists: 数据库是否已存在
        dry_run: 是否模拟执行
    
    Returns:
        bool: 是否成功执行
    """
    print_section("阶段1：数据库结构")
    print_step("1.1", "执行 Django migrations")
    
    if skip_migrate:
        print(colored("    ⊘ 跳过（由外部脚本执行）", "yellow"))
        return True
    
    if incremental and db_exists:
        if not dry_run:
            if not _has_pending_migrations():
                print(colored("    ⊘ 无待执行迁移，跳过", "green"))
            else:
                from django.core.management import call_command
                call_command('migrate', '--noinput')
                print(colored("    ✓ migrations 执行完成", "green"))
        else:
            print(colored("    [模拟] 将检查并执行 pending migrations", "yellow"))
        return True
    
    if not dry_run:
        from django.core.management import call_command
        try:
            call_command('migrate', '--noinput')
            print(colored("    ✓ migrations 执行完成", "green"))
        except Exception as e:
            print(colored(f"    ✗ migrations 执行失败: {str(e)}", "red"))
            import sys
            sys.exit(1)
    else:
        print(colored("    [模拟] 将执行 python manage.py migrate --noinput", "yellow"))
    
    return True


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
