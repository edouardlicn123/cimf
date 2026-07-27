# customer 模块快照

## 模型
| 模型 | 字段 |
|------|------|
| CustomerFields | node, customer_name, customer_code, customer_type, enterprise_name, phone1, email1, phone2... |

## 服务类
| 方法 | 参数 |
|------|------|
| CustomerService.get_by_node_id | node_id |
| CustomerService.get_list | search, customer_type_id, customer_level_id, user |
| CustomerService._generate_unique_code |  |
| CustomerService._build_fields | data, extra |
| CustomerService.create | user, data |
| CustomerService.import_row | data, user |
| CustomerService.update | customer_id, _user, data |
| CustomerService.delete | customer_id |
| CustomerService.get_exportable_fields |  |
| CustomerService.init_sample_data |  |

## 文件
- `modules/customer/models.py` (87 行)
- `modules/customer/services.py` (262 行)
- `modules/customer/views.py` (209 行)
- `modules/customer/forms.py` (160 行)
- `modules/customer/module.py` (83 行)
