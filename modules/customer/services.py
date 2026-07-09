"""
================================================================================
文件：services.py
路径：/home/edo/cimf-v2/modules/customer/services.py
================================================================================

功能说明：
    海外客户管理服务，提供客户的 CRUD 操作

    主要功能：
    - 获取客户列表
    - 创建/更新/删除客户
    - 获取客户详情

用法：
    1. 获取客户列表：
        customers = CustomerService.get_list(search='keyword')

    2. 创建客户：
        customer = CustomerService.create(user=request.user, data={})

版本：
    - 1.0: 从 Flask 迁移
    - 1.1: 移动到 modules/customer/ 目录

依赖：
    - modules.models.CustomerFields: 客户字段模型
    - core.node.services: NodeService
    - core.services: PermissionService
"""

from datetime import timedelta
from typing import Any

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from core.node.models import Node, NodeType
from core.node.services import NodeService
from core.services import PermissionService

from .models import CustomerFields
from .sample_data import OVERSEAS_CUSTOMERS

User = get_user_model()


class CustomerService:
    """海外客户管理服务"""

    @staticmethod
    def get_list(
        search: str | None = None, customer_type_id: int | None = None, customer_level_id: int | None = None, user=None
    ) -> list[CustomerFields]:
        """获取客户列表

        Args:
            search: 搜索关键词
            customer_type_id: 客户类型ID
            customer_level_id: 客户等级ID
            user: 当前用户，为None时返回所有客户
        """
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
        """根据 ID 获取客户"""
        return CustomerFields.objects.filter(id=customer_id).first()

    @staticmethod
    def get_by_node_id(node_id: int) -> CustomerFields | None:
        """根据节点 ID 获取客户"""
        return CustomerFields.objects.filter(node_id=node_id).first()

    @staticmethod
    def _generate_unique_code() -> str:
        """生成不重复的客户编码（cc + 8位序号，与现有数据格式一致）"""
        max_code = (
            CustomerFields.objects.filter(customer_code__startswith="cc")
            .order_by("customer_code")
            .last()
        )
        next_num = int(max_code.customer_code[2:]) + 1 if max_code else 1
        return f"cc{next_num:08d}"

    @staticmethod
    def create(user, data: dict[str, Any]) -> CustomerFields:
        """创建客户"""
        from django.db import transaction  # noqa: PLC0415

        with transaction.atomic():
            node = NodeService.create_node("customer", {}, user)
            if not node:
                raise ValueError("创建节点失败")

            customer_code = data.get("customer_code")
            if not customer_code:
                customer_code = CustomerService._generate_unique_code()

            customer = CustomerFields.objects.create(
                node=node,
                customer_name=data.get("customer_name", ""),
                customer_code=customer_code,
                customer_type_id=data.get("customer_type_id"),
                enterprise_name=data.get("enterprise_name"),
                phone1=data.get("phone1"),
                email1=data.get("email1"),
                phone2=data.get("phone2"),
                email2=data.get("email2"),
                linkedin=data.get("linkedin"),
                country_id=data.get("country_id"),
                province=data.get("province"),
                address=data.get("address"),
                postal_code=data.get("postal_code"),
                industry=data.get("industry"),
                enterprise_type_id=data.get("enterprise_type_id"),
                registered_capital=data.get("registered_capital"),
                customer_level_id=data.get("customer_level_id"),
                credit_limit=data.get("credit_limit"),
                website=data.get("website"),
                notes=data.get("notes"),
            )

        return customer

    @staticmethod
    def import_row(data: dict, user) -> CustomerFields:
        """导入一行客户数据，含 customer_code 自动生成"""
        customer_code = data.get("customer_code")
        if not customer_code:
            customer_code = CustomerService._generate_unique_code()

        node = Node.objects.create(
            node_type=NodeType.objects.get(slug="customer"),
            created_by=user,
            updated_by=user,
        )
        return CustomerFields.objects.create(
            node=node,
            customer_code=customer_code,
        )

    @staticmethod
    def update(customer_id: int, _user, data: dict[str, Any]) -> CustomerFields | None:
        """更新客户"""
        from django.db import transaction  # noqa: PLC0415

        with transaction.atomic():
            customer = CustomerFields.objects.filter(id=customer_id).first()
            if not customer:
                return None

            if not customer.node_id:
                raise ValueError("客户关联节点不存在")
            NodeService.update_node(customer.node_id, {})

            allowed_fields = {
                "customer_name",
                "customer_code",
                "customer_type_id",
                "enterprise_name",
                "phone1",
                "email1",
                "phone2",
                "email2",
                "linkedin",
                "country_id",
                "province",
                "address",
                "postal_code",
                "industry",
                "enterprise_type_id",
                "registered_capital",
                "customer_level_id",
                "credit_limit",
                "website",
                "notes",
            }
            for key, value in data.items():
                if key in allowed_fields:
                    setattr(customer, key, value)

            customer.save()
            return customer

    @staticmethod
    def delete(customer_id: int) -> bool:
        """删除客户"""
        from django.db import transaction  # noqa: PLC0415

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
        """获取可导出的字段列表"""
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
        """获取客户总数"""
        return CustomerFields.objects.count()

    @staticmethod
    def get_recent_count(days: int = 7) -> int:
        """获取最近N天新增的客户数量"""
        start_date = timezone.now() - timedelta(days=days)
        return CustomerFields.objects.filter(created_at__gte=start_date).count()

    @staticmethod
    def init_sample_data() -> int:
        """初始化样本数据"""
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
