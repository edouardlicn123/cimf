# app/utils.py
"""
FFE 项目跟进系统 - 通用工具函数集合

存放不依赖特定蓝图/模型的纯函数或辅助类。
尽量保持无副作用、易测试、文档清晰。
"""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Union, Set
from urllib.parse import urlparse
from flask import current_app, url_for, safe_join
from werkzeug.utils import secure_filename


# ──────────────────────────────────────────────
# 文件上传相关
# ──────────────────────────────────────────────

def allowed_file(filename: str, allowed_extensions: Optional[Set[str]] = None) -> bool:
    """
    检查文件名是否在允许的扩展名集合中（不区分大小写）
    
    Args:
        filename: 文件名
        allowed_extensions: 允许的扩展名集合（默认使用 config 中的值）
    
    Returns:
        bool: 是否允许上传
    """
    if not allowed_extensions:
        allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'xlsx', 'docx'})
    
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in allowed_extensions


def get_secure_upload_path(filename: str, subfolder: Optional[str] = None) -> str:
    """
    生成安全的上传文件完整路径
    
    - 使用 secure_filename 防止路径穿越
    - 支持子目录（例如按用户ID或项目ID分目录）
    - 自动添加时间戳前缀避免覆盖（可选）
    
    Args:
        filename: 原文件名
        subfolder: 可选子目录名（如 'user_123' 或 'project_456'）
    
    Returns:
        str: 完整的服务器文件路径
    """
    filename = secure_filename(filename)
    
    # 可选：添加时间戳前缀避免同名覆盖
    # timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    # filename = f"{timestamp}_{filename}"
    
    upload_folder = current_app.config['UPLOAD_FOLDER']
    
    if subfolder:
        # 防止 subfolder 路径穿越
        subfolder = secure_filename(subfolder)
        target_dir = safe_join(upload_folder, subfolder)
    else:
        target_dir = upload_folder
    
    os.makedirs(target_dir, exist_ok=True)
    return str(Path(target_dir) / filename)


def get_upload_url(filename: str, subfolder: Optional[str] = None) -> str:
    """
    生成上传文件的可访问 URL（假设有静态路由 /uploads）
    
    生产环境建议使用 nginx/云存储直链，此函数仅作参考
    """
    if subfolder:
        path = f"{subfolder}/{filename}"
    else:
        path = filename
    
    # 如果项目配置了自定义上传域名，可在此处替换
    return url_for('static', filename=f'uploads/{path}', _external=True)


# ──────────────────────────────────────────────
# 字符串 & 格式化工具
# ──────────────────────────────────────────────

def clean_username(username: str) -> str:
    """清理用户名：去除前后空格，转换为小写（视需求）"""
    return (username or '').strip()


def is_safe_url(target: str) -> bool:
    """
    验证 next 重定向目标是否安全（防开放重定向）
    
    只允许同源或相对路径
    """
    if not target:
        return False
    
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc


def format_currency(value: Union[int, float], currency: str = 'USD') -> str:
    """格式化金额（带千位分隔符）"""
    if value is None:
        return "—"
    return f"{value:,.2f} {currency}"


def truncate_text(text: str, max_length: int = 120, suffix: str = "...") -> str:
    """截断长文本，常用于列表显示"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


# ──────────────────────────────────────────────
# 调试 & 日志辅助（开发阶段常用）
# ──────────────────────────────────────────────

def debug_print(*args, **kwargs):
    """开发环境专用的彩色打印（生产环境自动静默）"""
    if current_app.debug:
        from termcolor import colored
        print(colored(f"[DEBUG {datetime.now().strftime('%H:%M:%S')}]", "cyan"), *args, **kwargs)


# ──────────────────────────────────────────────
# Jinja2 自定义过滤器（在 __init__.py 中注册使用）
# ──────────────────────────────────────────────

def register_jinja_filters(app):
    """在 create_app() 中调用：app.jinja_env.filters.update({...})"""
    filters = {
        'clean_username': clean_username,
        'format_currency': format_currency,
        'truncate': truncate_text,
        'datetimeformat': lambda value, fmt='%Y-%m-%d %H:%M': 
            value.strftime(fmt) if isinstance(value, datetime) else value,
    }
    app.jinja_env.filters.update(filters)


# 示例：在 app/__init__.py 的 create_app() 末尾添加：
# from app.utils import register_jinja_filters
# register_jinja_filters(app)
