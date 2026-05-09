from django.test import TestCase
from django.contrib.auth import get_user_model
from core.models import Taxonomy, TaxonomyItem, SystemSetting, ChinaRegion

User = get_user_model()


class UserModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='test12345678',
            email='test@example.com',
            role='manager',
            is_admin=False
        )

    def test_user_creation(self):
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.role, 'manager')
        self.assertFalse(self.user.is_admin)

    def test_user_str(self):
        self.assertIn('testuser', str(self.user))

    def test_user_is_active(self):
        self.assertTrue(self.user.is_active)

    def test_user_is_staff_false(self):
        self.assertFalse(self.user.is_staff)

    def test_admin_user(self):
        admin = User.objects.create_user(
            username='admin',
            password='admin123456',
            role='manager',
            is_admin=True
        )
        self.assertTrue(admin.is_admin)


class TaxonomyModelTestCase(TestCase):
    def setUp(self):
        self.taxonomy = Taxonomy.objects.create(
            name='测试分类',
            slug='test_tax',
            description='测试描述'
        )

    def test_taxonomy_creation(self):
        self.assertEqual(self.taxonomy.name, '测试分类')
        self.assertEqual(self.taxonomy.slug, 'test_tax')

    def test_taxonomy_str(self):
        self.assertIn('测试分类', str(self.taxonomy))

    def test_taxonomy_items_relationship(self):
        item = TaxonomyItem.objects.create(
            taxonomy=self.taxonomy,
            name='选项1',
            weight=1
        )
        self.assertEqual(item.taxonomy, self.taxonomy)
        self.assertIn(self.taxonomy.items.count(), [1])


class SystemSettingModelTestCase(TestCase):
    def setUp(self):
        self.setting = SystemSetting.objects.create(
            key='test_key',
            value='test_value',
            description='测试设置'
        )

    def test_setting_creation(self):
        self.assertEqual(self.setting.key, 'test_key')
        self.assertEqual(self.setting.value, 'test_value')

    def test_setting_str(self):
        self.assertIn('test_key', str(self.setting))

    def test_setting_update(self):
        self.setting.value = 'updated_value'
        self.setting.save()
        updated = SystemSetting.objects.get(key='test_key')
        self.assertEqual(updated.value, 'updated_value')


class ChinaRegionModelTestCase(TestCase):
    def setUp(self):
        self.province = ChinaRegion.objects.create(
            code='440000',
            name='广东省',
            level=1
        )
        self.city = ChinaRegion.objects.create(
            code='440100',
            name='广州市',
            level=2,
            parent=self.province
        )

    def test_province_creation(self):
        self.assertEqual(self.province.name, '广东省')
        self.assertEqual(self.province.level, 1)

    def test_city_creation(self):
        self.assertEqual(self.city.name, '广州市')
        self.assertEqual(self.city.level, 2)
        self.assertEqual(self.city.parent, self.province)

    def test_full_path(self):
        self.assertIn('广东省', self.city.full_path)

    def test_children_relationship(self):
        children = self.province.children.all()
        self.assertEqual(children.count(), 1)
        self.assertEqual(children.first().name, '广州市')