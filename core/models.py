# -*- coding: utf-8 -*-
"""
================================================================================
文件：models.py
路径：/home/edo/cimf-v2/core/models.py
================================================================================

功能说明：
    核心应用模型，包含用户、系统设置、词汇表等核心数据模型。
    
    主要模型：
    - User: 用户模型，扩展 Django AbstractUser
    - SystemSetting: 系统设置模型
    - Taxonomy: 词汇表模型
    - TaxonomyItem: 词汇项模型

版本：
    - 1.0: 初始版本，从 Flask 迁移

依赖：
    - django.contrib.auth: 用户认证
    - django.db: 数据模型
"""

from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
from datetime import timedelta
from core.constants import UserRole, UserTheme


class BaseModel(models.Model):
    """抽象基础模型，提供公共时间戳字段"""
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        abstract = True


class UserManager(BaseUserManager):
    """
    自定义用户管理器
    """
    
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('用户名不能为空')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_admin', True)
        return self.create_user(username, password, **extra_fields)


class User(AbstractUser):
    """
    用户表 - 系统核心实体
    
    用于登录认证、权限控制、项目归属、个人偏好存储等。
    扩展 Django AbstractUser，保留原有字段和功能。
    """
    
    class Role(models.TextChoices):
        MANAGER = UserRole.MANAGER, UserRole.LABELS[UserRole.MANAGER]
        LEADER = UserRole.LEADER, UserRole.LABELS[UserRole.LEADER]
        EMPLOYEE = UserRole.EMPLOYEE, UserRole.LABELS[UserRole.EMPLOYEE]
    
    class Theme(models.TextChoices):
        DEFAULT = UserTheme.DEFAULT, UserTheme.LABELS[UserTheme.DEFAULT]
        GOV = UserTheme.GOV, UserTheme.LABELS[UserTheme.GOV]
        INDIGO = UserTheme.INDIGO, UserTheme.LABELS[UserTheme.INDIGO]
        DOPAMINE = UserTheme.DOPAMINE, UserTheme.LABELS[UserTheme.DOPAMINE]
        MACARON = UserTheme.MACARON, UserTheme.LABELS[UserTheme.MACARON]
        TEAL = UserTheme.TEAL, UserTheme.LABELS[UserTheme.TEAL]
        UNIKLO = UserTheme.UNIKLO, UserTheme.LABELS[UserTheme.UNIKLO]
    
    nickname = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        verbose_name='昵称',
        help_text='显示昵称（仪表盘、项目成员列表等处优先显示）'
    )
    
    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name='邮箱',
        help_text='用户邮箱（可选，用于密码重置、通知等）'
    )
    
    is_admin = models.BooleanField(
        default=False,
        verbose_name='系统管理员',
        help_text='是否为系统管理员（拥有后台管理权限）'
    )
    
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.EMPLOYEE,
        verbose_name='角色',
        help_text='角色：manager=一类用户 / leader=二类用户 / employee=三类用户'
    )
    
    permissions = models.JSONField(
        default=list,
        verbose_name='权限列表',
        help_text='细粒度权限列表，如 ["system.manage", "user.manage"]'
    )
    
    failed_login_attempts = models.IntegerField(
        default=0,
        verbose_name='登录失败次数',
        help_text='连续登录失败次数，达到阈值后临时锁定'
    )
    
    locked_until = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='锁定截止时间',
        help_text='账号临时锁定的截止时间（为空表示未锁定）'
    )
    
    theme = models.CharField(
        max_length=20,
        choices=Theme.choices,
        default=Theme.DEFAULT,
        verbose_name='界面主题'
    )
    
    notifications_enabled = models.BooleanField(
        default=True,
        verbose_name='开启通知',
        help_text='是否开启系统通知（新项目、任务提醒等）'
    )
    
    preferred_language = models.CharField(
        max_length=10,
        default='zh',
        verbose_name='首选语言',
        help_text='首选界面语言：zh / en'
    )
    
    navigation_cards = models.JSONField(
        default=list,
        blank=True,
        verbose_name='导航卡片配置',
        help_text='用户自定义导航卡片，存储为JSON数组，每张卡片包含position字段(1-12)'
    )
    
    last_login_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='最后登录时间'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )
    
    objects = UserManager()
    
    class Meta:
        db_table = 'users'
        verbose_name = '用户'
        verbose_name_plural = '用户'
    
    def __str__(self):
        display_name = self.nickname or self.username
        return f'{display_name} (id:{self.id})'  # 注意：如果循环打印，建议使用 select_related('node_type')
    
    def is_locked(self) -> bool:
        """判断账号是否处于锁定状态"""
        return self.locked_until is not None and self.locked_until > timezone.now()
    
    def record_login(self) -> None:
        """记录成功登录时间"""
        self.last_login_at = timezone.now()
        self.failed_login_attempts = 0
        self.locked_until = None
        self.save(update_fields=['last_login_at', 'failed_login_attempts', 'locked_until'])
    
    def record_failed_attempt(self) -> None:
        """记录登录失败，达到阈值后锁定账号"""
        from core.services import AuthService
        LOCK_THRESHOLD = AuthService.get_login_max_failures()
        LOCK_MINUTES = AuthService.get_login_lock_minutes()
        
        self.failed_login_attempts += 1
        
        if self.failed_login_attempts >= LOCK_THRESHOLD:
            self.locked_until = timezone.now() + timedelta(minutes=LOCK_MINUTES)
        self.save(update_fields=['failed_login_attempts', 'locked_until'])
    
    def reset_failed_attempts(self) -> None:
        """登录成功或手动重置时，清零失败计数并解除锁定"""
        self.failed_login_attempts = 0
        self.locked_until = None
        self.save(update_fields=['failed_login_attempts', 'locked_until'])


class SystemSetting(models.Model):
    """
    系统设置表 - 键值对存储
    
    整个系统只有多条记录，每条记录代表一个配置项（key + value）
    通过 SettingsService 统一读写，默认值在服务层处理
    """
    
    key = models.CharField(
        max_length=128,
        unique=True,
        db_index=True,
        verbose_name='配置键',
        help_text='配置键名（唯一，例如 "upload_max_size_mb"）'
    )
    
    value = models.TextField(
        verbose_name='配置值',
        help_text='配置值（统一存字符串，服务层负责类型转换）'
    )
    
    description = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='描述'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )
    
    class Meta:
        db_table = 'system_settings'
        verbose_name = '系统设置'
        verbose_name_plural = '系统设置'
    
    def __str__(self):
        return f'{self.key}: {self.value}'


class Taxonomy(BaseModel):
    """
    词汇表模型
    
    用于分类和组织内容的层级结构，如：项目类型、标签、状态等
    """
    
    name = models.CharField(
        max_length=128,
        verbose_name='词汇表名称'
    )
    
    slug = models.CharField(
        max_length=128,
        unique=True,
        db_index=True,
        verbose_name='标识符',
        help_text='URL 标识'
    )
    
    description = models.CharField(
        max_length=512,
        blank=True,
        null=True,
        verbose_name='描述'
    )
    
    class Meta:
        db_table = 'taxonomies'
        verbose_name = '词汇表'
        verbose_name_plural = '词汇表'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class TaxonomyItem(BaseModel):
    """
    词汇项模型
    
    属于某个词汇表的具体项目
    """
    
    taxonomy = models.ForeignKey(
        Taxonomy,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='所属词汇表'
    )
    
    name = models.CharField(
        max_length=256,
        verbose_name='词汇名称'
    )
    
    description = models.CharField(
        max_length=512,
        blank=True,
        null=True,
        verbose_name='描述'
    )
    
    weight = models.IntegerField(
        default=0,
        verbose_name='排序权重'
    )
    
    class Meta:
        db_table = 'taxonomy_items'
        verbose_name = '词汇项'
        verbose_name_plural = '词汇项'
        ordering = ['weight', 'name']
    
    def __str__(self):
        return self.name


class ChinaRegion(models.Model):
    """
    中国行政区划
    
    使用自关联实现省-市-县三级层级结构
    """
    
    LEVEL_CHOICES = [
        (1, '省级'),
        (2, '地级市'),
        (3, '县/区'),
    ]
    
    code = models.CharField(
        max_length=6,
        unique=True,
        verbose_name='行政区划代码'
    )
    
    name = models.CharField(
        max_length=100,
        verbose_name='名称'
    )
    
    level = models.IntegerField(
        choices=LEVEL_CHOICES,
        verbose_name='层级'
    )
    
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='父级行政区划'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'china_regions'
        verbose_name = '行政区划'
        verbose_name_plural = '行政区划'
        ordering = ['code']
    
    def __str__(self):
        return f'{self.name} ({self.code})'
    
    @property
    def full_path(self):
        """获取完整路径"""
        parts = [self.name]
        parent = self.parent
        while parent:
            parts.append(parent.name)
            parent = parent.parent
        return ' - '.join(reversed(parts))
