# -*- coding: utf-8 -*-
"""
统一日志服务 - 读写合一

功能：
- 写日志：从原 logging_utils.py 迁移的安全事件记录
- 读日志：日志文件读取与页面展示

版本：1.0
"""

import logging
import os
from pathlib import Path
from typing import List, Dict, Optional
from django.conf import settings


class LogService:
    """统一日志服务"""
    
    LOG_DIR = Path(settings.BASE_DIR) / 'storage' / 'logs'
    
    LOG_FILES = {
        'cimf': 'cimf.log',
        'error': 'error.log',
        'security': 'security.log',
    }
    
    _security_logger = None
    
    @classmethod
    def _get_security_logger(cls):
        if cls._security_logger is None:
            cls._security_logger = logging.getLogger('django.security')
        return cls._security_logger
    
    # ===== 写日志功能 =====
    
    @staticmethod
    def get_client_ip(request) -> str:
        """获取客户端 IP"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', 'unknown')
    
    @classmethod
    def log_login_attempt(cls, request, username: str, success: bool, reason: str = None):
        """记录登录尝试"""
        logger = cls._get_security_logger()
        level = logging.INFO if success else logging.WARNING
        ip = cls.get_client_ip(request)
        message = f"Login attempt: user={username}, success={success}, ip={ip}"
        if reason:
            message += f", reason={reason}"
        logger.log(level, message)
    
    @classmethod
    def log_logout(cls, user, username: str, ip: str):
        """记录登出"""
        logger = cls._get_security_logger()
        logger.info(f"Logout: user={username}, ip={ip}")
    
    @classmethod
    def log_permission_denied(cls, request, user, resource: str, reason: str = None):
        """记录权限拒绝"""
        logger = cls._get_security_logger()
        ip = cls.get_client_ip(request)
        username = user.username if user else 'anonymous'
        message = f"Permission denied: user={username}, resource={resource}, ip={ip}"
        if reason:
            message += f", reason={reason}"
        logger.warning(message)
    
    @classmethod
    def log_security_event(cls, event_type: str, details: str, level=logging.INFO):
        """记录安全事件"""
        logger = cls._get_security_logger()
        logger.log(level, f"Security event: {event_type}, details={details}")
    
    @classmethod
    def log_api_access(cls, request, endpoint: str, user=None):
        """记录 API 访问"""
        logger = cls._get_security_logger()
        ip = cls.get_client_ip(request)
        username = user.username if user else 'anonymous'
        logger.info(f"API access: user={username}, endpoint={endpoint}, ip={ip}")
    
    @classmethod
    def log_data_export(cls, request, user, export_type: str, record_count: int):
        """记录数据导出"""
        logger = cls._get_security_logger()
        ip = cls.get_client_ip(request)
        logger.info(
            f"Data export: user={user.username}, type={export_type}, "
            f"count={record_count}, ip={ip}"
        )
    
    @classmethod
    def log_failed_validation(cls, request, form_name: str, errors: str):
        """记录验证失败"""
        logger = cls._get_security_logger()
        ip = cls.get_client_ip(request)
        logger.warning(
            f"Validation failed: form={form_name}, errors={errors}, ip={ip}"
        )
    
    # ===== 读日志功能 =====
    
    @classmethod
    def get_log_files(cls) -> List[Dict]:
        """获取日志文件列表及基本信息"""
        files = []
        for key, filename in cls.LOG_FILES.items():
            filepath = cls.LOG_DIR / filename
            info = {
                'key': key,
                'name': filename,
                'exists': filepath.exists(),
                'size': filepath.stat().st_size if filepath.exists() else 0,
            }
            files.append(info)
        return files
    
    @classmethod
    def read_log(cls, log_type: str, page: int = 1, page_size: int = 100, 
                 level: str = None) -> Dict:
        """读取日志，支持分页和级别筛选"""
        filename = cls.LOG_FILES.get(log_type)
        if not filename:
            return {'lines': [], 'total': 0, 'page': page, 'page_size': page_size}
        
        filepath = cls.LOG_DIR / filename
        if not filepath.exists():
            return {'lines': [], 'total': 0, 'page': page, 'page_size': page_size}
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                all_lines = f.readlines()
        except Exception:
            return {'lines': [], 'total': 0, 'page': page, 'page_size': page_size, 'error': '无法读取文件'}
        
        total = len(all_lines)
        
        if level and level != 'all':
            filtered = [line for line in all_lines if level.upper() in line.upper()]
        else:
            filtered = all_lines
        
        total_filtered = len(filtered)
        
        start = (page - 1) * page_size
        end = start + page_size
        page_lines = filtered[start:end]
        
        parsed_lines = []
        for line in enumerate(page_lines, start=start + 1):
            parsed_lines.append({
                'line_num': line[0],
                'content': line[1].rstrip('\n')
            })
        
        return {
            'lines': parsed_lines,
            'total': total_filtered,
            'page': page,
            'page_size': page_size,
            'total_pages': (total_filtered + page_size - 1) // page_size,
        }
    
    @classmethod
    def get_log_stats(cls, log_type: str) -> Dict:
        """获取日志统计（总行数、各级别数量）"""
        filename = cls.LOG_FILES.get(log_type)
        if not filename:
            return {'total': 0, 'levels': {}}
        
        filepath = cls.LOG_DIR / filename
        if not filepath.exists():
            return {'total': 0, 'levels': {}}
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()
        except Exception:
            return {'total': 0, 'levels': {}}
        
        total = len(lines)
        levels = {'DEBUG': 0, 'INFO': 0, 'WARNING': 0, 'ERROR': 0}
        
        for line in lines:
            for lvl in levels:
                if lvl in line.upper():
                    levels[lvl] += 1
                    break
        
        return {'total': total, 'levels': levels}


# 兼容旧导入方式
log_login_attempt = LogService.log_login_attempt
log_logout = LogService.log_logout
log_permission_denied = LogService.log_permission_denied
log_security_event = LogService.log_security_event
log_api_access = LogService.log_api_access
log_data_export = LogService.log_data_export
log_failed_validation = LogService.log_failed_validation
get_client_ip = LogService.get_client_ip