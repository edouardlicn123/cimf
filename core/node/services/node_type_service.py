import os
from typing import List, Optional, Dict, Any
from core.node.models import NodeType, Node


class NodeTypeService:
    
    @staticmethod
    def get_all() -> List[NodeType]:
        return NodeType.objects.filter(is_active=True)
    
    @staticmethod
    def get_all_including_inactive() -> List[NodeType]:
        return NodeType.objects.all()
    
    @staticmethod
    def get_by_id(node_type_id: int) -> Optional[NodeType]:
        return NodeType.objects.filter(id=node_type_id).first()  # 调用者需检查 None
    
    @staticmethod
    def get_by_id_or_404(node_type_id: int) -> NodeType:
        """获取节点类型，不存在则抛出异常"""
        node_type = NodeType.objects.filter(id=node_type_id).first()
        if not node_type:
            raise ValueError(f'节点类型不存在: {node_type_id}')
        return node_type
    
    @staticmethod
    def get_by_slug(slug: str) -> Optional[NodeType]:
        return NodeType.objects.filter(slug=slug, is_active=True).first()  # 调用者需检查 None
    
    @staticmethod
    def get_by_slug_or_404(slug: str) -> NodeType:
        """获取节点类型，不存在则抛出异常"""
        node_type = NodeType.objects.filter(slug=slug, is_active=True).first()
        if not node_type:
            raise ValueError(f'节点类型不存在: {slug}')
        return node_type
    
    @staticmethod
    def get_by_slug_including_inactive(slug: str) -> Optional[NodeType]:
        return NodeType.objects.filter(slug=slug).first()  # 调用者需检查 None
    
    @staticmethod
    def get_by_slug_including_inactive_or_404(slug: str) -> NodeType:
        """获取节点类型（含未激活），不存在则抛出异常"""
        node_type = NodeType.objects.filter(slug=slug).first()
        if not node_type:
            raise ValueError(f'节点类型不存在: {slug}')
        return node_type
    
    @staticmethod
    def create(data: Dict[str, Any]) -> NodeType:
        return NodeType.objects.create(**data)
    
    @staticmethod
    def update(node_type_id: int, data: Dict[str, Any]) -> Optional[NodeType]:
        node_type = NodeType.objects.filter(id=node_type_id).first()
        if node_type:
            for key, value in data.items():
                if hasattr(node_type, key):
                    setattr(node_type, key, value)
            node_type.save()
        return node_type
    
    @staticmethod
    def delete(node_type_id: int) -> bool:
        node_type = NodeType.objects.filter(id=node_type_id).first()
        if node_type:
            node_type.is_active = False
            node_type.save()
            return True
        return False
    
    @staticmethod
    def enable(node_type_id: int) -> bool:
        node_type = NodeType.objects.filter(id=node_type_id).first()
        if node_type:
            node_type.is_active = True
            node_type.save()
            return True
        return False
    
    @staticmethod
    def disable(node_type_id: int) -> bool:
        node_type = NodeType.objects.filter(id=node_type_id).first()
        if node_type:
            node_type.is_active = False
            node_type.save()
            return True
        return False
    
    @staticmethod
    def toggle_active(node_type_id: int) -> bool:
        node_type = NodeType.objects.filter(id=node_type_id).first()
        if node_type:
            node_type.is_active = not node_type.is_active
            node_type.save()
            return node_type.is_active
        return False
    
    @staticmethod
    def get_node_count(node_type_id: int) -> int:
        return Node.objects.filter(node_type_id=node_type_id).count()
    
    @staticmethod
    def get_node_types_from_modules() -> List[Dict[str, Any]]:
        from importlib import import_module
        node_types = []
        modules_dir = 'modules'
        
        if not os.path.exists(modules_dir):
            return node_types
        
        for item in os.listdir(modules_dir):
            item_path = os.path.join(modules_dir, item)
            if not os.path.isdir(item_path):
                continue
            
            module_file = os.path.join(item_path, 'module.py')
            if not os.path.exists(module_file):
                continue
            
            try:
                mod = import_module(f'modules.{item}.module')
                if hasattr(mod, 'MODULE_INFO'):
                    module_info = mod.MODULE_INFO
                    if module_info.get('type') == 'node':
                        node_type_config = module_info.get('node_type', {})
                        if not node_type_config:
                            node_type_config = {
                                'name': module_info.get('name', item),
                                'slug': module_info.get('id', item),
                                'description': module_info.get('description', ''),
                                'icon': module_info.get('icon', 'bi-folder'),
                            }
                        node_types.append(node_type_config)
            except (ImportError, ModuleNotFoundError, AttributeError):
                pass
        
        return node_types
    
    @staticmethod
    def init_default_node_types() -> None:
        node_types_config = NodeTypeService.get_node_types_from_modules()
        for nt_data in node_types_config:
            slug = nt_data.get('slug')
            if not slug:
                continue
            
            existing = NodeType.objects.filter(slug=slug).first()
            if existing:
                continue
            
            NodeType.objects.create(
                name=nt_data.get('name', slug),
                slug=slug,
                description=nt_data.get('description', ''),
                icon=nt_data.get('icon', 'bi-folder'),
                fields_config=nt_data.get('fields_config', []),
                is_active=nt_data.get('is_active', True)
            )