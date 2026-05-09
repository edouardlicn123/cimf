#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
文件：run.py
路径：/home/edo/cimf-v2/run.py
================================================================================

功能说明：
    Django 启动入口，类似 Flask 的 run.py
    
    开发环境：python run.py
    生产环境：推荐使用 gunicorn

环境变量：
    - DJANGO_ENV        : development | production (默认 development)
    - DJANGO_DEBUG      : true/false (默认随 DJANGO_ENV)
    - DJANGO_HOST       : 监听地址 (默认 0.0.0.0)
    - DJASKO_PORT       : 监听端口 (默认 8000)

用法：
    python run.py              # 启动开发服务器
    python run.py 8080        # 指定端口
"""

import os
import sys
import socket
import threading
from datetime import datetime

# 设置 Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cimf_django.settings')

# 环境变量
ENV = os.environ.get('DJANGO_ENV', 'development').lower()
DEBUG = os.environ.get('DJANGO_DEBUG', 'true' if ENV == 'development' else 'false').lower() in ('true', '1', 't', 'yes', 'on')
HOST = os.environ.get('DJANGO_HOST', '0.0.0.0')

# 端口从命令行参数或环境变量获取
if len(sys.argv) > 1 and sys.argv[1].isdigit():
    CUSTOM_PORT = int(sys.argv[1])
else:
    CUSTOM_PORT = None
PORT = CUSTOM_PORT if CUSTOM_PORT else int(os.environ.get('DJANGO_PORT', '8000'))


def check_database():
    """检查数据库状态"""
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'django.db')
    
    if not os.path.exists(db_path):
        print(f"\n未检测到数据库文件: {db_path}")
        print("将创建新数据库...")
        print("执行 python manage.py migrate ...")
        os.system('python manage.py migrate')
        print("数据库初始化完成!")
    else:
        print(f"\n数据库路径: {db_path}")


def validate_and_fix_installed_apps():
    """
    验证 INSTALLED_APPS 中的模块状态
    
    注意：由于 settings.py 已使用动态扫描，此函数仅做验证和警告输出，
    不再修改 INSTALLED_APPS（已在 settings.py 中处理）
    """
    from django.conf import settings
    
    # 检查已加载的模块
    loaded_node_modules = [app for app in settings.INSTALLED_APPS if app.startswith('modules.')]
    
    print(f"  已加载 Node 模块: {', '.join(loaded_node_modules) if loaded_node_modules else '无'}")


def init_modules():
    """初始化 Node 模块 - 列表加载 + 安装"""
    print("\n初始化 Node 模块...")
    try:
        import django
        django.setup()
        from core.module.services import ModuleService
        
        # 扫描并注册所有模块（不安装）
        modules = ModuleService.scan_modules()
        registered_count = 0
        
        for m in modules:
            module = ModuleService.register_module(m)
            registered_count += 1
            print(f"  已注册: {m['name']}")
        
        print(f"模块注册完成: {registered_count} 个模块")
    except Exception as e:
        print(f"模块初始化失败: {e}")


def check_production():
    """生产环境安全检查"""
    if ENV == 'production':
        if DEBUG:
            print("\n" + "=" * 80)
            print("【致命错误】生产环境禁止开启 debug 模式！")
            print("请设置：export DJANGO_ENV=production && export DJANGO_DEBUG=false")
            print("=" * 80 + "\n")
            sys.exit(1)
        
        try:
            from django.conf import settings
            if not settings.SECRET_KEY or len(settings.SECRET_KEY) < 48:
                print("\n" + "=" * 80)
                print("【警告】SECRET_KEY 太弱，建议设置为至少48位随机字符串")
                print("=" * 80 + "\n")
        except Exception:
            pass


def main():
    """主入口"""
    # 检查生产环境
    check_production()
    
    # 验证并修复 INSTALLED_APPS
    validate_and_fix_installed_apps()
    
    # 检查数据库
    check_database()
    
    # 初始化 Node 模块
    init_modules()
    
    # 启动信息 - 立即刷新输出
    print("\n" + "=" * 70, flush=True)
    print(f"CIMF 管理系统启动 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})", flush=True)
    print(f"Python: {sys.version.split()[0]}", flush=True)
    print(f"环境: {ENV.upper()}", flush=True)
    print(f"Debug: {DEBUG}", flush=True)
    print(f"监听: {HOST}:{PORT}", flush=True)
    
    try:
        local_ip = socket.gethostbyname(socket.gethostname())
        if local_ip != '127.0.0.1':
            print(f"局域网访问: http://{local_ip}:{PORT}", flush=True)
    except Exception:
        pass
    
    print(f"本地访问: http://localhost:{PORT}", flush=True)
    print(f"后台管理: http://localhost:{PORT}/admin/", flush=True)
    print("=" * 70 + "\n", flush=True)
    
    if ENV == 'production' or not DEBUG:
        print("生产环境推荐启动命令：", flush=True)
        print("  gunicorn cimf_django.wsgi:application -w 4 -b 0.0.0.0:8000", flush=True)
        print("-" * 70 + "\n", flush=True)
    
    from django.core.management import execute_from_command_line
    # 模拟 manage.py 的行为，设置正确的 sys.argv
    # 使用 --noreload 避免 Django autoreload 导致 Cron 服务状态丢失
    sys.argv = ['manage.py', 'runserver', f'{HOST}:{PORT}', '--noreload']
    
    # 启动后台线程初始化 Cron 服务（在 Django 加载完成后）
    def start_cron():
        import django
        django.setup()  # 确保 Django 应用已加载
        from core.services import init_cron_service
        init_cron_service()
    
    cron_thread = threading.Thread(target=start_cron, daemon=True)
    cron_thread.start()
    
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
