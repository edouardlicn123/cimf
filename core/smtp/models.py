# -*- coding: utf-8 -*-
"""
SMTP 邮件模块模型
"""

from django.db import models
from django.utils import timezone


class EmailTemplate(models.Model):
    """邮件模板"""
    name = models.CharField(max_length=64, unique=True, verbose_name='模板标识')
    subject = models.CharField(max_length=255, verbose_name='邮件主题模板')
    html_body = models.TextField(verbose_name='HTML正文模板')
    text_body = models.TextField(blank=True, verbose_name='纯文本正文模板')
    description = models.CharField(max_length=255, blank=True, verbose_name='模板说明')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'email_templates'
        verbose_name = '邮件模板'
        verbose_name_plural = '邮件模板'

    def __str__(self):
        return self.name


class EmailLog(models.Model):
    """邮件发送记录"""
    STATUS_CHOICES = [
        ('pending', '待发送'),
        ('sending', '发送中'),
        ('sent', '已发送'),
        ('failed', '发送失败'),
    ]

    from_email = models.EmailField(verbose_name='发件人')
    to_email = models.TextField(verbose_name='收件人')
    subject = models.CharField(max_length=255, verbose_name='邮件主题')
    text_body = models.TextField(blank=True, verbose_name='纯文本正文')
    html_body = models.TextField(blank=True, verbose_name='HTML正文')
    template_name = models.CharField(max_length=64, blank=True, verbose_name='使用的模板')
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    error_message = models.TextField(blank=True, verbose_name='错误信息')
    retry_count = models.IntegerField(default=0, verbose_name='重试次数')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name='发送时间')

    class Meta:
        db_table = 'email_logs'
        verbose_name = '邮件发送记录'
        verbose_name_plural = '邮件发送记录'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.to_email} - {self.subject}'
