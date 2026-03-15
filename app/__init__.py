# 文件路径：app/__init__.py
# 更新日期：2026-02-17
# 功能说明：Flask 应用工厂函数，负责全局配置加载、扩展初始化、蓝图统一注册、日志设置、安全检查、Jinja 过滤器定义、未授权处理等，是整个应用的启动入口与核心配置中心

import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, redirect, url_for, request, flash, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# 全局扩展实例（只在此文件定义一次，避免重复初始化）
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()

# 配置登录视图与提示信息
login_manager.login_view = 'auth.login'
login_manager.login_message = '请先登录系统'
login_manager.login_message_category = 'warning'


def create_app(config_name='default'):
    app = Flask(__name__)

    # ── 1. 加载配置（环境变量优先级最高） ────────────────────────────────────────────────
    from config import get_config
    cfg = get_config()
    app.config.from_object(cfg)

    # 强制覆盖关键敏感配置（环境变量 > 配置文件）
    app.config['SECRET_KEY'] = (
        os.environ.get('SECRET_KEY')
        or os.environ.get('FLASK_SECRET_KEY')
        or app.config.get('SECRET_KEY')
    )
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        os.environ.get('DATABASE_URL')
        or app.config.get('SQLALCHEMY_DATABASE_URI')
    )
    app.config['UPLOAD_FOLDER'] = (
        os.environ.get('UPLOAD_FOLDER')
        or app.config.get('UPLOAD_FOLDER', 'persistent_uploads')  # 与项目目录树保持一致
    )

    is_production = app.config.get('ENV') == 'production'

    # 开发环境调试信息（便于排查配置问题）
    if not is_production:
        print(f"[DEBUG] 环境: development")
        print(f"[DEBUG] 数据库 URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        print(f"[DEBUG] 项目根路径: {app.root_path}")
        print(f"[DEBUG] 上传目录: {app.config['UPLOAD_FOLDER']}")

    # ── 生产环境强制安全检查（防止低安全启动） ──
    if is_production:
        if not app.config.get('SECRET_KEY') or len(app.config['SECRET_KEY']) < 48:
            raise RuntimeError(
                "生产环境致命错误：SECRET_KEY 未设置或长度不足48字符！\n"
                "请通过环境变量 SECRET_KEY 设置强随机值。"
            )
        if app.debug:
            raise RuntimeError("生产环境禁止开启 debug 模式！")

    # ── 2. 确保关键目录存在并可写 ──
    upload_folder = app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)
    instance_dir = app.config.get('BASE_DIR', app.root_path) / 'instance'
    os.makedirs(instance_dir, exist_ok=True)

    if not is_production:
        print(f"[DEBUG] instance 目录已确保存在: {instance_dir}")
        print(f"[DEBUG] 上传目录已确保存在: {upload_folder}")

    # ── 3. 初始化 Flask 扩展 ──
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    # ── 4. 自定义 Jinja2 过滤器（用于模板中的防缓存与时间格式化） ──
    @app.template_filter('timestamp')
    def timestamp_filter(dummy=None):
        """返回当前时间戳（精确到秒），常用于静态资源版本号防缓存"""
        import time
        return str(int(time.time()))

    @app.template_filter('now_format')
    def now_format_filter(format_str='%Y%m%d%H%M%S'):
        """灵活格式化当前时间，支持自定义格式字符串"""
        return datetime.now().strftime(format_str)

    # ── 5. 日志配置（生产/非调试模式下写入旋转文件） ──
    if not app.debug and not app.testing:
        log_dir = 'logs'
        os.makedirs(log_dir, exist_ok=True)

        file_handler = RotatingFileHandler(
            os.path.join(log_dir, 'ffe.log'),
            maxBytes=10 * 1024 * 1024,   # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s [%(name)s:%(lineno)d] %(message)s'
        ))
        file_handler.setLevel(logging.INFO)

        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('FFE 项目跟进系统 - 应用启动成功')

    # ── 6. 未授权访问统一处理（支持 AJAX/JSON 与普通页面） ──
    @login_manager.unauthorized_handler
    def unauthorized():
        flash('请先登录系统才能访问该页面', 'warning')

        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        is_json = 'application/json' in request.headers.get('Accept', '')

        if is_ajax or is_json:
            return jsonify({'error': 'unauthorized', 'message': '请先登录系统'}), 401

        return redirect(url_for('auth.login', next=request.full_path))

    # ── 7. 用户加载器（从数据库加载当前登录用户） ──
    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return User.query.get(int(user_id))
        except (ValueError, TypeError):
            app.logger.warning(f"无效 user_id 尝试加载: {user_id}")
            return None

    # ── 8. 统一注册所有蓝图（通过 routes/__init__.py 集中管理） ──
    from app.routes import register_blueprints
    register_blueprints(app)

    # ── 9. 添加模板上下文处理器（提供自定义角色名称、系统名称、所有设置、时间戳） ──
    @app.context_processor
    def inject_role_labels():
        from app.services import SettingsService, UserRole
        import time
        import random
        role_labels = dict(UserRole.LABELS)
        custom_leader = SettingsService.get_setting('role_name_leader')
        custom_employee = SettingsService.get_setting('role_name_employee')
        if custom_leader:
            role_labels[UserRole.LEADER] = custom_leader
        if custom_employee:
            role_labels[UserRole.EMPLOYEE] = custom_employee
        
        system_name = SettingsService.get_setting('system_name') or 'CIMF'
        all_settings = SettingsService.get_all_settings()
        
        timestamp = str(int(time.time())) + str(random.randint(0, 999))
        now = datetime.now()
        
        try:
            from app.services.node.node_type_service import NodeTypeService
            node_types = NodeTypeService.get_all()
        except Exception:
            node_types = []
        
        try:
            from app.services.core.time_service import TimeService
            current_time = TimeService.get_current_time()
        except Exception:
            current_time = now.strftime('%Y-%m-%d %H:%M:%S')
        
        return dict(role_labels=role_labels, system_name=system_name, settings=all_settings, timestamp=timestamp, node_types=node_types, now=now, current_time=current_time)

    # ── 10. 数据库初始化（根据配置模式） ─────────────────────────────────────────────
    init_database(app)

    # ── 11. 初始化 Cron 调度服务 ─────────────────────────────────────────────
    from app.services.core.cron_service import get_cron_service
    from app.services.core.tasks import TimeSyncTask, CacheCleanupTask
    
    cron = get_cron_service()
    cron.init_app(app)  # 传入 app 以便在后台线程中使用 app context
    cron.register(TimeSyncTask())
    cron.register(CacheCleanupTask())
    cron.start()
    cron.set_app_ready(True)  # 立即启用任务
    app.logger.info("Cron 调度服务已启动")

    app.logger.info("FFE 项目跟进系统 - 应用初始化完成")
    return app


def init_database(app):
    """根据配置模式初始化数据库
    
    初始化顺序：
    1. 创建数据库表（schema_only/auto 模式）
    2. 初始化种子数据（仅 auto 模式 + DB_SEED_DATA=true）
       - 系统设置（SettingsService）
       - 词汇表数据（TaxonomyService）
    """
    mode = app.config.get('DB_INIT_MODE', 'none')
    
    if mode == 'none':
        app.logger.info("数据库初始化已禁用（DB_INIT_MODE=none），请使用 Flask-Migrate 管理")
        return
    
    with app.app_context():
        # 步骤 1: 创建表
        if mode in ('auto', 'schema_only'):
            db.create_all()
            app.logger.info("数据库表创建完成")
        
        # 步骤 2: 种子数据
        if mode == 'auto' and app.config.get('DB_SEED_DATA'):
            # 初始化词汇表
            from app.modules.core.taxonomy.service import TaxonomyService
            TaxonomyService.init_default_taxonomies()
            app.logger.info("词汇表数据初始化完成")
            
            # 初始化节点类型
            from app.services.node.node_type_service import NodeTypeService
            NodeTypeService.init_default_node_types()
            app.logger.info("节点类型数据初始化完成")
