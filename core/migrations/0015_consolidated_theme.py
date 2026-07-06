# 主题迁移整合文件（替换 0008～0014）
# 日后修改主题列表只需修改本文件的 AlterField 的 choices

from django.db import migrations, models


def migrate_teal_users(apps, schema_editor):
    User = apps.get_model("core", "User")
    User.objects.filter(theme="teal").update(theme="default")


class Migration(migrations.Migration):
    replaces = [
        ("core", "0008_alter_user_theme"),
        ("core", "0009_alter_user_theme"),
        ("core", "0010_alter_user_theme"),
        ("core", "0011_alter_user_theme"),
        ("core", "0012_alter_user_theme"),
        ("core", "0013_alter_user_theme"),
        ("core", "0014_alter_user_theme"),
    ]

    dependencies = [
        ("core", "0007_alter_module_module_type_alter_user_theme"),
    ]

    operations = [
        migrations.RunPython(migrate_teal_users, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name="user",
            name="theme",
            field=models.CharField(
                choices=[
                    ("default", "默认"),
                    ("gov", "中国红"),
                    ("indigo", "靛蓝"),
                    ("macaron", "马卡龙"),
                    ("savawoku", "橙红"),
                    ("kajima", "绿岛森林"),
                    ("odoru", "踊"),
                    ("tais", "梵紫"),
                ],
                default="default",
                max_length=20,
                verbose_name="界面主题",
            ),
        ),
    ]
