# -*- coding: utf-8 -*-
"""
===============================================================================
文件：version_service.py
路径：/home/edo/cimf/core/services/version_service.py
===============================================================================

功能说明：
    版本服务，提供应用版本和 API 版本管理
    
    版本控制：
    - 应用版本：用于前端展示和更新提示
    - API 版本：用于 API 兼容性检查

版本：
    - 1.0: 初始版本

依赖：
    - settings: Django 设置
"""

class VersionService:
    """版本服务类"""
    
    VERSION = '1.0.0'
    API_VERSION = 'v1'
    BUILD_DATE = '2026-04-09'
    
    @classmethod
    def get_version(cls):
        """获取应用版本号"""
        return cls.VERSION
    
    @classmethod
    def get_api_version(cls):
        """获取 API 版本号"""
        return cls.API_VERSION
    
    @classmethod
    def get_build_date(cls):
        """获取构建日期"""
        return cls.BUILD_DATE
    
    @classmethod
    def get_info(cls):
        """获取完整的版本信息"""
        return {
            'version': cls.VERSION,
            'api_version': cls.API_VERSION,
            'build_date': cls.BUILD_DATE,
        }
    
    @classmethod
    def check_compatibility(cls, client_version: str) -> bool:
        """检查客户端版本与 API 的兼容性"""
        if not client_version:
            return False
        
        if client_version.startswith('v'):
            client_version = client_version[1:]
        
        try:
            major = int(client_version.split('.')[0])
            return major >= 1
        except (ValueError, IndexError):
            return False
    
    @classmethod
    def get_supported_versions(cls) -> list:
        """获取支持的 API 版本列表"""
        return ['v1']