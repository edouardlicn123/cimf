# -*- coding: utf-8 -*-
"""
================================================================================
文件：stage3_users.py
路径：/home/edo/cimf/core/init_scripts/stage3_users.py
================================================================================

功能说明：
    初始化流程的阶段3：用户管理（创建管理员用户）。
    
    负责创建系统管理员账号，包括：
    - 用户名、昵称、邮箱、密码
    - 角色分配（UserRole.MANAGER）
    - 管理员权限标记（is_admin=True）
    - 默认导航卡片配置（6个默认卡片）
    - 主题偏好、通知设置、语言偏好
    
    支持以下特性：
    - 生产环境密码强度检查（≥10位）
    - 通过环境变量配置管理员信息（ADMIN_USERNAME 等）
    - --force 参数强制重置已存在的管理员
    - 生产环境保护限制（需要 ALLOW_SEED_PROD=1）

主要功能：
    - run_stage3(): 执行阶段3的主函数
    - 检查管理员是否已存在（增量初始化时跳过）
    - 验证生产环境安全限制
    - 创建或重置管理员用户

用法：
    1. 通过 init_db.py 调用：
       python init_db.py --stage 3 --with-data
       python init_db.py --stage 3 --with-data --force  # 强制重置
    
    2. 直接调用：
       from core.init_scripts.stage3_users import run_stage3
       run_stage3(force=False, dry_run=False)

环境变量：
    - ADMIN_USERNAME: 管理员用户名（默认: admin）
    - ADMIN_NICKNAME: 管理员昵称（默认: 系统管理员）
    - ADMIN_PASSWORD: 管理员密码（默认: admin123）
    - ADMIN_EMAIL: 管理员邮箱（默认: admin@example.com）
    - ADMIN_THEME: 主题偏好（默认: default）
    - ADMIN_NOTIFICATIONS: 是否启用通知（默认: true）
    - ADMIN_PREFERRED_LANGUAGE: 偏好语言（默认: zh）
    - ALLOW_SEED_PROD: 允许生产环境执行（默认: false）

性能目标：
    - 创建管理员：< 0.5秒

版本：
    - 1.0: 从 init_db.py 拆分，独立为阶段文件

依赖：
    - django.conf.settings
    - core.models.User
    - core.services.UserRole
    - core.init_scripts.common

注意：
    - 必须指定 --with-data 参数才会执行此阶段
    - 生产环境必须使用强密码（≥10位）
    - 首次登录后强烈建议修改密码
"""

from core.init_scripts.common import print_section, print_step, colored
from typing import Optional


def run_stage3(force: bool = False, dry_run: bool = False) -> bool:
    """
    执行阶段3：创建管理员用户
    
    Args:
        force: 是否强制重置已存在的管理员
        dry_run: 是否模拟执行
    
    Returns:
        bool: 是否成功执行
    """
    print_section("阶段3：用户管理")
    print_step("3.1", "创建管理员用户")
    
    from django.conf import settings
    from core.models import User
    from core.constants import UserRole
    import os
    
    admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
    admin_nickname = os.environ.get('ADMIN_NICKNAME', '系统管理员')
    admin_password = os.environ.get('ADMIN_PASSWORD')  # 生产环境必须设置
    if not admin_password:
        if os.environ.get('DJANGO_ENV', 'development') == 'production':
            print("❌ 错误：生产环境必须设置 ADMIN_PASSWORD 环境变量！")
            return False
        else:
            admin_password = 'admin123'  # 仅开发环境默认值
            print(f"⚠️ 警告：使用默认密码，生产环境请设置 ADMIN_PASSWORD")
    admin_email = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
    admin_theme = os.environ.get('ADMIN_THEME', 'default')
    admin_notifications = os.environ.get('ADMIN_NOTIFICATIONS', 'true').lower() in ('true', '1', 'yes', 'on')
    admin_language = os.environ.get('ADMIN_PREFERRED_LANGUAGE', 'zh')
    
    env = os.environ.get('DJANGO_ENV', 'development')
    
    # 生产环境安全限制
    if env == 'production' and not os.environ.get('ALLOW_SEED_PROD'):
        print(colored("【生产环境安全限制】禁止自动插入初始数据！", "red"))
        print(colored("如需强制执行，请设置环境变量 ALLOW_SEED_PROD=1 （极度不推荐）"))
        return False
    
    if env == 'production':
        if len(admin_password) < 10:
            print(colored("错误：管理员密码长度不足 10 位！请通过环境变量 ADMIN_PASSWORD 设置更强密码", "red"))
            return False
    
    try:
        existing_admin = User.objects.filter(username=admin_username).first()
    except Exception as e:
        if 'no such table' in str(e) or 'does not exist' in str(e):
            print(colored("✗ 数据库表不存在，请先运行阶段1完成数据库迁移：", "red"))
            print(colored("  ./venv/bin/python init_db.py --stage 1", "yellow"))
            return False
        raise
    
    if existing_admin and not force:
        print(colored(f"    - 管理员 '{admin_username}' 已存在，跳过创建", "yellow"))
        if force:
            print(colored(f"    (使用 --force 可强制重置)", "yellow"))
        return True
    
    if existing_admin and force:
        print(colored(f"    - 强制删除旧管理员 '{admin_username}' ...", "yellow"))
        if not dry_run:
            existing_admin.delete()
    
    if not dry_run:
        DEFAULT_NAV_CARDS = [
            {"id": "default-1", "name": "必应搜索", "url": "https://www.bing.com", "bg_color": "#3584e4", "position": 1},
            {"id": "default-2", "name": "豆包", "url": "https://www.doubao.com", "bg_color": "#2ec27e", "position": 2},
            {"id": "default-3", "name": "千问", "url": "https://tongyi.aliyun.com", "bg_color": "#9141ac", "position": 3},
            {"id": "default-4", "name": "百度地图", "url": "https://map.baidu.com", "bg_color": "#2932e1", "position": 4},
            {"id": "default-5", "name": "哔哩哔哩", "url": "https://www.bilibili.com", "bg_color": "#00a1d6", "position": 5},
            {"id": "default-6", "name": "36氪", "url": "https://36kr.com", "bg_color": "#f85959", "position": 6},
        ]
        admin = User.objects.create_user(
            username=admin_username,
            nickname=admin_nickname,
            email=admin_email,
            role=UserRole.MANAGER,
            is_admin=True,
            is_active=True,
            theme=admin_theme,
            notifications_enabled=admin_notifications,
            preferred_language=admin_language,
            navigation_cards=DEFAULT_NAV_CARDS,
        )
        admin.set_password(admin_password)
        admin.save()
        
        print(colored("    ✓ 管理员用户创建成功", "green"))
        print(f"      用户名: {admin_username}")
        print(f"      昵称: {admin_nickname}")
        print(f"      密码: {admin_password} （生产环境请立即修改！）")
        print(colored("    ⚠ 请登录后立即修改密码！", "yellow"))
    else:
        print(colored(f"    [模拟] 将创建管理员用户: {admin_username}", "yellow"))
    
    return True
