"""
默认邮件模板常量
"""

WELCOME_TEMPLATE = """<!DOCTYPE html>
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
            <h2>欢迎加入</h2>
            <p>您好，</p>
            <p>欢迎加入 {{ system_name | default('CIMF系统') }}！</p>
            <p>您的账号已成功创建。</p>
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
</html>"""

WELCOME_TEXT_TEMPLATE = """{{ system_name | default('CIMF系统') }}

欢迎加入

您好，

欢迎加入 {{ system_name | default('CIMF系统') }}！

您的账号已成功创建。

祝好，
{{ system_name | default('CIMF系统') }} 团队

---
此邮件由系统自动发送，请勿回复。
&copy; {{ year | default('2026') }} {{ system_name | default('CIMF系统') }}"""

RESET_PASSWORD_TEMPLATE = """<!DOCTYPE html>
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
                <a href="{{ reset_link | safe }}" class="btn">重置密码</a>
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
</html>"""

RESET_PASSWORD_TEXT_TEMPLATE = """{{ system_name | default('CIMF系统') }}

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
&copy; {{ year | default('2026') }} {{ system_name | default('CIMF系统') }}"""

VERIFICATION_CODE_TEMPLATE = """<!DOCTYPE html>
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
</html>"""

VERIFICATION_CODE_TEXT_TEMPLATE = """{{ system_name | default('CIMF系统') }}

验证码

您好，

您的验证码是：{{ code }}

验证码将在 {{ expire_minutes }} 分钟后失效。

如果您没有请求此验证码，请忽略此邮件。

祝好，
{{ system_name | default('CIMF系统') }} 团队

---
此邮件由系统自动发送，请勿回复。
&copy; {{ year | default('2026') }} {{ system_name | default('CIMF系统') }}"""

NOTIFICATION_TEMPLATE = """<!DOCTYPE html>
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
                <a href="{{ action_url | safe }}" class="btn">{{ action_text | default('查看详情') }}</a>
            </p>
            {% endif %}
        </div>
        <div class="footer">
            <p>此邮件由系统自动发送，请勿回复。</p>
            <p>&copy; {{ year | default('2026') }} {{ system_name | default('CIMF系统') }}. All rights reserved.</p>
        </div>
    </div>
</body>
</html>"""

NOTIFICATION_TEXT_TEMPLATE = """{{ system_name | default('CIMF系统') }}

{{ title }}

{{ message }}

{% if action_url %}
查看详情: {{ action_url }}
{% endif %}

---
此邮件由系统自动发送，请勿回复。
&copy; {{ year | default('2026') }} {{ system_name | default('CIMF系统') }}"""

DEFAULT_TEMPLATES = {
    "verification_code": {
        "name": "验证码",
        "subject": "【CIMF系统】您的验证码",
        "description": "用户注册、登录验证码邮件模板",
        "html_body": VERIFICATION_CODE_TEMPLATE,
        "text_body": VERIFICATION_CODE_TEXT_TEMPLATE,
    },
    "password_reset": {
        "name": "密码重置",
        "subject": "【CIMF系统】密码重置链接",
        "description": "密码重置邮件模板",
        "html_body": RESET_PASSWORD_TEMPLATE,
        "text_body": RESET_PASSWORD_TEXT_TEMPLATE,
    },
    "notification": {
        "name": "通知邮件",
        "subject": "【CIMF系统】{{ title }}",
        "description": "通用通知邮件模板",
        "html_body": NOTIFICATION_TEMPLATE,
        "text_body": NOTIFICATION_TEXT_TEMPLATE,
    },
}
