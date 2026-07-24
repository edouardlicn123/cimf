"""
邮件模板服务
"""

import logging

from jinja2 import Environment, UndefinedError

from core.smtp.models import EmailTemplate
from core.smtp.services.default_templates import DEFAULT_TEMPLATES

logger = logging.getLogger(__name__)

_email_env = Environment(autoescape=True)


class TemplateService:
    """邮件模板服务"""

    @classmethod
    def get_template(cls, name: str) -> EmailTemplate | None:
        """获取模板"""
        return EmailTemplate.objects.filter(name=name, is_active=True).first()

    @classmethod
    def _render_safe(cls, template_text: str, context: dict) -> str:
        """安全渲染模板，出错时返回空字符串"""
        try:
            return _email_env.from_string(template_text).render(**context)
        except UndefinedError as e:
            logger.error(f"邮件模板渲染错误: {e}")
            return ""

    @classmethod
    def render_subject(cls, template: EmailTemplate, context: dict) -> str:
        """渲染邮件主题"""
        return cls._render_safe(template.subject, context)

    @classmethod
    def render_body(cls, template: EmailTemplate, context: dict) -> tuple[str, str]:
        """渲染邮件正文，返回 (html, text)"""
        html_body = cls._render_safe(template.html_body, context)
        text_body = cls._render_safe(template.text_body, context)
        return html_body, text_body

    @classmethod
    def list_templates(cls) -> list[EmailTemplate]:
        """列出所有模板"""
        return list(EmailTemplate.objects.filter(is_active=True).order_by("-created_at"))

    @classmethod
    def create_template(
        cls,
        name: str,
        subject: str,
        html_body: str,
        text_body: str = "",
        description: str = "",
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
        subject: str | None = None,
        html_body: str | None = None,
        text_body: str | None = None,
        description: str | None = None,
        is_active: bool | None = None,
    ) -> EmailTemplate:
        """更新模板"""
        changed_fields = []
        if subject is not None:
            template.subject = subject
            changed_fields.append("subject")
        if html_body is not None:
            template.html_body = html_body
            changed_fields.append("html_body")
        if text_body is not None:
            template.text_body = text_body
            changed_fields.append("text_body")
        if description is not None:
            template.description = description
            changed_fields.append("description")
        if is_active is not None:
            template.is_active = is_active
            changed_fields.append("is_active")
        if changed_fields:
            template.save(update_fields=changed_fields)
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
        existing_names = set(EmailTemplate.objects.values_list("name", flat=True))

        templates_to_create = []
        for type_key, tmpl in DEFAULT_TEMPLATES.items():
            if type_key not in existing_names:
                templates_to_create.append(
                    EmailTemplate(
                        name=type_key,
                        subject=tmpl["subject"],
                        description=tmpl["description"],
                        html_body=tmpl["html_body"],
                        text_body=tmpl.get("text_body", ""),
                        is_active=True,
                    )
                )
                existing_names.add(type_key)

        if templates_to_create:
            EmailTemplate.objects.bulk_create(templates_to_create, batch_size=10)

        return len(templates_to_create)
