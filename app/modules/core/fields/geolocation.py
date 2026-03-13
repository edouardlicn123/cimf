from .base import BaseField

class GeolocationField(BaseField):
    name = 'geolocation'
    label = '地理位置'
    widget = 'geolocation_input'
    properties = ['lat', 'lng', 'address']
    
    def render(self, value, mode='edit'):
        lat = value.get('lat', '')
        lng = value.get('lng', '')
        address = value.get('address', '')
        
        if mode == 'view':
            if lat and lng:
                return f'{address or ""} ({lat}, {lng})'
            return ''
        
        return f'''
        <div class="geolocation-input">
            <input type="text" name="{self.field_name}_lat" placeholder="纬度" value="{lat}" class="form-control mb-2">
            <input type="text" name="{self.field_name}_lng" placeholder="经度" value="{lng}" class="form-control mb-2">
            <input type="text" name="{self.field_name}_address" placeholder="地址" value="{address}" class="form-control">
        </div>
        '''
    
    def validate(self, value):
        errors = []
        if self.field_config.get('required') and not value.get('lat'):
            errors.append(f'{self.field_config.get("label")} 为必填项')
        return errors
