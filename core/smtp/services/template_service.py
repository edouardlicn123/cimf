# -*- coding: utf-8 -*-
"""
邮件模板服务
"""

import logging
from typing import Optional, List, Tuple
from jinja2 import Template, UndefinedError
from core.smtp.models import EmailTemplate

logger = logging.getLogger(__name__)


class TemplateService:
    """邮件模板服务"""

    @classmethod
    def get_template(cls, name: str) -> Optional[EmailTemplate]:
        """获取模板"""
        return EmailTemplate.objects.filter(name=name, is_active=True).first()

    @classmethod
    def _render_safe(cls, template_text: str, context: dict) -> str:
        """安全渲染模板，出错时返回空字符串"""
        try:
            return Template(template_text).render(**context)
        except UndefinedError as e:
            logger.error(f"邮件模板渲染错误: {e}")
            return ''

    @classmethod
    def render_subject(cls, template: EmailTemplate, context: dict) -> str:
        """渲染邮件主题"""
        return cls._render_safe(template.subject, context)

    @classmethod
    def render_body(cls, template: EmailTemplate, context: dict) -> Tuple[str, str]:
        """渲染邮件正文，返回 (html, text)"""
        html_body = cls._render_safe(template.html_body, context)
        text_body = cls._render_safe(template.text_body, context)
        return html_body, text_body

    @classmethod
    def list_templates(cls) -> List[EmailTemplate]:
        """列出所有模板"""
        return list(EmailTemplate.objects.filter(is_active=True).order_by('-created_at'))

    @classmethod
    def create_template(
        cls,
        name: str,
        subject: str,
        html_body: str,
        text_body: str = '',
        description: str = '',
    ) -> EmailTemplate:
        """创建模板"""
        return EmailTemplate.objects.create(
            name=name,
            subject=subject,
            html_body=html_body,
            text_body=text_body,
            description=description,
        )

    @classmethod
    def update_template(
        cls,
        template: EmailTemplate,
        subject: str = None,
        html_body: str = None,
        text_body: str = None,
        description: str = None,
        is_active: bool = None,
    ) -> EmailTemplate:
        """更新模板"""
        if subject is not None:
            template.subject = subject
        if html_body is not None:
            template.html_body = html_body
        if text_body is not None:
            template.text_body = text_body
        if description is not None:
            template.description = description
        if is_active is not None:
            template.is_active = is_active
        template.save()
        return template

    @classmethod
    def delete_template(cls, template: EmailTemplate) -> None:
        """删除模板"""
        template.delete()

    @classmethod
    def init_default_templates(cls) -> int:
        """
        初始化默认邮件模板
        
        Returns:
            创建的模板数量
        """
        default_templates = [
            {
                'name': 'verification_code',
                'subject': '【CIMF系统】您的验证码',
                'description': '用户注册、登录验证码邮件模板',
                'html_body': '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
        .content { background: #ffffff; padding: 30px; border: 1px solid #e0e0e0; border-top: none; }
        .footer { background: #f8f9fa; padding: 20px; text-align: center; font-size: 12px; color: #666; border-radius: 0 0 10px 10px; border: 1px solid #e0e0e0; border-top: none; }
        .code { background: #f4f4f4; padding: 15px; border-radius: 5px; font-family: monospace; font-size: 24px; text-align: center; letter-spacing: 8px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{{ system_name | default('CIMF系统') }}</h1>
        </div>
        <div class="content">
            <h2>验证码</h2>
            <p>您好，</p>
            <p>您的验证码是：</p>
            <div class="code">{{ code }}</div>
            <p>验证码将在 {{ expire_minutes }} 分钟后失效。</p>
            <p>如果您没有请求此验证码，请忽略此邮件。</p>
            <p style="margin-top: 30px;">
                祝好，<br>
                {{ system_name | default('CIMF系统') }} 团队
            </p>
        </div>
        <div class="footer">
            <p>此邮件由系统自动发送，请勿回复。</p>
            <p>&copy; {{ year | default('2026') }} {{ system_name | default('CIMF系统') }}. All rights reserved.</p>
        </div>
    </div>
</body>
</html>''',
                'text_body': '''{{ system_name | default('CIMF系统') }}

验证码

您好，

您的验证码是：{{ code }}

验证码将在 {{ expire_minutes }} 分钟后失效。

如果您没有请求此验证码，请忽略此邮件。

祝好，
{{ system_name | default('CIMF系统') }} 团队

---
此邮件由系统自动发送，请勿回复。
&copy; {{ year | default('2026') }} {{ system_name | default('CIMF系统') }}''',
            },
            {
                'name': 'password_reset',
                'subject': '【CIMF系统】密码重置链接',
                'description': '密码重置邮件模板',
                'html_body': '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
        .content { background: #ffffff; padding: 30px; border: 1px solid #e0e0e0; border-top: none; }
        .footer { background: #f8f9fa; padding: 20px; text-align: center; font-size: 12px; color: #666; border-radius: 0 0 10px 10px; border: 1px solid #e0e0e0; border-top: none; }
        .btn { display: inline-block; padding: 12px 30px; background: #f5576c; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{{ system_name | default('CIMF系统') }}</h1>
        </div>
        <div class="content">
            <h2>密码重置</h2>
            <p>您好，</p>
            <p>您请求重置密码，请点击下面的按钮：</p>
            <p style="text-align: center;">
                <a href="{{ reset_link }}" class="btn">重置密码</a>
            </p>
            <p>链接将在 {{ expire_hours }} 小时后失效。</p>
            <p>如果您没有请求重置密码，请忽略此邮件。</p>
            <p style="margin-top: 30px;">
                祝好，<br>
                {{ system_name | default('CIMF系统') }} 团队
            </p>
        </div>
        <div class="footer">
            <p>此邮件由系统自动发送，请勿回复。</p>
            <p>&copy; {{ year | default('2026') }} {{ system_name | default('CIMF系统') }}. All rights reserved.</p>
        </div>
    </div>
</body>
</html>''',
                'text_body': '''{{ system_name | default('CIMF系统') }}

密码重置

您好，

您请求重置密码，请访问以下链接：

{{ reset_link }}

链接将在 {{ expire_hours }} 小时后失效。

如果您没有请求重置密码，请忽略此邮件。

祝好，
{{ system_name | default('CIMF系统') }} 团队

---
此邮件由系统自动发送，请勿回复。
&copy; {{ year | default('2026') }} {{ system_name | default('CIMF系统') }}''',
            },
            {
                'name': 'notification',
                'subject': '【CIMF系统】{{ title }}',
                'description': '通用通知邮件模板',
                'html_body': '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
        .content { background: #ffffff; padding: 30px; border: 1px solid #e0e0e0; border-top: none; }
        .footer { background: #f8f9fa; padding: 20px; text-align: center; font-size: 12px; color: #666; border-radius: 0 0 10px 10px; border: 1px solid #e0e0e0; border-top: none; }
        .btn { display: inline-block; padding: 12px 30px; background: #4facfe; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{{ system_name | default('CIMF系统') }}</h1>
        </div>
        <div class="content">
            <h2>{{ title }}</h2>
            <p>{{ message }}</p>
            {% if action_url %}
            <p style="text-align: center;">
                <a href="{{ action_url }}" class="btn">{{ action_text | default('查看详情') }}</a>
            </p>
            {% endif %}
        </div>
        <div class="footer">
            <p>此邮件由系统自动发送，请勿回复。</p>
            <p>&copy; {{ year | default('2026') }} {{ system_name | default('CIMF系统') }}. All rights reserved.</p>
        </div>
    </div>
</body>
</html>''',
                'text_body': '''{{ system_name | default('CIMF系统') }}

{{ title }}

{{ message }}

{% if action_url %}
查看详情: {{ action_url }}
{% endif %}

---
此邮件由系统自动发送，请勿回复。
&copy; {{ year | default('2026') }} {{ system_name | default('CIMF系统') }}''',
            },
        ]
        
        # 批量查询已存在的模板名称（优化：避免循环查询）
        existing_names = set(EmailTemplate.objects.values_list('name', flat=True))
        
        templates_to_create = []
        for tmpl in default_templates:
            if tmpl['name'] not in existing_names:
                templates_to_create.append(EmailTemplate(
                    name=tmpl['name'],
                    subject=tmpl['subject'],
                    description=tmpl['description'],
                    html_body=tmpl['html_body'],
                    text_body=tmpl.get('text_body', ''),
                    is_active=True,
                ))
                existing_names.add(tmpl['name'])  # 更新内存缓存
        
        if templates_to_create:
            EmailTemplate.objects.bulk_create(templates_to_create, batch_size=10)
        
        return len(templates_to_create)
