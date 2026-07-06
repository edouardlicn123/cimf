"""
客户样本数据初始化服务
"""


class SampleDataService:
    """客户样本数据初始化服务"""

    @staticmethod
    def init_sample_customers() -> dict[str, int]:
        """初始化客户样本数据"""
        from django.db import transaction  # noqa: PLC0415

        from modules.customer_cn.models import CustomerCnFields  # noqa: PLC0415
        from modules.customer_cn.sample_data import DOMESTIC_CUSTOMERS  # noqa: PLC0415

        from core.models import User  # noqa: PLC0415
        from core.node.models import Node, NodeType  # noqa: PLC0415
        from modules.customer.models import CustomerFields  # noqa: PLC0415
        from modules.customer.sample_data import OVERSEAS_CUSTOMERS  # noqa: PLC0415

        results = {"overseas": 0, "domestic": 0}

        admin_user = User.objects.filter(is_admin=True).first()

        customer_node_type = NodeType.objects.filter(slug="customer").first()
        customer_cn_node_type = NodeType.objects.filter(slug="customer_cn").first()

        if not admin_user:
            return results

        with transaction.atomic():
            if customer_node_type:
                for data in OVERSEAS_CUSTOMERS:
                    if CustomerFields.objects.filter(customer_name=data["customer_name"]).exists():
                        continue

                    node = Node.objects.create(
                        node_type=customer_node_type,
                        created_by=admin_user,
                        updated_by=admin_user,
                    )

                    fields_data = {
                        k: v
                        for k, v in data.items()
                        if k
                        not in ("customer_name", "customer_type_id", "country_id", "enterprise_type_id", "customer_level_id")
                    }
                    CustomerFields.objects.create(
                        node=node,
                        customer_name=data["customer_name"],
                        **fields_data,
                    )
                    results["overseas"] += 1

            if customer_cn_node_type:
                for data in DOMESTIC_CUSTOMERS:
                    if CustomerCnFields.objects.filter(customer_name=data["customer_name"]).exists():
                        continue

                    node = Node.objects.create(
                        node_type=customer_cn_node_type,
                        created_by=admin_user,
                        updated_by=admin_user,
                    )

                    fields_data = {
                        k: v
                        for k, v in data.items()
                        if k not in ("customer_name", "customer_type_id", "enterprise_type_id", "customer_level_id")
                    }
                    CustomerCnFields.objects.create(
                        node=node,
                        customer_name=data["customer_name"],
                        **fields_data,
                    )
                    results["domestic"] += 1

        return results
