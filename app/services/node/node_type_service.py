# Node Type Service
from app.models.node.node_type import NodeType
from app.models.node.node import Node
from app import db

class NodeTypeService:
    """节点类型服务"""
    
    @staticmethod
    def get_all():
        return NodeType.query.filter_by(is_active=True).all()
    
    @staticmethod
    def get_all_including_inactive():
        return NodeType.query.all()
    
    @staticmethod
    def get_by_id(node_type_id):
        return NodeType.query.get(node_type_id)
    
    @staticmethod
    def get_by_slug(slug):
        return NodeType.query.filter_by(slug=slug, is_active=True).first()
    
    @staticmethod
    def get_by_slug_including_inactive(slug):
        return NodeType.query.filter_by(slug=slug).first()
    
    @staticmethod
    def create(data):
        node_type = NodeType(**data)
        db.session.add(node_type)
        db.session.commit()
        return node_type
    
    @staticmethod
    def update(node_type_id, data):
        node_type = NodeType.query.get(node_type_id)
        for key, value in data.items():
            if hasattr(node_type, key):
                setattr(node_type, key, value)
        db.session.commit()
        return node_type
    
    @staticmethod
    def delete(node_type_id):
        node_type = NodeType.query.get(node_type_id)
        node_type.is_active = False
        db.session.commit()
    
    @staticmethod
    def enable(node_type_id):
        node_type = NodeType.query.get(node_type_id)
        if node_type:
            node_type.is_active = True
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def disable(node_type_id):
        node_type = NodeType.query.get(node_type_id)
        if node_type:
            node_type.is_active = False
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def get_node_count(node_type_id):
        return Node.query.filter_by(node_type_id=node_type_id).count()
    
    @staticmethod
    def init_default_node_types():
        """初始化预置节点类型"""
        default_node_types = [
            {
                'name': '客户信息',
                'slug': 'customer',
                'description': '记录客户基本信息',
                'icon': 'bi-people',
                'fields_config': [
                    {'field_type': 'string', 'name': 'customer_name', 'label': '客户名称', 'required': True, 'unique': True},
                    {'field_type': 'string', 'name': 'contact_person', 'label': '联系人', 'required': False},
                    {'field_type': 'telephone', 'name': 'phone', 'label': '电话', 'required': False},
                    {'field_type': 'email', 'name': 'email', 'label': '邮箱', 'required': False},
                    {'field_type': 'address', 'name': 'address', 'label': '地址', 'required': False},
                    {'field_type': 'entity_reference', 'name': 'customer_type', 'label': '客户类型', 'required': False, 'reference_type': 'taxonomy'},
                    {'field_type': 'string_long', 'name': 'notes', 'label': '备注', 'required': False},
                ],
                'is_active': True,
            },
        ]
        
        for nt_data in default_node_types:
            # 检查是否已存在
            existing = NodeType.query.filter_by(slug=nt_data['slug']).first()
            if existing:
                continue
                
            node_type = NodeType(
                name=nt_data['name'],
                slug=nt_data['slug'],
                description=nt_data.get('description', ''),
                icon=nt_data.get('icon', 'bi-folder'),
                fields_config=nt_data.get('fields_config', []),
                is_active=nt_data.get('is_active', True)
            )
            db.session.add(node_type)
        
        db.session.commit()
