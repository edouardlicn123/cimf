from .base import BaseField

class AddressField(BaseField):
    name = 'address'
    label = '标准地址字段'
    widget = 'address_input'
    properties = ['province', 'city', 'district', 'street', 'house_number', 'grid_id']
    
    def render(self, value, mode='edit'):
        province = value.get('province', '')
        city = value.get('city', '')
        district = value.get('district', '')
        street = value.get('street', '')
        house_number = value.get('house_number', '')
        
        if mode == 'view':
            return f"{province}{city}{district}{street}{house_number}"
        
        return f'''
        <div class="address-field">
            <div class="row">
                <div class="col-md-3 mb-2">
                    <input type="text" name="{self.field_name}[province]" placeholder="省" value="{province}" class="form-control">
                </div>
                <div class="col-md-3 mb-2">
                    <input type="text" name="{self.field_name}[city]" placeholder="市" value="{city}" class="form-control">
                </div>
                <div class="col-md-3 mb-2">
                    <input type="text" name="{self.field_name}[district]" placeholder="区" value="{district}" class="form-control">
                </div>
                <div class="col-md-3 mb-2">
                    <input type="text" name="{self.field_name}[grid_id]" placeholder="网格ID" value="{value.get('grid_id', '')}" class="form-control">
                </div>
            </div>
            <div class="row">
                <div class="col-md-6 mb-2">
                    <input type="text" name="{self.field_name}[street]" placeholder="街道" value="{street}" class="form-control">
                </div>
                <div class="col-md-6 mb-2">
                    <input type="text" name="{self.field_name}[house_number]" placeholder="门牌号" value="{house_number}" class="form-control">
                </div>
            </div>
        </div>
        '''
    
    def validate(self, value):
        errors = []
        if self.field_config.get('required') and not value.get('province'):
            errors.append(f'{self.field_config.get("label")} 为必填项')
        return errors
