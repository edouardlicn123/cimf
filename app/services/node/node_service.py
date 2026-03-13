# Node Service
from app.models.node.node import Node
from app.models.node.node_type import NodeType
from app.services.node.node_type_service import NodeTypeService
from app import db

class NodeService:
    """节点数据服务"""
    
    @staticmethod
    def get_by_type(node_type_slug, page=1, per_page=20):
        node_type = NodeTypeService.get_by_slug(node_type_slug)
        if not node_type:
            return []
        return Node.query.filter_by(node_type_id=node_type.id).paginate(page=page, per_page=per_page)
    
    @staticmethod
    def get_by_id(node_id):
        return Node.query.get(node_id)
    
    @staticmethod
    def create(node_type_id, user_id):
        node = Node(
            node_type_id=node_type_id,
            created_by=user_id,
            updated_by=user_id
        )
        db.session.add(node)
        db.session.commit()
        return node
    
    @staticmethod
    def update(node_id, user_id):
        node = Node.query.get(node_id)
        node.updated_by = user_id
        db.session.commit()
        return node
    
    @staticmethod
    def delete(node_id):
        node = Node.query.get(node_id)
        db.session.delete(node)
        db.session.commit()
