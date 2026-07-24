"""
邮件发送服务 - 发送核心
"""

import logging

from django.core.mail import EmailMultiAlternatives, send_mail

from core.smtp.models import EmailLog
from core.smtp.services.smtp_service import SmtpService, _apply_proxy_patch

logger = logging.getLogger(__name__)


class EmailServiceSenderMixin:

    @staticmethod
    def _resolve_system_url(request=None) -> str:
        system_url = SmtpService.get_system_url()
        if system_url:
            return system_url
        if request:
            host = request.get_host()
            scheme = "https" if request.is_secure() else "http"
            return f"{scheme}://{host}"
        return ""

    @classmethod
    def send_email(
        cls,
        to: str | list[str],
        subject: str,
        body: str,
        html_body: str | None = None,
        from_email: str | None = None,
        async_send: bool = True,
    ) -> bool | int:
        to_list = [to] if isinstance(to, str) else to
        subject = subject.replace("\r", "").replace("\n", "")

        config = SmtpService.get_current_config()

        if not config.get("enabled"):
            return False

        from_email = from_email or config.get("from_email")
        if not from_email:
            from_email = config.get("username", "")

        default_from = f"{config.get('from_name', '仙芙CIMF')} <{from_email}>"

        if async_send:
            log = cls._create_log(
                from_email=from_email,
                to_emails=to_list,
                subject=subject,
                text_body=body,
                html_body=html_body,
            )

            cls._send_async(log.id)
            return log.id
        else:
            return cls._send_sync(
                to_list=to_list,
                subject=subject,
                body=body,
                html_body=html_body,
                default_from=default_from,
            )

    @classmethod
    def _create_log(
        cls,
        from_email: str,
        to_emails: list[str],
        subject: str,
        text_body: str = "",
        html_body: str = "",
        template_name: str = "",
    ) -> EmailLog:
        return EmailLog.objects.create(
            from_email=from_email,
            to_email=",".join(to_emails),
            subject=subject,
            text_body=text_body,
            html_body=html_body or "",
            template_name=template_name,
            status="pending",
        )

    @classmethod
    def _send_async(cls, log_id: int) -> None:
        EmailLog.objects.filter(id=log_id).update(status="pending")

    @classmethod
    def _send_sync(
        cls,
        to_list: list[str],
        subject: str,
        body: str,
        html_body: str,
        default_from: str,
    ) -> bool:
        config = SmtpService.get_current_config()
        try:
            with _apply_proxy_patch(config):
                if html_body:
                    msg = EmailMultiAlternatives(
                        subject=subject,
                        body=body,
                        from_email=default_from,
                        to=to_list,
                    )
                    msg.attach_alternative(html_body, "text/html")
                    msg.send()
                else:
                    send_mail(
                        subject=subject,
                        message=body,
                        from_email=default_from,
                        recipient_list=to_list,
                        fail_silently=False,
                    )
                return True
        except Exception as e:
            logger.error(f"邮件发送失败: to={to_list}, subject={subject}, error={e}", exc_info=True)
            return False
