# -*- coding: utf-8 -*-
"""
ImportService - 导入服务

提供通用的数据导入功能，支持 CSV/Excel 格式
"""

import re
import io
from typing import List, Dict, Any, Tuple
from django.http import HttpResponse

try:
    import chardet
except ImportError:
    chardet = None


class ImportService:
    """通用导入服务"""
    
    FORMAT_CSV = 'csv'
    FORMAT_XLSX = 'xlsx'
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    
    FK_TAXONOMY_OVERRIDES = {
        ('customer_cn', 'enterprise_type'): 'enterprise_nature',
    }
    
    @classmethod
    def get_importable_fields(cls, node_type_slug: str) -> List[Dict]:
        """获取可导入的字段列表"""
        from core.importexport.model_registry import ModelRegistry
        from core.importexport.field_extractor import FieldDefExtractor
        
        model_class = ModelRegistry.get_model(node_type_slug)
        if not model_class:
            return []
        
        return FieldDefExtractor.extract(model_class)
    
    @classmethod
    def read_file(cls, file, format: str) -> Tuple[List[str], List[List[str]]]:
        """读取文件内容，含大小检查"""
        cls._validate_file_size(file)
        if format == cls.FORMAT_CSV:
            return cls._read_csv(file)
        else:
            return cls._read_xlsx(file)
    
    @classmethod
    def _validate_file_size(cls, file):
        """验证文件大小不超过限制"""
        if hasattr(file, 'size') and file.size > cls.MAX_FILE_SIZE:
            raise ValueError(f"文件过大（{file.size / 1024 / 1024:.1f}MB），最大允许 {cls.MAX_FILE_SIZE / 1024 / 1024:.0f}MB")
    
    @classmethod
    def _detect_encoding(cls, raw: bytes) -> str:
        """检测文件编码"""
        if chardet:
            try:
                result = chardet.detect(raw)
                encoding = result.get('encoding', '') or ''
                if encoding.lower().replace('-', '') in ('utf8', 'utf8sig', 'ascii'):
                    return 'utf-8'
                if encoding:
                    return encoding
            except Exception:
                pass
        # 回退：尝试常见编码
        for enc in ('utf-8-sig', 'utf-8', 'gbk', 'gb2312', 'latin-1'):
            try:
                raw.decode(enc)
                return enc
            except (UnicodeDecodeError, LookupError):
                continue
        return 'utf-8'
    
    @classmethod
    def _read_csv(cls, file) -> Tuple[List[str], List[List[str]]]:
        """读取 CSV 文件，含编码检测"""
        import csv
        
        file_content = file.read()
        if hasattr(file, 'seek'):
            file.seek(0)
        if not file_content:
            return [], []
        encoding = cls._detect_encoding(file_content)
        try:
            decoded_file = file_content.decode(encoding)
        except (UnicodeDecodeError, LookupError):
            decoded_file = file_content.decode('utf-8', errors='replace')
        reader = csv.reader(decoded_file.splitlines())
        rows = list(reader)
        
        if not rows:
            return [], []
        
        headers = rows[0] if rows else []
        data_rows = rows[1:] if len(rows) > 1 else []
        
        return headers, data_rows
    
    @classmethod
    def _read_xlsx(cls, file) -> Tuple[List[str], List[List[str]]]:
        """读取 XLSX 文件"""
        from openpyxl import load_workbook
        
        file_content = file.read()
        if hasattr(file, 'seek'):
            file.seek(0)
        wb = load_workbook(filename=io.BytesIO(file_content), data_only=True)
        ws = wb.active
        
        rows = list(ws.values)
        
        if not rows:
            return [], []
        
        headers = [str(h) if h is not None else '' for h in rows[0]]
        data_rows = [[str(cell) if cell is not None else '' for cell in row] for row in rows[1:]]
        
        return headers, data_rows
    
    @classmethod
    def map_headers_to_fields(cls, headers: List[str], fields: List[Dict]) -> Dict[str, str]:
        """将文件头部映射到字段定义"""
        header_to_field = {}
        header_lower_map = {h.lower(): h for h in headers}
        
        for field in fields:
            field_label = field['label'].lower()
            
            if field_label in header_lower_map:
                header_to_field[header_lower_map[field_label]] = field['name']
            else:
                field_name = field['name'].lower()
                if field_name in header_lower_map:
                    header_to_field[header_lower_map[field_name]] = field['name']
        
        return header_to_field
    
    @classmethod
    def parse_data(cls, headers: List[str], data_rows: List[List[str]], 
                   header_to_field: Dict[str, str]) -> List[Dict]:
        """解析数据行"""
        parsed_rows = []
        
        for row in data_rows:
            row_dict = {}
            for i, cell in enumerate(row):
                if i < len(headers):
                    header = headers[i]
                    if header in header_to_field:
                        field_name = header_to_field[header]
                        row_dict[field_name] = str(cell).strip() if cell else ''
            
            parsed_rows.append(row_dict)
        
        return parsed_rows
    
    @classmethod
    def validate_data(cls, node_type_slug: str, rows: List[Dict]) -> Dict:
        """验证数据"""
        fields = cls.get_importable_fields(node_type_slug)
        field_map = {f['name']: f for f in fields}
        
        valid_count = 0
        errors = []
        
        for idx, row in enumerate(rows, start=1):
            row_errors = []
            
            for field_name, value in row.items():
                if field_name not in field_map:
                    continue
                
                field = field_map[field_name]
                field_errors = cls._validate_field(field, value)
                row_errors.extend(field_errors)
            
            if row_errors:
                errors.append({
                    'row': idx,
                    'data': row,
                    'errors': row_errors,
                })
            else:
                valid_count += 1
        
        return {
            'valid_count': valid_count,
            'error_count': len(errors),
            'errors': errors,
        }
    
    @classmethod
    def _validate_field(cls, field: Dict, value: Any) -> List[str]:
        """验证单个字段

        注意：对于外键(FK)字段，只验证数据类型是否有效，不验证值是否在词汇表中存在。
        外键值的映射和自动创建在数据转换阶段处理。
        """
        errors = []

        if not value:
            if field['required']:
                errors.append(f"{field['label']} 不能为空")
            return errors

        field_type = field['type']

        if field_type == 'email':
            if not cls._is_valid_email(value):
                errors.append(f"{field['label']} 邮箱格式不正确")

        elif field_type == 'json':
            from core.importexport.special_field_handler import SpecialFieldPool
            if SpecialFieldPool.is_special_field(field['name']):
                pass

        return errors
    
    @classmethod
    def _is_valid_email(cls, email: str) -> bool:
        """验证邮箱格式"""
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return bool(re.match(pattern, str(email)))
    
    @staticmethod
    def _convert_boolean(value: Any) -> bool:
        """将多种布尔表示转换为 Python Boolean
        
        支持的输入格式：
        - 是/否
        - True/False
        - true/false
        - 1/0
        - 1.0/0.0
        - yes/no
        """
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return bool(value)
        if isinstance(value, str):
            normalized = value.strip().lower()
            return normalized in ['是', 'true', '1', '1.0', 'yes', 'y']
        return bool(value)
    
    @classmethod
    def import_data(cls, node_type_slug: str, rows: List[Dict], 
                    user, skip_duplicates: bool = True) -> Dict:
        """执行导入"""
        from core.importexport.model_registry import ModelRegistry
        from core.importexport.fk_resolver import FKResolverPool
        from core.importexport.special_field_handler import SpecialFieldPool
        from core.node.models import Node, NodeType
        
        model_class = ModelRegistry.get_model(node_type_slug)
        fields = cls.get_importable_fields(node_type_slug)
        field_map = {f['name']: f for f in fields}

        success_count = 0
        errors = []
        warnings = []

        node_type = NodeType.objects.filter(slug=node_type_slug).first()
        if not node_type:
            raise ValueError(f"未找到节点类型: {node_type_slug}")

        for idx, row in enumerate(rows, start=1):
            try:
                transformed = cls._transform_row(row, node_type_slug, field_map)

                existing = cls._find_existing(model_class, transformed)

                if existing:
                    if skip_duplicates:
                        warnings.append({
                            'row': idx,
                            'data': row,
                            'message': '记录已存在，已跳过',
                        })
                        continue
                    instance = existing
                else:
                    node = Node.objects.create(
                        node_type=node_type,
                        created_by=user,
                        updated_by=user,
                    )
                    instance = model_class.objects.create(node=node)

                for key, value in transformed.items():
                    setattr(instance, key, value)

                instance.save()
                success_count += 1

            except Exception as e:
                errors.append({
                    'row': idx,
                    'data': row,
                    'errors': [str(e)],
                })

        return {
            'success_count': success_count,
            'warning_count': len(warnings),
            'warning_details': warnings,
            'error_count': len(errors),
            'errors': errors,
        }
    
    @classmethod
    def _transform_row(cls, row: Dict, node_type_slug: str, field_map: Dict) -> Dict:
        """转换行数据"""
        from core.importexport.fk_resolver import FKResolverPool
        from core.importexport.special_field_handler import SpecialFieldPool
        
        transformed = {}
        
        for field_name, value in row.items():
            if field_name not in field_map:
                continue
            
            field = field_map[field_name]
            field_type = field['type']
            
            if value is None or (isinstance(value, str) and not value.strip()):
                continue
            
            if field_type == 'fk':
                fk_to = field.get('fk_to')
                if fk_to:
                    taxonomy_slug = cls.FK_TAXONOMY_OVERRIDES.get(
                        (node_type_slug, field_name),
                        field.get('taxonomy', field_name)
                    )
                    resolved = FKResolverPool.resolve(fk_to, value, taxonomy_slug, auto_create=True)
                    if resolved is not None:
                        transformed[field_name] = resolved
            
            elif field_type == 'json':
                if SpecialFieldPool.is_special_field(field_name):
                    transformed[field_name] = SpecialFieldPool.handle_import(field_name, value)
                else:
                    transformed[field_name] = value
            
            elif field_type == 'boolean':
                transformed[field_name] = cls._convert_boolean(value)
            
            else:
                transformed[field_name] = value
        
        return transformed
    
    @classmethod
    def _find_existing(cls, model_class, data: Dict):
        """查找已存在的记录"""
        for field_name, value in data.items():
            try:
                field = model_class._meta.get_field(field_name)
            except Exception:
                continue
            if getattr(field, 'unique', False) and value:
                existing = model_class.objects.filter(**{field_name: value}).first()
                if existing:
                    return existing
        return None
    
    @classmethod
    def get_fk_fields_with_options(cls, node_type_slug: str) -> List[Dict]:
        """获取 FK 字段及其可选值"""
        from core.importexport.model_registry import ModelRegistry
        from core.models import Taxonomy, TaxonomyItem
        
        fields = cls.get_importable_fields(node_type_slug)
        
        result = []
        
        for field in fields:
            if field['type'] != 'fk':
                continue
            
            field_name = field['name']
            
            taxonomy_slug = cls.FK_TAXONOMY_OVERRIDES.get(
                (node_type_slug, field_name),
                field.get('taxonomy', field_name)
            )
            
            taxonomy = Taxonomy.objects.filter(slug=taxonomy_slug).first()
            
            if taxonomy:
                items = list(TaxonomyItem.objects.filter(
                    taxonomy=taxonomy
                ).values_list('name', flat=True).order_by('weight', 'name'))
                
                result.append({
                    'name': field_name,
                    'label': field['label'],
                    'items': items,
                    'total': len(items)
                })
        
        return result
    
    @classmethod
    def generate_error_csv(cls, errors: List[Dict], fields: List[Dict]) -> HttpResponse:
        """生成错误列表 CSV"""
        import csv
        
        response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
        response['Content-Disposition'] = 'attachment; filename="import_errors.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['行号', '错误原因', '数据'])
        
        for error in errors:
            row_num = error.get('row', '')
            error_msgs = '; '.join(error.get('errors', []))
            data = str(error.get('data', ''))
            writer.writerow([row_num, error_msgs, data])
        
        return response