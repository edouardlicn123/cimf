# -*- coding: utf-8 -*-
"""
模块注册表和工具类型模型
"""

import os

from django.db import models
from django.conf import settings
from core.models import BaseModel
from core.constants import ModuleType


class Module(BaseModel):
    """模块注册表"""
    
    module_id = models.CharField(max_length=50, unique=True, verbose_name='模块ID')
    name = models.CharField(max_length=100, verbose_name='模块名称')
    version = models.CharField(max_length=20, verbose_name='版本号')
    author = models.CharField(max_length=100, blank=True, null=True, verbose_name='作者')
    description = models.TextField(blank=True, null=True, verbose_name='描述')
    icon = models.CharField(max_length=50, default='bi-wrench', verbose_name='图标')
    path = models.CharField(max_length=200, verbose_name='模块路径')
    
    is_installed = models.BooleanField(default=False, verbose_name='是否已安装')
    is_active = models.BooleanField(default=False, verbose_name='是否启用')
    is_system = models.BooleanField(default=False, verbose_name='是否系统默认模块')
    module_type = models.CharField(max_length=20, default=ModuleType.NODE, choices=ModuleType.CHOICES, verbose_name='模块类型')
    install_on_init = models.BooleanField(default=True, verbose_name='初始化时安装')
    
    installed_at = models.DateTimeField(null=True, blank=True, verbose_name='安装时间')
    activated_at = models.DateTimeField(null=True, blank=True, verbose_name='启用时间')
    
    class Meta:
        db_table = 'modules'
        verbose_name = '模块'
        verbose_name_plural = '模块'
        ordering = ['name']
    
    @property
    def path_exists(self) -> bool:
        """检查模块目录是否存在"""
        if not self.path:
            return False
        module_path = os.path.join(settings.BASE_DIR, 'modules', self.path)
        return os.path.isdir(module_path)
    
    def __str__(self):
        return f"{self.name} ({self.module_id})"


class ToolType(BaseModel):
    """工具类型模型"""
    
    name = models.CharField(max_length=100, verbose_name='工具名称')
    slug = models.CharField(max_length=50, unique=True, db_index=True, verbose_name='标识符')
    description = models.CharField(max_length=500, blank=True, null=True, verbose_name='描述')
    icon = models.CharField(max_length=50, default='bi-wrench', verbose_name='图标')
    author = models.CharField(max_length=100, blank=True, null=True, verbose_name='作者')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    
    class Meta:
        db_table = 'tool_types'
        verbose_name = '工具类型'
        verbose_name_plural = '工具类型'
        ordering = ['name']
    
    def __str__(self):
        return self.name
