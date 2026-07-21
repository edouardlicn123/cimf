import logging
from datetime import timedelta
from typing import Any

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import IntegerField, Q
from django.db.models.functions import Cast, Substr
from django.utils import timezone

from core.node.models import Node, NodeType
from core.node.services import NodeService
from core.services import PermissionService

from .models import CustomerFields
from .sample_data import OVERSEAS_CUSTOMERS

logger = logging.getLogger(__name__)
User = get_user_model()

FIELD_MAPPING = {
    "customer_name": str,
    "customer_code": str,
    "customer_type_id": int,
    "enterprise_name": str,
    "phone1": str,
    "email1": str,
    "phone2": str,
    "email2": str,
    "linkedin": str,
    "country_id": int,
    "province": str,
    "address": str,
    "postal_code": str,
    "industry": str,
    "enterprise_type_id": int,
    "registered_capital": float,
    "customer_level_id": int,
    "credit_limit": float,
    "website": str,
    "notes": str,
}


class CustomerService:
    """海外客户管理服务"""

    @staticmethod
    def get_list(
        search: str | None = None, customer_type_id: int | None = None, customer_level_id: int | None = None, user=None
    ) -> list[CustomerFields]:
        queryset = CustomerFields.objects.select_related(
            "customer_type", "customer_level", "country", "enterprise_type", "node__created_by"
        )

        if user and not user.is_admin and not PermissionService.has_permission(user, "node.customer.view_others"):
            queryset = queryset.filter(node__created_by=user)

        if search:
            queryset = queryset.filter(
                Q(customer_name__icontains=search)
                | Q(enterprise_name__icontains=search)
                | Q(phone1__icontains=search)
                | Q(phone2__icontains=search)
            )

        if customer_type_id:
            queryset = queryset.filter(customer_type_id=customer_type_id)

        if customer_level_id:
            queryset = queryset.filter(customer_level_id=customer_level_id)

        return queryset.order_by("-created_at")

    @staticmethod
    def get_by_id(customer_id: int) -> CustomerFields | None:
        return CustomerFields.objects.filter(id=customer_id).first()

    @staticmethod
    def get_by_node_id(node_id: int) -> CustomerFields | None:
        return CustomerFields.objects.filter(node_id=node_id).first()

    @staticmethod
    def _generate_unique_code() -> str:
        max_code = (
            CustomerFields.objects.filter(customer_code__startswith="cc")
            .annotate(code_num=Cast(Substr("customer_code", 3), IntegerField()))
            .order_by("-code_num")
            .first()
        )
        next_num = (max_code.code_num + 1) if max_code and max_code.code_num is not None else 1
        return f"cc{next_num:08d}"

    @staticmethod
    def _build_fields(data: dict, extra: dict) -> dict:
        fields = dict(extra)
        for field_name, _type in FIELD_MAPPING.items():
            val = data.get(field_name)
            if val is not None and val != "":
                try:
                    fields[field_name] = _type(val) if _type is not str else val
                except (ValueError, TypeError):
                    logger.warning("字段 '%s' 类型转换失败，使用原始值: %r", field_name, val)
                    fields[field_name] = val
        return fields

    @staticmethod
    def create(user, data: dict[str, Any]) -> CustomerFields:
        from django.db import IntegrityError  # noqa: PLC0415

        customer_code = data.get("customer_code")
        max_retries = 3 if not customer_code else 1
        for attempt in range(max_retries):
            try:
                with transaction.atomic():
                    node = NodeService.create_node("customer", {}, user)
                    if not node:
                        raise ValueError("创建节点失败")

                    code = customer_code or CustomerService._generate_unique_code()
                    fields = CustomerService._build_fields(data, {"node": node, "customer_code": code})
                    return CustomerFields.objects.create(**fields)
            except IntegrityError as e:
                if attempt == max_retries - 1:
                    raise ValueError(f"客户代码重复且重试耗尽: {e}")
                logger.warning("客户代码冲突，重试生成唯一代码")
                continue

    @staticmethod
    def import_row(data: dict, user) -> CustomerFields:
        customer_code = data.get("customer_code")
        if not customer_code:
            customer_code = CustomerService._generate_unique_code()

        node_type = NodeType.objects.filter(slug="customer").first()
        if not node_type:
            raise ValueError("客户节点类型不存在，请确保已安装客户模块")
        node = Node.objects.create(
            node_type=node_type,
            created_by=user,
            updated_by=user,
        )
        fields = CustomerService._build_fields(data, {"node": node, "customer_code": customer_code})
        return CustomerFields.objects.create(**fields)

    @staticmethod
    def update(customer_id: int, _user, data: dict[str, Any]) -> CustomerFields | None:
        with transaction.atomic():
            customer = CustomerFields.objects.filter(id=customer_id).first()
            if not customer:
                return None

            if not customer.node_id:
                raise ValueError("客户关联节点不存在")

            for key, value in data.items():
                if key in FIELD_MAPPING:
                    setattr(customer, key, value)

            customer.save()
            return customer

    @staticmethod
    def delete(customer_id: int) -> bool:
        with transaction.atomic():
            customer = CustomerFields.objects.filter(id=customer_id).first()
            if customer:
                node = customer.node
                customer.delete()
                if node:
                    node.delete()
                return True
            return False

    @staticmethod
    def get_exportable_fields() -> list[dict]:
        return [
            {"name": "customer_name", "label": "客户名称", "type": "string", "required": True},
            {"name": "customer_code", "label": "客户代码", "type": "string", "required": True},
            {"name": "customer_type", "label": "客户类型", "type": "fk"},
            {"name": "enterprise_name", "label": "企业名称", "type": "string"},
            {"name": "phone1", "label": "电话1", "type": "telephone"},
            {"name": "email1", "label": "邮箱1", "type": "email"},
            {"name": "phone2", "label": "电话2", "type": "telephone"},
            {"name": "email2", "label": "邮箱2", "type": "email"},
            {"name": "linkedin", "label": "领英", "type": "link"},
            {"name": "country", "label": "国家", "type": "fk"},
            {"name": "province", "label": "省份", "type": "string"},
            {"name": "address", "label": "详细地址", "type": "string"},
            {"name": "postal_code", "label": "邮政编码", "type": "string"},
            {"name": "industry", "label": "行业", "type": "string"},
            {"name": "enterprise_type", "label": "企业类型", "type": "fk"},
            {"name": "registered_capital", "label": "注册资本", "type": "decimal"},
            {"name": "customer_level", "label": "客户等级", "type": "fk"},
            {"name": "credit_limit", "label": "信用额度", "type": "decimal"},
            {"name": "website", "label": "网站", "type": "string"},
            {"name": "notes", "label": "备注", "type": "string"},
        ]

    @staticmethod
    def get_count() -> int:
        return CustomerFields.objects.count()

    @staticmethod
    def get_recent_count(days: int = 7) -> int:
        start_date = timezone.now() - timedelta(days=days)
        return CustomerFields.objects.filter(created_at__gte=start_date).count()

    @staticmethod
    def init_sample_data() -> int:
        admin_user = User.objects.filter(is_admin=True).first()
        if not admin_user:
            return 0

        node_type = NodeType.objects.filter(slug="customer").first()
        if not node_type:
            return 0

        existing_names = set(CustomerFields.objects.values_list("customer_name", flat=True))

        nodes_to_create = []
        fields_to_create = []

        for data in OVERSEAS_CUSTOMERS:
            customer_name = data.get("customer_name")
            if not customer_name or customer_name in existing_names:
                continue

            nodes_to_create.append(
                Node(
                    node_type=node_type,
                    created_by=admin_user,
                    updated_by=admin_user,
                )
            )

            fields_data = {k: v for k, v in data.items() if k != "customer_name"}
            fields_to_create.append(
                {
                    "customer_name": customer_name,
                    "fields_data": fields_data,
                }
            )

        if not nodes_to_create:
            return 0

        with transaction.atomic():
            Node.objects.bulk_create(nodes_to_create)

            created_nodes = Node.objects.filter(
                node_type=node_type,
                created_by=admin_user,
            ).order_by("-id")[: len(nodes_to_create)]
            node_ids = [n.id for n in reversed(list(created_nodes))]

            customer_fields_objs = []
            for i, fields_info in enumerate(fields_to_create):
                customer_fields_objs.append(
                    CustomerFields(
                        node_id=node_ids[i],
                        customer_name=fields_info["customer_name"],
                        **fields_info["fields_data"],
                    )
                )

            CustomerFields.objects.bulk_create(customer_fields_objs)

        return len(nodes_to_create)
