# -*- coding: utf-8 -*-
"""
SMTP 配置表单
"""

from django import forms
from core.smtp.services.smtp_service import SMTP_PRESETS


class SmtpConfigForm(forms.Form):
    """SMTP 配置表单"""
    
    provider = forms.ChoiceField(
        label='服务商预设',
        choices=[(k, v['name']) for k, v in SMTP_PRESETS.items()],
        initial='gmail_tls',
        help_text='选择邮件服务商，将自动填充服务器配置',
    )
    
    host = forms.CharField(
        label='SMTP 服务器',
        max_length=255,
        required=True,
        help_text='SMTP 服务器地址',
    )
    
    port = forms.IntegerField(
        label='端口',
        min_value=1,
        max_value=65535,
        initial=587,
    )
    
    use_ssl = forms.BooleanField(
        label='使用 SSL',
        required=False,
        help_text='使用 SSL 加密连接',
    )
    
    use_tls = forms.BooleanField(
        label='使用 TLS',
        required=False,
        initial=True,
        help_text='使用 TLS 加密连接（推荐）',
    )
    
    username = forms.EmailField(
        label='邮箱地址',
        max_length=255,
        required=True,
        help_text='SMTP 认证用户名，通常是您的邮箱地址',
    )
    
    password = forms.CharField(
        label='密码/授权码',
        max_length=255,
        required=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text='SMTP 认证密码或授权码（留空则保持不变）',
    )
    
    from_email = forms.EmailField(
        label='发件人邮箱',
        max_length=255,
        required=True,
        help_text='显示在邮件中的发件人地址',
    )
    
    from_name = forms.CharField(
        label='发件人名称',
        max_length=64,
        initial='仙芙CIMF',
        help_text='显示在邮件中的发件人名称',
    )
    
    timeout = forms.IntegerField(
        label='连接超时',
        min_value=5,
        max_value=300,
        initial=30,
        help_text='连接超时时间（秒）',
    )
    
    skip_verify = forms.BooleanField(
        label='跳过证书验证',
        required=False,
        initial=False,
        help_text='仅用于自签名证书（不建议生产环境使用）',
    )
    
    enabled = forms.BooleanField(
        label='启用邮件服务',
        required=False,
        initial=False,
        help_text='启用后将使用配置的 SMTP 服务器发送邮件',
    )
    
    batch_size = forms.IntegerField(
        label='每批发送数量',
        min_value=1,
        max_value=100,
        initial=10,
        help_text='每次处理的邮件数量',
    )
    
    rate_limit = forms.IntegerField(
        label='每分钟发送上限',
        min_value=0,
        max_value=1000,
        initial=0,
        help_text='每分钟发送的邮件数量上限（0=不限制）',
    )
    
    log_days = forms.IntegerField(
        label='日志保留天数',
        min_value=1,
        max_value=365,
        initial=30,
        help_text='邮件日志保留的天数',
    )
    
    failed_notify = forms.BooleanField(
        label='失败时通知',
        required=False,
        initial=False,
        help_text='邮件发送失败时发送通知邮件',
    )
    
    notify_email = forms.EmailField(
        label='通知邮箱',
        max_length=255,
        required=False,
        initial='',
        help_text='接收失败通知的邮箱地址',
    )
    
    system_url = forms.URLField(
        label='系统访问地址',
        max_length=255,
        required=False,
        initial='',
        help_text='系统访问URL（邮件中的链接将使用此地址）',
    )

    def clean(self):
        cleaned_data = super().clean()
        use_ssl = cleaned_data.get('use_ssl', False)
        use_tls = cleaned_data.get('use_tls', False)
        failed_notify = cleaned_data.get('failed_notify', False)
        notify_email = cleaned_data.get('notify_email', '')
        
        if use_ssl and use_tls:
            self.add_error('use_ssl', 'SSL 和 TLS 不能同时启用')
        
        if not use_ssl and not use_tls:
            self.add_error('use_tls', '请至少启用一种加密方式（推荐 TLS）')
        
        if failed_notify and not notify_email:
            self.add_error('notify_email', '启用失败通知时，请填写通知邮箱')
        
        return cleaned_data
