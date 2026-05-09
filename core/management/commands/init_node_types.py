# -*- coding: utf-8 -*-
"""
初始化节点类型数据
用法: ./venv/bin/python manage.py init_node_types
"""

from django.core.management.base import BaseCommand

from core.node.models import NodeType
from core.node.services import NodeTypeService


class Command(BaseCommand):
    help = '初始化节点类型数据（从模块配置动态读取）'

    def handle(self, *args, **options):
        # 从模块配置中动态获取节点类型定义
        node_types = NodeTypeService.get_node_types_from_modules()
        
        if not node_types:
            self.stdout.write(self.style.WARNING("未找到任何模块配置的节点类型"))
            return

        count = 0
        for data in node_types:
            slug = data.get('slug')
            name = data.get('name', slug)
            
            if not slug:
                self.stdout.write(self.style.WARNING(f"跳过无效配置: {data}"))
                continue
            
            if NodeType.objects.filter(slug=slug).exists():
                self.stdout.write(f"跳过已存在: {name}")
                continue

            NodeType.objects.create(
                name=name,
                slug=slug,
                icon=data.get('icon', 'bi-folder'),
                description=data.get('description', ''),
                is_active=True,
            )
            count += 1
            self.stdout.write(f"创建: {name}")

        self.stdout.write(self.style.SUCCESS(f"完成! 新增 {count} 个节点类型"))
