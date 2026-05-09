#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
文件：init_db.py
路径：/home/edo/cimf/init_db.py
================================================================================

功能说明：
    Django 数据库初始化脚本（主入口，向后兼容）
    
    初始化阶段：
    【阶段1】数据库结构 - 执行 Django migrations（仅核心模块）
    【阶段2】系统配置 - 设置、权限、词汇表
    【阶段3】用户管理 - 创建管理员
    【阶段4】业务模块 - 扫描并注册模块（不安装，不创建表）
    
    注意：
    - 模块的安装（包括建表、初始化样本数据）在用户手动安装模块时执行
    - 使用 ./run.sh → 5 → 3 进入模块管理页面手动安装
    
    用法：
    python init_db.py                         # 仅创建核心表
    python init_db.py --with-data            # 创建表 + 初始数据
    python init_db.py --with-data --force    # 强制重置 admin 用户
    python init_db.py --with-data --reset-db # 删除数据库后重新初始化
    python init_db.py --with-data --incremental # 增量式初始化
    python init_db.py --dry-run              # 模拟执行
    python init_db.py --skip-migrate         # 跳过 migrations（外部已执行时使用）
    python init_db.py --stage 1               # 仅执行阶段1
    python init_db.py --stage 2 --with-data  # 仅执行阶段2
    
    环境变量：
    ADMIN_USERNAME: 管理员用户名 (默认: admin)
    ADMIN_NICKNAME: 管理员昵称 (默认: 系统管理员)
    ADMIN_PASSWORD: 管理员密码 (默认: admin123)
    ADMIN_EMAIL: 管理员邮箱 (默认: admin@example.com)
    ADMIN_THEME: 主题偏好 (默认: default)
    ALLOW_SEED_PROD: 允许在生产环境执行 (默认: false)

版本：
    - 4.0: 重构为多阶段分文件架构（core/init_scripts/）
    - 3.0: 重构为系统初始化与模块初始化分离

依赖：
    - Django 6.0+
    - core.init_scripts（多阶段初始化包）
"""

import os
import sys
import argparse
from datetime import datetime

# 导入初始化脚本包
from core.init_scripts import (
    run_stage1, run_stage2, run_stage3, run_stage4,
    print_module_results,
)
from core.init_scripts.common import colored, print_section, print_step


def init_database(with_data: bool = False, force: bool = False, dry_run: bool = False,
                  reset_db: bool = False, incremental: bool = False, skip_migrate: bool = False,
                  stage: int = None):
    """
    初始化数据库核心逻辑（调用各阶段函数）
    
    Args:
        with_data: 是否初始化初始数据
        force: 是否强制重置管理员用户
        dry_run: 是否模拟执行
        reset_db: 是否删除数据库后重建
        incremental: 是否增量式初始化
        skip_migrate: 是否跳过 migrations（外部已执行时使用）
        stage: 指定执行阶段（1-4），None 表示执行全部
    """
    banner = f"\033[1m\033[96m{'='*60}\033[0m"
    print(banner)
    print(colored(f"CIMF 管理系统 - 数据库初始化工具", "cyan"))
    print(colored(f"({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})", "cyan"))
    print(banner)
    print(colored(f"当前环境: {os.environ.get('DJANGO_ENV', 'development')}", "cyan"))
    
    if dry_run:
        print(colored("【DRY-RUN 模式】仅模拟执行，不会修改数据库", "yellow"))
        print(colored("=" * 60, "cyan"))
    
    # 导入数据库工具
    from cimf_django.database import database_exists, drop_database, get_database_config
    
    # 检查数据库是否存在
    db_exists = database_exists()
    db_config = get_database_config()
    db_path = str(db_config.get('NAME', 'unknown'))
    
    # 处理数据库删除逻辑
    if db_exists:
        if reset_db:
            print(colored("检测到已存在的数据库", "yellow"))
            print(colored("【删除重建模式】正在删除原有数据库...", "yellow"))
            if not dry_run:
                drop_database()
                print(colored("数据库已删除，将重新创建", "green"))
            else:
                print(colored(f"[模拟] 将删除数据库: {db_path}", "yellow"))
        elif incremental:
            print(colored("检测到已存在的数据库", "yellow"))
            print(colored("【增量式模式】保留现有数据，仅更新结构", "cyan"))
        else:
            from core.init_scripts.common import ask_reset_mode
            should_reset = ask_reset_mode(db_path)
            if should_reset:
                print(colored("【删除重建模式】正在删除原有数据库...", "yellow"))
                if not dry_run:
                    drop_database()
                    print(colored("数据库已删除，将重新创建", "green"))
                else:
                    print(colored(f"[模拟] 将删除数据库: {db_path}", "yellow"))
            else:
                print(colored("【增量式模式】保留现有数据，仅更新结构", "cyan"))
    else:
        print(colored("未检测到数据库文件，将执行全新初始化...", "cyan"))
    
    print(colored("=" * 60, "cyan"))
    
    # 设置 Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cimf_django.settings')
    
    import django
    django.setup()
    
    from django.conf import settings
    from django.db import connection
    
    print(colored(f"数据库: {settings.DATABASES['default']['NAME']}", "cyan"))
    print(colored("=" * 60, "cyan"))
    
    # ===== 【阶段1】数据库结构 =====
    if stage is None or stage == 1:
        print(colored(f"\n[1/4] 阶段1：数据库结构", "cyan"))
        run_stage1(skip_migrate=skip_migrate, incremental=incremental,
                     db_exists=db_exists, dry_run=dry_run)
    else:
        print(colored(f"\n[1/4] 跳过阶段1（--stage {stage} 参数指定）", "yellow"))
        print(colored("=" * 60, "yellow"))
    
    if not with_data:
        print(colored("\n未指定 --with-data，跳过初始数据插入", "yellow"))
        print(colored("=" * 60, "cyan"))
    else:
        # ===== 【阶段2】系统配置 =====
        if stage is None or stage == 2:
            print(colored(f"\n[2/4] 阶段2：系统配置", "cyan"))
            run_stage2(dry_run=dry_run)
        else:
            print(colored(f"\n[2/4] 跳过阶段2（--stage {stage} 参数指定）", "yellow"))
            print(colored("=" * 60, "yellow"))
        
        # ===== 【阶段3】用户管理 =====
        if stage is None or stage == 3:
            print(colored(f"\n[3/4] 阶段3：用户管理", "cyan"))
            run_stage3(force=force, dry_run=dry_run)
        else:
            print(colored(f"\n[3/4] 跳过阶段3（--stage {stage} 参数指定）", "yellow"))
            print(colored("=" * 60, "yellow"))
    
    # ===== 【阶段4】业务模块 =====
    # 模块安装不依赖 with_data，可以独立执行
    if stage is None or stage == 4:
        print(colored(f"\n[4/4] 阶段4：业务模块", "cyan"))
        results4 = run_stage4(dry_run=dry_run)
        print_module_results(results4)
    else:
        print(colored(f"\n[4/4] 跳过阶段4（--stage {stage} 参数指定）", "yellow"))
        print(colored("=" * 60, "yellow"))
    
    # ===== 完成 =====
    print()
    print(colored(f"{'='*60}", "green"))
    print(colored("✓ 所有初始化完成！", "green"))
    print(colored(f"{'='*60}", "green"))
    
    if with_data:
        print(colored("\n下一步建议：", "cyan"))
        print("  1. 启动服务: ./run.sh")
        print("  2. 访问 /auth/login 登录后台")
        print("  3. 强烈建议生产环境修改管理员密码")


def main():
    parser = argparse.ArgumentParser(
        description="CIMF 数据库初始化脚本（多阶段分文件架构）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
初始化阶段：
  【阶段1】数据库结构 - 执行 Django migrations（仅核心模块）
  【阶段2】系统配置 - 设置、权限、词汇表
  【阶段3】用户管理 - 创建管理员
  【阶段4】业务模块 - 扫描并注册模块（不安装，不创建表）

  注意：模块安装需在模块管理页面手动执行

生产环境请谨慎使用此脚本

新增：--stage 参数支持单独执行某个阶段
        """
    )
    parser.add_argument("--with-data", action="store_true", 
                        help="创建表 + 插入/重置初始管理员 + 系统设置默认记录")
    parser.add_argument("--force", action="store_true", 
                        help="强制重置 admin 用户")
    parser.add_argument("--dry-run", action="store_true", 
                        help="模拟执行，不实际写入数据库")
    parser.add_argument("--reset-db", action="store_true",
                        help="删除原有数据库后重新初始化（会丢失所有数据）")
    parser.add_argument("--incremental", action="store_true",
                        help="增量式初始化（保留现有数据，仅更新结构）")
    parser.add_argument("--skip-migrate", action="store_true",
                        help="跳过 migrations（外部已执行时使用）")
    parser.add_argument("--stage", type=int, choices=[1, 2, 3, 4],
                        help="指定初始化阶段（1-4），不指定则执行全部")
    
    global args
    args = parser.parse_args()
    
    if args.reset_db and args.incremental:
        print(colored("错误：--reset-db 和 --incremental 不能同时使用", "red"))
        sys.exit(1)
    
    try:
        init_database(
            with_data=args.with_data,
            force=args.force,
            dry_run=args.dry_run,
            reset_db=args.reset_db,
            incremental=args.incremental,
            skip_migrate=args.skip_migrate,
            stage=args.stage
        )
    except KeyboardInterrupt:
        print("\n用户取消操作。")
        sys.exit(0)
    except Exception as e:
        print(colored(f"初始化过程中发生未预期错误: {str(e)}", "red"), file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
