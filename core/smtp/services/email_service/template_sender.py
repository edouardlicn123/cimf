"""
邮件发送服务 - 模板发送
"""

import logging

from django.utils import timezone

from core.smtp.services.template_service import TemplateService

logger = logging.getLogger(__name__)


class EmailServiceTemplateMixin:

    @classmethod
    def send_template_email(
        cls,
        to: str | list[str],
        template_name: str,
        context: dict,
        async_send: bool = True,
    ) -> bool | int:
        template = TemplateService.get_template(template_name)
        if not template:
            return False

        subject = TemplateService.render_subject(template, context).replace("\r", "").replace("\n", "")
        html_body, text_body = TemplateService.render_body(template, context)

        return cls.send_email(
            to=to,
            subject=subject,
            body=text_body,
            html_body=html_body,
            async_send=async_send,
        )

    @classmethod
    def send_verification_code(
        cls,
        to: str,
        code: str,
        expire_minutes: int = 5,
        request=None,
        async_send: bool = True,
    ) -> bool | int:
        system_url = cls._resolve_system_url(request)
        context = {
            "code": code,
            "expire_minutes": expire_minutes,
            "system_url": system_url,
            "year": timezone.now().year,
        }
        return cls.send_template_email(
            to=to,
            template_name="verification_code",
            context=context,
            async_send=async_send,
        )

    @classmethod
    def send_password_reset(
        cls,
        to: str,
        reset_link: str,
        expire_hours: int = 24,
        request=None,
        async_send: bool = True,
    ) -> bool | int:
        system_url = cls._resolve_system_url(request)
        context = {
            "reset_link": reset_link,
            "expire_hours": expire_hours,
            "system_url": system_url,
            "year": timezone.now().year,
        }
        return cls.send_template_email(
            to=to,
            template_name="password_reset",
            context=context,
            async_send=async_send,
        )

    @classmethod
    def send_notification(
        cls,
        to: str | list[str],
        title: str,
        message: str,
        action_url: str = "",
        action_text: str = "",
        request=None,
        async_send: bool = True,
    ) -> bool | int:
        system_url = cls._resolve_system_url(request)
        context = {
            "title": title,
            "message": message,
            "action_url": action_url,
            "action_text": action_text,
            "system_url": system_url,
            "year": timezone.now().year,
        }
        return cls.send_template_email(
            to=to,
            template_name="notification",
            context=context,
            async_send=async_send,
        )
