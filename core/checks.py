# -*- coding: utf-8 -*-
"""
自定义 Django 检查：自动检测缺少认证的视图
运行：./venv/bin/python manage.py check
"""
import os
import re
from django.core.checks import register, Warning


@register()
def check_auth_decorators(app_configs, **kwargs):
    """检查视图函数是否有认证保护"""
    errors = []
    
    # 需要检查的视图目录
    view_dirs = [
        os.path.join(os.path.dirname(__file__), 'views'),
        os.path.join(os.path.dirname(__file__), '..', 'modules'),
    ]
    
    # 有效的认证装饰器
    auth_decorators = ['login_required', 'login_required_json', 'admin_required']
    # API 函数应该使用的装饰器
    api_decorators = ['login_required_json', 'admin_required']
    
    for view_dir in view_dirs:
        if not os.path.exists(view_dir):
            continue
        
        for root, dirs, files in os.walk(view_dir):
            if 'venv' in root:
                continue
            
            for file in files:
                if file == 'views.py':
                    filepath = os.path.join(root, file)
                    errors.extend(_check_file_auth(filepath, auth_decorators, api_decorators))
    
    return errors


def _check_file_auth(filepath, auth_decorators, api_decorators):
    """检查单个文件中的视图函数认证"""
    errors = []
    
    try:
        with open(filepath) as f:
            content = f.read()
        
        # 提取所有视图函数及其装饰器
        func_dec_map = {}
        lines = content.split('\n')
        current_decorators = []
        
        for line in lines:
            stripped = line.strip()
            # 收集装饰器
            if stripped.startswith('@'):
                deco_match = re.match(r'@(\w+)', stripped)
                if deco_match:
                    current_decorators.append(deco_match.group(1))
            # 遇到函数定义，保存映射
            elif stripped.startswith('def '):
                func_match = re.match(r'def (\w+)\(', stripped)
                if func_match:
                    func_name = func_match.group(1)
                    if not func_name.startswith('_'):
                        func_dec_map[func_name] = current_decorators[:]
                    current_decorators = []
            else:
                # 非装饰器非函数定义，清空装饰器缓存
                if not stripped.startswith('#'):
                    current_decorators = []
        
        # 检查每个函数
        for func_name, decorators in func_dec_map.items():
            rel_path = os.path.relpath(filepath, os.path.dirname(__file__))
            
            # 检查1：是否有装饰器
            if not decorators:
                if not func_name.startswith('api_'):
                    errors.append(
                        Warning(
                            f'视图函数 {func_name}() 可能缺少认证装饰器',
                            hint='添加 @login_required 或确保全局中间件已启用',
                            obj=rel_path,
                            id='CIMF_W001',
                        )
                    )
                continue
            
            # 检查2：api_ 函数必须使用 JSON 装饰器
            if func_name.startswith('api_'):
                has_json_deco = any(d in api_decorators for d in decorators)
                if not has_json_deco:
                    errors.append(
                        Warning(
                            f'API 函数 {func_name}() 应使用 JSON 装饰器',
                            hint='使用 @login_required_json 或 @admin_required',
                            obj=rel_path,
                            id='CIMF_W002',
                        )
                    )
    
    except Exception:
        pass
    
    return errors
