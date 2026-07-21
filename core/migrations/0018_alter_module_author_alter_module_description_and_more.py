from django.db import migrations, models


def _null_to_empty(apps, schema_editor):
    """将现有 NULL 值转为空字符串"""
    tables = [
        ("modules", ["author", "description"]),
        ("node_types", ["author", "description"]),
        ("system_settings", ["description"]),
        ("taxonomies", ["description"]),
        ("taxonomy_items", ["description"]),
        ("tool_types", ["author", "description"]),
    ]
    with schema_editor.connection.cursor() as cursor:
        for table, fields in tables:
            for field in fields:
                cursor.execute(f"UPDATE {table} SET {field} = '' WHERE {field} IS NULL")  # noqa: S608


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0017_alter_taxonomyitem_unique_together"),
    ]

    operations = [
        migrations.RunPython(_null_to_empty, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="module",
            name="author",
            field=models.CharField(blank=True, max_length=100, verbose_name="作者"),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="module",
            name="description",
            field=models.TextField(blank=True, verbose_name="描述"),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="nodetype",
            name="author",
            field=models.CharField(blank=True, max_length=100, verbose_name="作者"),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="nodetype",
            name="description",
            field=models.CharField(blank=True, max_length=500, verbose_name="描述"),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="systemsetting",
            name="description",
            field=models.CharField(blank=True, max_length=255, verbose_name="描述"),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="taxonomy",
            name="description",
            field=models.CharField(blank=True, max_length=512, verbose_name="描述"),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="taxonomyitem",
            name="description",
            field=models.CharField(blank=True, max_length=512, verbose_name="描述"),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="tooltype",
            name="author",
            field=models.CharField(blank=True, max_length=100, verbose_name="作者"),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="tooltype",
            name="description",
            field=models.CharField(blank=True, max_length=500, verbose_name="描述"),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="user",
            name="email",
            field=models.EmailField(
                blank=True,
                db_index=True,
                help_text="用户邮箱（可选，用于密码重置、通知等）",
                max_length=254,
                verbose_name="邮箱",
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="user",
            name="nickname",
            field=models.CharField(
                blank=True, help_text="显示昵称（仪表盘、项目成员列表等处优先显示）", max_length=64, verbose_name="昵称"
            ),
            preserve_default=False,
        ),
    ]
