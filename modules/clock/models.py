"""
时钟模块占位模型

此模型仅用于在 Django 中注册 clock 模块的数据库表。
当前版本无业务字段，后续扩展时可添加时钟相关配置字段。
"""

from django.db import models


class ClockModel(models.Model):
    class Meta:
        db_table = "clock_model"
        verbose_name = "时钟"
        verbose_name_plural = "时钟"

    def __str__(self):
        return f"ClockModel #{self.pk}"
