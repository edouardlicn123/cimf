# Customer Node Configuration
"""客户节点配置文件"""

from app.modules.nodes.customer.routes import customer_bp

NODE_TYPE_CONFIG = {
    'slug': 'customer',
    'name': '客户信息',
    'description': '记录客户基本信息',
    
    'files': {
        'model': 'app/models/node/customer.py',
        'service': 'app/services/node/customer/customer_service.py',
        'routes': 'app/modules/nodes/customer/routes.py',
        'forms': 'app/modules/nodes/customer/forms.py',
        'templates': 'app/templates/nodes/customer/',
    },
    
    'tables': {
        'main': 'nodes',
        'fields': 'customer_fields',
    },
    
    'fields': [
        {'name': 'customer_name', 'type': 'string', 'label': '客户名称', 'required': True, 'unique': True},
        {'name': 'contact_person', 'type': 'string', 'label': '联系人', 'required': False},
        {'name': 'phone', 'type': 'telephone', 'label': '电话', 'required': False},
        {'name': 'email', 'type': 'email', 'label': '邮箱', 'required': False},
        {'name': 'address', 'type': 'address', 'label': '地址', 'required': False},
        {'name': 'customer_type', 'type': 'entity_reference', 'label': '客户类型', 'required': False, 'reference_type': 'taxonomy'},
        {'name': 'notes', 'type': 'string_long', 'label': '备注', 'required': False},
    ],
    
    'enabled': True,
}

def get_config():
    return NODE_TYPE_CONFIG
