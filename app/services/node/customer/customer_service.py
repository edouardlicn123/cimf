# Customer Service
from app.models.node import Node, NodeType
from app.models.node.customer import CustomerFields
from app.services.node.node_service import NodeService
from app.services.node.node_type_service import NodeTypeService
from app import db

class CustomerService:
    """客户节点专用服务"""
    
    NODE_TYPE_SLUG = 'customer'
    
    @staticmethod
    def get_node_type():
        return NodeTypeService.get_by_slug(CustomerService.NODE_TYPE_SLUG)
    
    @staticmethod
    def get_customer_list(page=1, per_page=20):
        node_type = CustomerService.get_node_type()
        if not node_type:
            return []
        return Node.query.filter_by(node_type_id=node_type.id).paginate(page=page, per_page=per_page)
    
    @staticmethod
    def get_customer_by_id(customer_id):
        node = Node.query.get(customer_id)
        if not node:
            return None
        fields = CustomerFields.query.filter_by(node_id=customer_id).first()
        return {'node': node, 'fields': fields}
    
    @staticmethod
    def create_customer(data, user_id):
        node_type = CustomerService.get_node_type()
        
        node = Node(
            node_type_id=node_type.id,
            created_by=user_id,
            updated_by=user_id
        )
        db.session.add(node)
        db.session.flush()
        
        fields = CustomerFields(
            node_id=node.id,
            customer_name=data.get('customer_name'),
            contact_person=data.get('contact_person'),
            phone=data.get('phone'),
            email=data.get('email'),
            address=data.get('address'),
            customer_type=data.get('customer_type'),
            notes=data.get('notes')
        )
        db.session.add(fields)
        db.session.commit()
        
        return node
    
    @staticmethod
    def update_customer(customer_id, data, user_id):
        node = Node.query.get(customer_id)
        node.updated_by = user_id
        
        fields = CustomerFields.query.filter_by(node_id=customer_id).first()
        if fields:
            for key, value in data.items():
                if hasattr(fields, key):
                    setattr(fields, key, value)
        
        db.session.commit()
        return node
    
    @staticmethod
    def delete_customer(customer_id):
        fields = CustomerFields.query.filter_by(node_id=customer_id).first()
        if fields:
            db.session.delete(fields)
        
        node = Node.query.get(customer_id)
        if node:
            db.session.delete(node)
        
        db.session.commit()
