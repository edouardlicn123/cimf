class BaseField:
    """字段类型基类"""
    name = None
    label = None
    widget = None
    properties = []
    
    def __init__(self, field_name, field_config):
        self.field_name = field_name
        self.field_config = field_config
    
    def render(self, value, mode='edit'):
        raise NotImplementedError
    
    def validate(self, value):
        return []
    
    def format(self, value):
        return value
    
    def get_widget_config(self):
        return {}
