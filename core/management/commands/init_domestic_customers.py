# -*- coding: utf-8 -*-
"""
国内客户样本数据初始化命令
用法: ./venv/bin/python manage.py init_domestic_customers
"""

from importlib import import_module

from django.core.management.base import BaseCommand
from django.db import transaction

from core.node.models import Node, NodeType
from core.models import User


class Command(BaseCommand):
    help = '初始化国内客户样本数据'

    def handle(self, *args, **options):
        try:
            customer_cn_module = import_module('modules.customer_cn.module')
            customer_cn_models = import_module('modules.customer_cn.models')
            customer_cn_sample_data = import_module('modules.customer_cn.sample_data')
        except (ImportError, ModuleNotFoundError) as e:
            self.stderr.write(self.style.ERROR(f'模块导入失败: {e}'))
            return
        
        CustomerCnFields = getattr(customer_cn_models, 'CustomerCnFields', None)
        DOMESTIC_CUSTOMERS = getattr(customer_cn_sample_data, 'DOMESTIC_CUSTOMERS', None)
        
        if not CustomerCnFields:
            self.stderr.write(self.style.ERROR('未找到 CustomerCnFields 模型'))
            return
        
        if not DOMESTIC_CUSTOMERS:
            self.stderr.write(self.style.ERROR('未找到 DOMESTIC_CUSTOMERS 样本数据'))
            return
        
        admin_user = User.objects.filter(is_admin=True).first()
        if not admin_user:
            self.stderr.write(self.style.ERROR('未找到管理员用户，请先创建用户'))
            return
        
        module_info = getattr(customer_cn_module, 'MODULE_INFO', {})
        module_id = module_info.get('id', 'customer_cn')
        
        customer_cn_node_type = NodeType.objects.filter(slug=module_id).first()
        if not customer_cn_node_type:
            self.stderr.write(self.style.ERROR(f'未找到节点类型 ({module_id})，请先运行 init_node_types'))
            return
        
        existing_names = set(CustomerCnFields.objects.values_list('customer_name', flat=True))
        
        nodes_to_create = []
        fields_to_create = []
        
        for data in DOMESTIC_CUSTOMERS:
            customer_name = data.get('customer_name')
            if not customer_name or customer_name in existing_names:
                continue
            
            nodes_to_create.append(Node(
                node_type=customer_cn_node_type,
                created_by=admin_user,
                updated_by=admin_user,
            ))
            
            fields_data = {k: v for k, v in data.items() if k != 'customer_name'}
            fields_to_create.append({
                'customer_name': customer_name,
                'fields_data': fields_data,
            })
        
        if not nodes_to_create:
            self.stdout.write(self.style.WARNING('没有需要创建的客户数据'))
            return
        
        with transaction.atomic():
            Node.objects.bulk_create(nodes_to_create)
            
            created_nodes = Node.objects.filter(
                node_type=customer_cn_node_type,
                created_by=admin_user,
            ).order_by('-id')[:len(nodes_to_create)]
            node_ids = [n.id for n in reversed(list(created_nodes))]
            
            customer_fields_objs = []
            for i, fields_info in enumerate(fields_to_create):
                customer_fields_objs.append(CustomerCnFields(
                    node_id=node_ids[i],
                    customer_name=fields_info['customer_name'],
                    **fields_info['fields_data'],
                ))
            
            CustomerCnFields.objects.bulk_create(customer_fields_objs)
        
        self.stdout.write(self.style.SUCCESS(f"完成! 新增 {len(nodes_to_create)} 条国内客户"))
