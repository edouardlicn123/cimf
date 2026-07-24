"""
回填客户 customer_code

扫描 CustomerFields 表中 customer_code 为空或 NULL 的记录，
使用动态导入获取模型为其补全顺序编码。

用法:
    ./venv/bin/python manage.py backfill_customer_codes          # 执行更新
    ./venv/bin/python manage.py backfill_customer_codes --dry-run  # 仅预览
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Max, Q

from core.module.services.module_registry_service import ModuleRegistryService


class Command(BaseCommand):
    help = "为导入的客户记录补全 customer_code"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="仅预览要更新的记录数，不实际执行",
        )

    def handle(self, **options):
        customer_models = ModuleRegistryService.safe_import_module_sub("customer", "models")
        if not customer_models:
            self.stderr.write(self.style.ERROR("客户模块未安装，请先安装 customer 模块"))
            return

        CustomerFields = getattr(customer_models, "CustomerFields", None)
        if not CustomerFields:
            self.stderr.write(self.style.ERROR("未找到 CustomerFields 模型"))
            return

        dry_run = options.get("dry_run", False)

        records = CustomerFields.objects.filter(Q(customer_code__isnull=True) | Q(customer_code=""))

        if dry_run:
            self.stdout.write(f"将更新 {records.count()} 条记录")
            return

        base = CustomerFields.objects.filter(
            customer_code__startswith="cc"
        ).aggregate(max_code=Max("customer_code"))["max_code"]
        next_num = (int(base[2:]) + 1) if base and base[2:].isdigit() else 1
        updated = 0
        with transaction.atomic():
            for customer in records:
                code = f"cc{next_num:08d}"
                customer.customer_code = code
                customer.save(update_fields=["customer_code"])
                next_num += 1
                updated += 1

        self.stdout.write(self.style.SUCCESS(f"已更新 {updated} 条记录"))
