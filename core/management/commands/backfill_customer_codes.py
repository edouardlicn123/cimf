"""
回填客户 customer_code

扫描 CustomerFields 表中 customer_code 为空或 NULL 的记录，
使用 CustomerService 的编码生成方法为其补全顺序编码。

用法:
    ./venv/bin/python manage.py backfill_customer_codes          # 执行更新
    ./venv/bin/python manage.py backfill_customer_codes --dry-run  # 仅预览
"""

from django.core.management.base import BaseCommand
from django.db.models import Q


class Command(BaseCommand):
    help = "为导入的客户记录补全 customer_code"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="仅预览要更新的记录数，不实际执行",
        )

    def handle(self, *args, **options):
        from modules.customer.models import CustomerFields  # noqa: PLC0415
        from modules.customer.services import CustomerService  # noqa: PLC0415

        dry_run = options.get("dry_run", False)

        records = CustomerFields.objects.filter(
            Q(customer_code__isnull=True) | Q(customer_code="")
        )

        if dry_run:
            self.stdout.write(f"将更新 {records.count()} 条记录")
            return

        updated = 0
        for customer in records:
            code = CustomerService._generate_unique_code()
            customer.customer_code = code
            customer.save(update_fields=["customer_code"])
            updated += 1

        self.stdout.write(self.style.SUCCESS(f"已更新 {updated} 条记录"))
