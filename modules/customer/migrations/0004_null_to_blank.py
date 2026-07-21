from django.db import migrations, models


def _null_to_empty(apps, schema_editor):
    """将 CustomerFields 字段的 NULL 转为空字符串"""
    fields = [
        "customer_code",
        "enterprise_name",
        "phone1",
        "email1",
        "phone2",
        "email2",
        "linkedin",
        "province",
        "address",
        "postal_code",
        "industry",
        "website",
        "notes",
    ]
    with schema_editor.connection.cursor() as cursor:
        for field in fields:
            cursor.execute(f"UPDATE customer_fields SET {field} = '' WHERE {field} IS NULL")  # noqa: S608


class Migration(migrations.Migration):
    dependencies = [
        ("customer", "0003_alter_customerfields_phone1_and_more"),
    ]

    operations = [
        migrations.RunPython(_null_to_empty, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="customerfields",
            name="address",
            field=models.CharField(blank=True, max_length=200, verbose_name="详细地址"),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="customerfields",
            name="customer_code",
            field=models.CharField(blank=True, max_length=50, unique=True, verbose_name="客户代码"),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="customerfields",
            name="email1",
            field=models.EmailField(blank=True, max_length=254, verbose_name="邮箱1"),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="customerfields",
            name="email2",
            field=models.EmailField(blank=True, max_length=254, verbose_name="邮箱2"),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="customerfields",
            name="enterprise_name",
            field=models.CharField(blank=True, max_length=200, verbose_name="企业名称"),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="customerfields",
            name="industry",
            field=models.CharField(blank=True, max_length=50, verbose_name="所属行业"),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="customerfields",
            name="linkedin",
            field=models.URLField(blank=True, max_length=200, verbose_name="领英"),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="customerfields",
            name="notes",
            field=models.TextField(blank=True, verbose_name="备注"),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="customerfields",
            name="phone1",
            field=models.CharField(blank=True, max_length=50, verbose_name="电话1"),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="customerfields",
            name="phone2",
            field=models.CharField(blank=True, max_length=50, verbose_name="电话2"),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="customerfields",
            name="postal_code",
            field=models.CharField(blank=True, max_length=10, verbose_name="邮政编码"),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="customerfields",
            name="province",
            field=models.CharField(blank=True, max_length=50, verbose_name="省份/城市"),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="customerfields",
            name="website",
            field=models.URLField(blank=True, max_length=200, verbose_name="网站"),
            preserve_default=False,
        ),
    ]
