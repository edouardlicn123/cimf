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

    VERSION = "2.001"
    API_VERSION = "v1"
    BUILD_DATE = "2026-07-05"

    @classmethod
    def get_info(cls):
        """获取完整的版本信息"""
        return {
            "version": cls.VERSION,
            "api_version": cls.API_VERSION,
            "build_date": cls.BUILD_DATE,
        }
