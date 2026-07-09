# customer 模块快照

## 模型
| 模型 | 字段 |
|------|------|
| CustomerFields | node, customer_name, customer_code, customer_type, enterprise_name, phone1, email1, phone2... |

## 服务类
| 方法 | 参数 |
|------|------|
| CustomerService.get_list | search, customer_type_id, customer_level_id, user |
| CustomerService.get_by_id | customer_id |
| CustomerService.get_by_node_id | node_id |
| CustomerService.create | user, data |
| CustomerService.update | customer_id, _user, data |
| CustomerService.delete | customer_id |
| CustomerService.get_exportable_fields |  |
| CustomerService.get_count |  |
| CustomerService.get_recent_count | days |
| CustomerService.init_sample_data |  |

## 文件
- `modules/customer/models.py` (84 行)
- `modules/customer/services.py` (296 行)
- `modules/customer/views.py` (327 行)
- `modules/customer/forms.py` (228 行)
- `modules/customer/module.py` (83 行)
