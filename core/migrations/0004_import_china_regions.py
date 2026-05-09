# -*- coding: utf-8 -*-
"""
================================================================================
文件：0004_import_china_regions.py
路径：/home/edo/cimf/core/migrations/
================================================================================

功能说明：
    迁移脚本 - 在数据库迁移时导入中国行政区划数据

版本：
    - 1.0: 初始版本

执行说明：
    运行 migrate 时会自动执行此迁移，导入省市区数据
"""

from django.db import migrations


def import_china_regions(apps, schema_editor):
    """导入省市区数据"""
    from core.services import ChinaRegionService
    result = ChinaRegionService.import_from_file()
    if result.get('success'):
        print(f"[迁移] 省市区数据导入成功: {result.get('count')} 条")
    else:
        print(f"[迁移] 省市区数据导入失败: {result.get('error')}")


def reverse_import(apps, schema_editor):
    """回滚 - 删除省市区数据"""
    from core.models import ChinaRegion
    count = ChinaRegion.objects.count()
    ChinaRegion.objects.all().delete()
    print(f"[迁移] 已删除 {count} 条省市区数据")


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0003_add_tool_type'),
    ]
    
    operations = [
        migrations.RunPython(import_china_regions, reverse_import),
    ]