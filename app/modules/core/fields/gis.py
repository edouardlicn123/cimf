from .base import BaseField

class GISField(BaseField):
    name = 'gis'
    label = '地理围栏'
    widget = 'gis_input'
    properties = ['point', 'spatial_ref']
    
    def render(self, value, mode='edit'):
        point = value.get('point', '')
        spatial_ref = value.get('spatial_ref', 'EPSG:4326')
        
        if mode == 'view':
            return point or '未设置'
        
        return f'''
        <div class="gis-input">
            <input type="text" name="{self.field_name}" placeholder="坐标点 (格式: x,y)" value="{point}" class="form-control mb-2">
            <input type="text" name="{self.field_name}_ref" placeholder="坐标系 (如 EPSG:4326)" value="{spatial_ref}" class="form-control">
        </div>
        '''
    
    def validate(self, value):
        errors = []
        if self.field_config.get('required') and not value.get('point'):
            errors.append(f'{self.field_config.get("label")} 为必填项')
        return errors
