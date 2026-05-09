# SMTP 邮件服务模块设计方案

## 1. 概述

### 1.1 项目背景
CIMF 系统目前缺少邮件发送能力，用户和客户模型中虽然包含邮箱字段，但仅用于数据存储。为了支持后续功能（如密码重置、验证码发送、通知推送等），需要建立统一的邮件发送服务。

### 1.2 设计目标
- 提供统一的邮件发送服务，作为系统的后台基础设施
- 支持 Gmail、163、Proton 三家主流邮件服务商的预置配置
- 用户只需填写个人账户信息，无需了解 SMTP 技术细节
- 支持异步发送，不阻塞主业务流程
- 提供基础邮件模板系统，支持格式化邮件发送
- 配置入口集成到 `frame_admin` 管理界面

### 1.3 技术选型

| 组件 | 选型 | 说明 |
|------|------|------|
| 邮件库 | django.core.mail | Django 内置邮件模块，原生支持 SMTP，无需额外依赖 |
| 异步队列 | django-q2 | 轻量级任务队列，适合中小项目，无需 Redis（支持 ORM Broker） |
| 模板引擎 | Django Templates | 复用现有模板系统，降低学习成本 |

---

## 2. 架构设计

### 2.1 目录结构

```
core/
├── smtp/                          # SMTP 邮件模块
│   ├── __init__.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── smtp_service.py        # SMTP 配置管理服务
│   │   ├── email_service.py       # 邮件发送服务
│   │   └── template_service.py    # 邮件模板服务
│   ├── tasks.py                   # 异步任务定义
│   ├── forms.py                   # 配置表单
│   └── views.py                   # 视图函数

core/templates/core/smtp/          # SMTP 模板目录
├── config.html                    # SMTP 配置页面
└── emails/                        # 邮件内容模板
    ├── base_email.html            # 邮件基础模板
    ├── verification_code.html     # 验证码邮件模板
    └── notification.html          # 通知邮件模板
```

### 2.2 模块依赖

```
┌─────────────────────────────────────────────────────────────┐
│                      业务模块（调用方）                        │
│         customer / customer_cn / auth / ...                  │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    EmailService（对外接口）                    │
│              send_email() / send_template_email()            │
└─────────────────────────┬───────────────────────────────────┘
                          │
          ┌───────────────┴───────────────┐
          ▼                               ▼
┌─────────────────────┐       ┌─────────────────────────┐
│   SmtpService       │       │   TemplateService       │
│  （配置管理）         │       │  （模板渲染）            │
└──────────┬──────────┘       └─────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────┐
│              django.core.mail（Django 内置邮件模块）           │
│                  SMTP 后端，直接连接邮件服务器                  │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    django-q2（异步队列）                       │
│                 任务调度 / 重试 / 失败处理                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. 数据设计

### 3.1 SMTP 配置存储

使用现有 `SystemSetting` 表存储配置，添加以下配置项：

| 配置 Key | 类型 | 默认值 | 说明 |
|----------|------|--------|------|
| `smtp_provider` | string | `gmail_tls` | 邮件服务商预设（gmail_ssl/gmail_tls/163_ssl/163_tls/proton_ssl/proton_tls/custom） |
| `smtp_host` | string | `smtp.gmail.com` | SMTP 服务器地址（由预设自动填充） |
| `smtp_port` | int | `587` | SMTP 端口（由预设自动填充） |
| `smtp_use_ssl` | bool | `false` | 是否使用 SSL |
| `smtp_use_tls` | bool | `true` | 是否使用 TLS |
| `smtp_username` | string | `` | SMTP 用户名（邮箱地址） |
| `smtp_password` | string | `` | SMTP 密码/应用专用密码（优先读取环境变量 `SMTP_PASSWORD`，否则从 SystemSetting 读取） |
| `smtp_from_email` | string | `` | 发件人邮箱 |
| `smtp_from_name` | string | 系统名称 | 发件人显示名称 |
| `smtp_timeout` | int | `30` | 连接超时时间（秒） |
| `smtp_enabled` | bool | `false` | 是否启用邮件服务 |

### 3.2 邮件模板表（新建模型）

```python
class EmailTemplate(models.Model):
    """邮件模板"""
    name = models.CharField(max_length=64, unique=True)           # 模板标识名
    subject = models.CharField(max_length=255)                    # 邮件主题模板
    html_body = models.TextField()                                # HTML 正文模板
    text_body = models.TextField(blank=True)                      # 纯文本正文模板
    description = models.CharField(max_length=255, blank=True)    # 模板说明
    is_active = models.BooleanField(default=True)                 # 是否启用
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### 3.3 邮件发送记录表（新建模型）

```python
class EmailLog(models.Model):
    """邮件发送记录"""
    STATUS_CHOICES = [
        ('pending', '待发送'),
        ('sending', '发送中'),
        ('sent', '已发送'),
        ('failed', '发送失败'),
    ]
    
    from_email = models.EmailField()                              # 发件人邮箱
    to_email = models.EmailField()                                # 收件人
    subject = models.CharField(max_length=255)                    # 邮件主题
    text_body = models.TextField(blank=True)                      # 纯文本正文
    html_body = models.TextField(blank=True)                      # HTML 正文
    template_name = models.CharField(max_length=64, blank=True)   # 使用的模板
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True)                  # 错误信息
    retry_count = models.IntegerField(default=0)                  # 重试次数
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)         # 实际发送时间
```

---

## 4. 预置服务商配置

### 4.1 服务商预设

采用扁平化预设结构，每个"服务商+加密方式"组合为独立预设项，用户一次选择即可完成服务器/端口/加密方式的全部配置。

```python
SMTP_PRESETS = {
    'gmail_ssl': {
        'name': 'Gmail (SSL)',
        'host': 'smtp.gmail.com',
        'port': 465,
        'use_ssl': True,
        'use_tls': False,
        'help_text': '需要开启两步验证并生成应用专用密码',
        'help_url': 'https://support.google.com/accounts/answer/185833',
    },
    'gmail_tls': {
        'name': 'Gmail (TLS)',
        'host': 'smtp.gmail.com',
        'port': 587,
        'use_ssl': False,
        'use_tls': True,
        'help_text': '需要开启两步验证并生成应用专用密码',
        'help_url': 'https://support.google.com/accounts/answer/185833',
    },
    '163_ssl': {
        'name': '163邮箱 (SSL)',
        'host': 'smtp.163.com',
        'port': 465,
        'use_ssl': True,
        'use_tls': False,
        'help_text': '需要在邮箱设置中开启SMTP服务并获取授权码',
        'help_url': None,
    },
    '163_tls': {
        'name': '163邮箱 (TLS)',
        'host': 'smtp.163.com',
        'port': 587,
        'use_ssl': False,
        'use_tls': True,
        'help_text': '需要在邮箱设置中开启SMTP服务并获取授权码',
        'help_url': None,
    },
    'proton_ssl': {
        'name': 'ProtonMail (SSL)',
        'host': 'smtp.protonmail.com',
        'port': 465,
        'use_ssl': True,
        'use_tls': False,
        'help_text': '需要ProtonMail Bridge本地代理',
        'help_url': 'https://proton.me/mail/bridge',
    },
    'proton_tls': {
        'name': 'ProtonMail (TLS)',
        'host': 'smtp.protonmail.com',
        'port': 587,
        'use_ssl': False,
        'use_tls': True,
        'help_text': '需要ProtonMail Bridge本地代理',
        'help_url': 'https://proton.me/mail/bridge',
    },
    'custom': {
        'name': '自定义',
        'host': '',
        'port': 587,
        'use_ssl': False,
        'use_tls': True,
        'help_text': '手动填写SMTP服务器信息',
        'help_url': None,
    },
}
```

**预设配置总览：**

| 预设 Key | 服务商 | 加密方式 | 服务器 | 端口 |
|----------|--------|----------|--------|------|
| `gmail_ssl` | Gmail | SSL | smtp.gmail.com | 465 |
| `gmail_tls` | Gmail | TLS | smtp.gmail.com | 587 |
| `163_ssl` | 163邮箱 | SSL | smtp.163.com | 465 |
| `163_tls` | 163邮箱 | TLS | smtp.163.com | 587 |
| `proton_ssl` | ProtonMail | SSL | smtp.protonmail.com | 465 |
| `proton_tls` | ProtonMail | TLS | smtp.protonmail.com | 587 |
| `custom` | 自定义 | 可配置 | 手动填写 | 默认587 |

### 4.2 配置界面行为

1. **选择服务商预设**（下拉框）→ 自动填充服务器地址、端口、加密方式（一次选择全部完成）
2. **用户填写**：邮箱地址、密码/授权码、发件人名称
3. **测试发送**：提供"发送测试邮件"按钮验证配置

**界面示例：**
```
服务商选择: [ Gmail (TLS)   ▼ ]    ← 下拉选择，共7个选项（6预设+1自定义）
SMTP 服务器:  [smtp.gmail.com    ]    ← 自动填充，可手动修改
端口:         [587               ]    ← 自动填充，可手动修改
加密方式:     [☐ SSL] [✓ TLS]         ← 自动勾选，可手动切换
```

---

## 5. 服务层设计

### 5.1 SmtpService（配置管理）

```python
class SmtpService:
    """SMTP 配置管理服务"""
    
    @classmethod
    def get_provider_presets(cls, provider: str) -> dict:
        """获取服务商预设配置"""
        
    @classmethod
    def get_current_config(cls) -> dict:
        """获取当前 SMTP 配置"""
        
    @classmethod
    def save_config(cls, config: dict) -> None:
        """保存 SMTP 配置"""
        
    @classmethod
    def test_connection(cls, config: dict = None) -> tuple[bool, str]:
        """测试 SMTP 连接"""
        
    @classmethod
    def update_django_settings(cls) -> None:
        """更新 Django 邮件配置（运行时）"""
```

### 5.2 EmailService（邮件发送）

```python
class EmailService:
    """邮件发送服务"""
    
    @classmethod
    def send_email(
        cls,
        to: str | list[str],
        subject: str,
        body: str,
        html_body: str = None,
        from_email: str = None,
        async_send: bool = True,
    ) -> bool | str:
        """
        发送邮件
        
        返回：同步返回 bool，异步返回 task_id
        """
        
    @classmethod
    def send_template_email(
        cls,
        to: str | list[str],
        template_name: str,
        context: dict,
        async_send: bool = True,
    ) -> bool | str:
        """
        使用模板发送邮件
        
        参数：
            template_name: 模板名称
            context: 模板上下文变量
        """
        
    @classmethod
    def get_send_history(
        cls,
        to_email: str = None,
        status: str = None,
        limit: int = 50,
    ) -> list:
        """获取发送历史"""
```

### 5.3 TemplateService（模板管理）

```python
class TemplateService:
    """邮件模板服务"""
    
    @classmethod
    def get_template(cls, name: str) -> EmailTemplate | None:
        """获取模板"""
        
    @classmethod
    def render_subject(cls, template: EmailTemplate, context: dict) -> str:
        """渲染邮件主题"""
        
    @classmethod
    def render_body(cls, template: EmailTemplate, context: dict) -> tuple[str, str]:
        """渲染邮件正文，返回 (html, text)"""
        
    @classmethod
    def list_templates(cls) -> list:
        """列出所有模板"""
```

---

## 6. 异步任务设计

### 6.1 使用 django-q2

django-q2 支持多种 Broker，项目使用 ORM Broker（数据库），无需额外安装 Redis。

```python
# tasks.py
from django.core.mail import send_mail, send_html_mail
from django.utils import timezone
from django_q.tasks import async_task
from core.smtp.models import EmailLog

def send_email_task(log_id: int):
    """
    异步发送邮件任务
    
    说明：
        从 EmailLog 读取邮件内容并发送，发送后更新记录状态。
        由 EmailService.send_email() 调用 async_task() 触发。
    """
    try:
        log = EmailLog.objects.get(id=log_id)
        log.status = 'sending'
        log.save(update_fields=['status'])
        
        # 使用 Django 内置邮件模块发送
        if log.html_body:
            from django.core.mail import EmailMultiAlternatives
            msg = EmailMultiAlternatives(
                subject=log.subject,
                body=log.text_body or '',
                from_email=log.from_email,
                to=[log.to_email],
            )
            msg.attach_alternative(log.html_body, "text/html")
            msg.send()
        else:
            send_mail(
                subject=log.subject,
                message=log.text_body or '',
                from_email=log.from_email,
                recipient_list=[log.to_email],
                fail_silently=False,
            )
        
        log.status = 'sent'
        log.sent_at = timezone.now()
        log.save(update_fields=['status', 'sent_at'])
        
    except Exception as e:
        EmailLog.objects.filter(id=log_id).update(
            status='failed',
            error_message=str(e),
        )
```

### 6.2 重试策略

- 最大重试次数：3 次
- 重试间隔：指数退避（30s, 60s, 120s）
- 超过重试次数标记为失败，记录错误信息

---

## 7. 界面设计

### 7.1 frame_admin 导航入口

在 `frame_admin.html` 左侧导航栏添加：

```html
<li class="nav-item">
  <a class="nav-link d-flex align-items-center py-2 px-2 rounded {% if active_section == 'smtp' %}active{% endif %}" 
     href="{{ url('core:smtp_config') }}">
    <i class="bi bi-envelope me-2 fs-6"></i>
    SMTP 配置
  </a>
</li>
```

### 7.2 配置页面布局

```
┌─────────────────────────────────────────────────────────────┐
│  SMTP 配置                                    [保存] [测试]  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 服务商选择（下拉框，一次选择完成全部配置）            │   │
│  │ [ Gmail (TLS)                                     ▼] │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 服务器配置（自动填充，可手动修改）                    │   │
│  │                                                     │   │
│  │ SMTP 服务器:  [smtp.gmail.com________]              │   │
│  │ 端口:         [587____]                             │   │
│  │ 加密方式:     [☐ SSL] [✓ TLS]                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 账户信息                                            │   │
│  │                                                     │   │
│  │ 邮箱地址:     [user@gmail.com____________]          │   │
│  │ 密码/授权码:  [********************************]    │   │
│  │ 发件人名称:   [仙芙CIMF__________________]          │   │
│  │                                                     │   │
│  │ ℹ️ Gmail 需要开启两步验证并生成应用专用密码          │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 启用邮件服务                                        │   │
│  │ [██████████████░░░░░░░░░░░░░░] 已启用               │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 最近发送记录                                        │   │
│  │ ┌────────┬──────────────┬────────┬────────────────┐ │   │
│  │ │ 时间   │ 收件人       │ 主题   │ 状态           │ │   │
│  │ ├────────┼──────────────┼────────┼────────────────┤ │   │
│  │ │ 12:30  │ user@xx.com  │ 验证码 │ ✓ 已发送       │ │   │
│  │ │ 12:28  │ admin@xx.com │ 通知   │ ✗ 失败         │ │   │
│  │ └────────┴──────────────┴────────┴────────────────┘ │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 8. URL 路由

```python
# core/urls.py
urlpatterns = [
    # ... 现有路由 ...
    path('system/smtp/', smtp_views.smtp_config, name='smtp_config'),
    path('system/smtp/test/', smtp_views.smtp_test, name='smtp_test'),
    path('system/smtp/templates/', smtp_views.email_templates, name='email_templates'),
    path('system/smtp/history/', smtp_views.send_history, name='send_history'),
]
```

---

## 9. 接口设计

### 9.1 供其他模块调用的接口

```python
# core.smtp.services.email_service
from core.smtp.services import EmailService

# 简单邮件
EmailService.send_email(
    to='user@example.com',
    subject='测试邮件',
    body='这是一封测试邮件',
)

# 模板邮件
EmailService.send_template_email(
    to='user@example.com',
    template_name='verification_code',
    context={
        'code': '123456',
        'expire_minutes': 10,
        'system_name': '仙芙CIMF',
    },
)
```

### 9.2 API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/system/smtp/` | GET | 配置页面 |
| `/system/smtp/` | POST | 保存配置 |
| `/system/smtp/test/` | POST | 测试连接/发送测试邮件 |
| `/system/smtp/presets/` | GET | 获取服务商预设（AJAX） |
| `/system/smtp/templates/` | GET | 模板列表页面 |
| `/system/smtp/history/` | GET | 发送历史页面 |

---

## 10. 实现步骤

### 阶段一：基础框架（1天）
1. 创建 `core/smtp/` 目录结构
2. 添加 `EmailTemplate` 和 `EmailLog` 模型
3. 创建数据库迁移
4. 在 `SettingsService.DEFAULT_SETTINGS` 添加 SMTP 配置项

### 阶段二：服务层（1天）
1. 实现 `SmtpService` 配置管理
2. 实现 `TemplateService` 模板渲染
3. 实现 `EmailService` 邮件发送

### 阶段三：异步集成（0.5天）
1. 添加 `django-q2` 依赖
2. 实现异步发送任务
3. 配置重试策略

### 阶段四：管理界面（1天）
1. 创建配置表单 `forms.py`
2. 实现视图函数 `views.py`
3. 创建配置页面模板 `config.html`
4. 更新 `frame_admin.html` 导航

### 阶段五：模板系统（0.5天）
1. 创建基础邮件模板
2. 创建验证码邮件模板
3. 创建通知邮件模板

### 阶段六：测试与文档（0.5天）
1. 编写单元测试
2. 更新开发规范文档
3. 更新进度记录

---

## 11. 依赖更新

### requirements.txt 新增

```
# 异步任务队列
django-q2>=1.7,<2.0
```

### settings.py 新增

```python
# 邮件配置（由 SmtpService 运行时动态更新）
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
DEFAULT_FROM_EMAIL = ''

# Django-Q2 配置
Q_CLUSTER = {
    'name': 'cimf',
    'workers': 2,
    'recycle': 500,
    'timeout': 300,
    'retry': 360,
    'orm': 'default',  # 使用默认数据库作为 Broker
}
```

---

## 12. 安全考虑

1. **密码存储**：优先读取环境变量 `SMTP_PASSWORD`，若不存在则从 `SystemSetting` 表读取（混合方式）
2. **权限控制**：SMTP 配置页面仅系统管理员可访问
3. **频率限制**：防止邮件滥用，设置每分钟/每小时发送上限
4. **日志脱敏**：邮件日志不记录密码等敏感信息
5. **输入验证**：邮箱地址格式验证，防止注入攻击

---

## 13. 扩展性

未来可扩展功能：
- 邮件模板可视化编辑器
- 发送统计报表
- 多发件人轮询（负载均衡）
- 邮件追踪（打开率、点击率）
- 附件支持
- 批量邮件发送（邮件列表）

---

## 14. 风险与对策

| 风险 | 影响 | 对策 |
|------|------|------|
| SMTP 服务商限制 | 发送失败 | 支持多服务商切换，失败自动重试 |
| 异步任务丢失 | 邮件未发送 | 使用持久化队列（数据库），支持手动重发 |
| 配置错误 | 无法发送 | 提供测试功能，配置前验证 |
| 密码泄露 | 账户被盗 | 加密存储，日志脱敏 |

---

## 15. 总结

本方案为 CIMF 系统提供完整的邮件发送能力，采用模块化设计，与现有架构无缝集成。通过预置服务商配置降低使用门槛，通过异步任务提高系统响应性能，通过模板系统支持多样化邮件需求。

预计开发周期：**4-5 天**
