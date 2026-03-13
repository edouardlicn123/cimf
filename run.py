#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run.py - FFE 项目跟进系统启动入口

开发环境直接运行：python run.py
生产环境强烈推荐使用 WSGI 服务器（如 gunicorn / uvicorn）

环境变量支持：
- FLASK_ENV          : development | production (默认 development)
- FLASK_DEBUG        : true/false (默认随 FLASK_ENV)
- FLASK_HOST         : 监听地址 (默认 0.0.0.0)
- FLASK_PORT         : 监听端口 (默认 5001)
"""

import os
import sys
import socket
from datetime import datetime
from flask import current_app
from app import create_app, db
from dotenv import load_dotenv

load_dotenv('config.env')  # 加载 config.env 文件（如果有）

# ──────────────────────────────────────────────
# 环境变量读取
# ──────────────────────────────────────────────
ENV = os.environ.get('FLASK_ENV', 'development').lower()
DEBUG = os.environ.get('FLASK_DEBUG', 'true' if ENV == 'development' else 'false').lower() in ('true', '1', 't', 'yes', 'on')
HOST = os.environ.get('FLASK_HOST', '0.0.0.0')
PORT = int(os.environ.get('FLASK_PORT', '5001'))

# ──────────────────────────────────────────────
# 应用初始化（只调用一次 create_app）
# ──────────────────────────────────────────────
app = create_app()

# ──────────────────────────────────────────────
# 主入口保护
# ──────────────────────────────────────────────
if __name__ == '__main__':
    # ── 数据库初始化（交互式安全版） ────────────────────────────────────────
    db_path = os.path.join(app.instance_path, 'site.db')
    perform_init = False

    print(f"\n数据库路径: {db_path}")

    if os.path.exists(db_path):
        print(f"检测到现有数据库文件: {db_path}")
        choice = input("是否继续执行? (y/n): ").strip().lower()
        if choice == 'y':
            choice = input("是否备份并重新初始化数据库? (y/n): ").strip().lower()
            if choice == 'y':
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_path = f"{db_path}.{timestamp}.bak"
                os.rename(db_path, backup_path)
                print(f"已备份原有数据库到: {backup_path}")
                perform_init = True
            else:
                print("跳过数据库初始化")
        else:
            print("退出初始化")
            sys.exit(0)
    else:
        print("未检测到数据库文件，将创建新数据库")
        perform_init = True

    if perform_init:
        with app.app_context():
            print("执行 db.create_all() ...")
            db.create_all()
            print("数据库初始化完成")

    # ── 生产环境强制检查 ────────────────────────────────────────
    if ENV == 'production':
        if DEBUG:
            print("\n" + "="*80)
            print("【致命错误】生产环境禁止开启 debug 模式！")
            print("请设置：export FLASK_ENV=production && export FLASK_DEBUG=false")
            print("="*80 + "\n")
            sys.exit(1)

        if not app.config.get('SECRET_KEY') or len(app.config['SECRET_KEY']) < 48:
            print("\n" + "="*80)
            print("【致命错误】生产环境 SECRET_KEY 未设置或太弱！")
            print("请设置环境变量 SECRET_KEY 为至少48位随机字符串")
            print("="*80 + "\n")
            sys.exit(1)

    # ── 启动信息打印 ────────────────────────────────────────────
    print("\n" + "="*70)
    print(f"FFE 项目跟进系统启动 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
    print(f"Python: {sys.version.split()[0]}")
    print(f"环境: {ENV.upper()}")
    print(f"Debug: {DEBUG}")
    print(f"监听: {HOST}:{PORT}")

    try:
        local_ip = socket.gethostbyname(socket.gethostname())
        if local_ip != '127.0.0.1':
            print(f"局域网访问示例: http://{local_ip}:{PORT}")
    except Exception:
        pass

    print(f"本地访问: http://localhost:{PORT}")
    print(f"后台管理: http://localhost:{PORT}/admin/system-settings (登录后)")
    print("="*70 + "\n")

    # ── 生产部署推荐 ────────────────────────────────────────────
    if ENV == 'production' or not DEBUG:
        print("生产环境推荐启动命令：")
        print("  gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 run:app")
        print("或 uvicorn：")
        print("  uvicorn run:app --host 0.0.0.0 --port 5000 --workers 4")
        print("-"*70 + "\n")

    # ── 实际启动 ─────────────────────────────────────────────────
    try:
        app.run(
            debug=DEBUG,
            host=HOST,
            port=PORT,
            use_reloader=DEBUG and not os.environ.get('FLASK_RUN_NO_RELOAD'),
            threaded=DEBUG,
        )
    except OSError as e:
        if 'Address already in use' in str(e):
            print(f"端口 {PORT} 已被占用！请释放端口或修改 FLASK_PORT", file=sys.stderr)
            sys.exit(1)
        raise
    except KeyboardInterrupt:
        print("\n用户中断，正常退出")
