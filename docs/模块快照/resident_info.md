# resident_info 模块快照

## 模型
| 模型 | 字段 |
|------|------|
| ResidentInfoFields | node, name, relation, id_card, other_id_type, other_id_number, gender, birth_date... |

## 服务类
| 方法 | 参数 |
|------|------|
| ResidentInfoService.get_list | search, resident_type_id, grid_id, current_community... |
| ResidentInfoService.get_by_node_id | node_id |
| ResidentInfoService.create | user, data |
| ResidentInfoService.update | resident_id, data |
| ResidentInfoService.delete | resident_id |
| ResidentInfoService.delete_by_node_id | node_id |
| ResidentInfoService.get_count |  |
| ResidentInfoService.get_recent_count | days |
| ResidentInfoService.get_exportable_fields |  |
| ResidentInfoService.init_sample_data |  |

## 文件
- `modules/resident_info/models.py` (189 行)
- `modules/resident_info/services.py` (239 行)
- `modules/resident_info/views.py` (244 行)
- `modules/resident_info/forms.py` (101 行)
- `modules/resident_info/module.py` (89 行)
