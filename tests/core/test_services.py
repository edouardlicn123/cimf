from django.test import TestCase
from django.contrib.auth import get_user_model
from core.services import PermissionService, TaxonomyService, ChinaRegionService, WatermarkService
from core.services import UserService, AuthService, SettingsService
from core.models import Taxonomy, TaxonomyItem, SystemSetting

User = get_user_model()


class PermissionServiceTestCase(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin',
            password='admin123456',
            role='manager',
            is_admin=True
        )
        self.manager = User.objects.create_user(
            username='manager',
            password='manager123456',
            role='manager',
            is_admin=False
        )
        self.leader = User.objects.create_user(
            username='leader',
            password='leader123456',
            role='leader',
            is_admin=False
        )
        self.employee = User.objects.create_user(
            username='employee',
            password='employee123456',
            role='employee',
            is_admin=False
        )

    def test_get_all_permissions(self):
        perms = PermissionService.get_all_permissions()
        self.assertIsInstance(perms, list)
        self.assertGreater(len(perms), 0)

    def test_get_system_permissions(self):
        sys_perms = PermissionService.get_system_permissions()
        self.assertIn('system_settings', sys_perms)
        self.assertIn('user', sys_perms)

    def test_get_role_permissions(self):
        manager_perms = PermissionService.get_role_permissions('manager')
        self.assertIsInstance(manager_perms, list)
        leader_perms = PermissionService.get_role_permissions('leader')
        self.assertIsInstance(leader_perms, list)
        employee_perms = PermissionService.get_role_permissions('employee')
        self.assertIsInstance(employee_perms, list)

    def test_has_permission_admin(self):
        self.assertTrue(PermissionService.has_permission(self.admin, 'system.settings.view'))
        self.assertTrue(PermissionService.has_permission(self.admin, 'user.create'))

    def test_has_permission_manager(self):
        self.assertTrue(PermissionService.has_permission(self.manager, 'importexport.view'))

    def test_has_permission_employee_no_perms(self):
        result = PermissionService.has_permission(self.employee, 'system.settings.view')
        self.assertFalse(result)

    def test_get_user_effective_permissions_admin(self):
        perms = PermissionService.get_user_effective_permissions(self.admin)
        self.assertEqual(perms, ['*'])

    def test_get_user_effective_permissions_manager(self):
        perms = PermissionService.get_user_effective_permissions(self.manager)
        self.assertIsInstance(perms, list)

    def test_can_access_admin_true(self):
        self.assertTrue(PermissionService.can_access_admin(self.admin))

    def test_can_access_admin_false(self):
        self.assertFalse(PermissionService.can_access_admin(self.employee))

    def test_save_and_get_role_permissions_from_db(self):
        test_perms = ['user.create', 'user.read']
        PermissionService.save_role_permissions('manager', test_perms)
        db_perms = PermissionService.get_role_permissions_from_db('manager')
        self.assertEqual(db_perms, test_perms)


class TaxonomyServiceTestCase(TestCase):
    def setUp(self):
        self.taxonomy = Taxonomy.objects.create(
            name='测试分类',
            slug='test_category',
            description='测试用分类'
        )
        self.item1 = TaxonomyItem.objects.create(
            taxonomy=self.taxonomy,
            name='选项一',
            weight=1
        )
        self.item2 = TaxonomyItem.objects.create(
            taxonomy=self.taxonomy,
            name='选项二',
            weight=2
        )

    def test_get_all_taxonomies(self):
        taxonomies = TaxonomyService.get_all_taxonomies()
        self.assertIsNotNone(taxonomies)

    def test_get_taxonomy_by_id(self):
        result = TaxonomyService.get_taxonomy_by_id(self.taxonomy.id)
        self.assertEqual(result, self.taxonomy)

    def test_get_taxonomy_by_id_nonexistent(self):
        result = TaxonomyService.get_taxonomy_by_id(99999)
        self.assertIsNone(result)

    def test_get_taxonomy_by_slug(self):
        result = TaxonomyService.get_taxonomy_by_slug('test_category')
        self.assertEqual(result, self.taxonomy)

    def test_get_taxonomy_by_slug_nonexistent(self):
        result = TaxonomyService.get_taxonomy_by_slug('nonexistent')
        self.assertIsNone(result)

    def test_create_taxonomy(self):
        new_tax = TaxonomyService.create_taxonomy('新分类', 'new_cat', '描述')
        self.assertEqual(new_tax.name, '新分类')
        self.assertEqual(new_tax.slug, 'new_cat')

    def test_update_taxonomy(self):
        updated = TaxonomyService.update_taxonomy(
            self.taxonomy.id,
            name='更新后的分类'
        )
        self.assertEqual(updated.name, '更新后的分类')

    def test_delete_taxonomy(self):
        tax_id = self.taxonomy.id
        result = TaxonomyService.delete_taxonomy(tax_id)
        self.assertTrue(result)
        self.assertIsNone(Taxonomy.objects.filter(id=tax_id).first())

    def test_get_items(self):
        items = TaxonomyService.get_items(self.taxonomy.id)
        self.assertEqual(len(items), 2)

    def test_get_item(self):
        result = TaxonomyService.get_item(self.item1.id)
        self.assertEqual(result, self.item1)

    def test_create_item(self):
        new_item = TaxonomyService.create_item(
            self.taxonomy.id,
            '新选项',
            description='描述'
        )
        self.assertEqual(new_item.name, '新选项')
        self.assertEqual(new_item.taxonomy_id, self.taxonomy.id)

    def test_update_item(self):
        updated = TaxonomyService.update_item(
            self.item1.id,
            name='更新后的选项'
        )
        self.assertEqual(updated.name, '更新后的选项')

    def test_delete_item(self):
        item_id = self.item1.id
        result = TaxonomyService.delete_item(item_id)
        self.assertTrue(result)
        self.assertIsNone(TaxonomyItem.objects.filter(id=item_id).first())

    def test_reorder_items(self):
        item_ids = [self.item2.id, self.item1.id]
        result = TaxonomyService.reorder_items(self.taxonomy.id, item_ids)
        self.assertTrue(result)


class ChinaRegionServiceTestCase(TestCase):
    def setUp(self):
        from core.models import ChinaRegion
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
        self.district = ChinaRegion.objects.create(
            code='440105',
            name='天河区',
            level=3,
            parent=self.city
        )

    def test_get_provinces(self):
        provinces = ChinaRegionService.get_provinces()
        self.assertIsInstance(provinces, list)
        self.assertTrue(any(p.code == '440000' for p in provinces))

    def test_get_cities(self):
        cities = ChinaRegionService.get_cities('440000')
        self.assertIsInstance(cities, list)
        self.assertTrue(any(c.code == '440100' for c in cities))

    def test_get_cities_invalid_province(self):
        cities = ChinaRegionService.get_cities('999999')
        self.assertEqual(cities, [])

    def test_get_districts(self):
        districts = ChinaRegionService.get_districts('440100')
        self.assertIsInstance(districts, list)
        self.assertTrue(any(d.code == '440105' for d in districts))

    def test_get_districts_invalid_city(self):
        districts = ChinaRegionService.get_districts('999999')
        self.assertEqual(districts, [])

    def test_get_by_code(self):
        region = ChinaRegionService.get_by_code('440000')
        self.assertEqual(region.name, '广东省')

    def test_get_by_code_nonexistent(self):
        region = ChinaRegionService.get_by_code('999999')
        self.assertIsNone(region)

    def test_search(self):
        results = ChinaRegionService.search('广东')
        self.assertIsInstance(results, list)

    def test_get_full_path(self):
        path = ChinaRegionService.get_full_path('440105')
        self.assertIn('广东省', path)
        self.assertIn('广州市', path)
        self.assertIn('天河区', path)

    def test_get_full_path_nonexistent(self):
        path = ChinaRegionService.get_full_path('999999')
        self.assertEqual(path, '')

    def test_get_stats(self):
        stats = ChinaRegionService.get_stats()
        self.assertIn('total', stats)
        self.assertIn('provinces', stats)
        self.assertIn('cities', stats)


class WatermarkServiceTestCase(TestCase):
    def test_add_text_watermark_returns_bool(self):
        from PIL import Image
        import tempfile
        import os

        img = Image.new('RGB', (100, 100), color='white')
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_in:
            img.save(tmp_in.name)
            in_path = tmp_in.name

        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_out:
            out_path = tmp_out.name

        try:
            result = WatermarkService.add_text_watermark(
                in_path,
                out_path,
                '测试水印',
                position='center',
                opacity=0.3
            )
            self.assertIsInstance(result, bool)
        finally:
            if os.path.exists(in_path):
                os.unlink(in_path)
            if os.path.exists(out_path):
                os.unlink(out_path)

    def test_add_text_watermark_invalid_path(self):
        result = WatermarkService.add_text_watermark(
            '/nonexistent/image.png',
            '/tmp/output.png',
            'Test'
        )
        self.assertFalse(result)

    def test_add_image_watermark_invalid_image(self):
        result = WatermarkService.add_image_watermark(
            '/nonexistent/image.png',
            '/tmp/output.png',
            '/nonexistent/logo.png'
        )
        self.assertFalse(result)


class UserServiceTestCase(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin',
            password='admin123456',
            role='manager',
            is_admin=True
        )
        self.user = User.objects.create_user(
            username='testuser',
            password='test12345678',
            role='employee',
            is_admin=False
        )

    def test_create_user_empty_password(self):
        with self.assertRaises(ValueError) as context:
            UserService.create_user(
                username='newuser',
                nickname='New User',
                email='new@example.com',
                password='',
                role='employee'
            )
        self.assertIn('密码不能为空', str(context.exception))

    def test_create_user_short_password(self):
        with self.assertRaises(ValueError) as context:
            UserService.create_user(
                username='newuser',
                nickname='New User',
                email='new@example.com',
                password='short',
                role='employee'
            )
        self.assertIn('10', str(context.exception))

    def test_create_user_duplicate_username(self):
        with self.assertRaises(ValueError) as context:
            UserService.create_user(
                username='testuser',
                nickname='Another User',
                email='another@example.com',
                password='password123456',
                role='employee'
            )
        self.assertIn('用户名已存在', str(context.exception))

    def test_get_user_by_nonexistent_id(self):
        result = UserService.get_user_by_id(99999)
        self.assertIsNone(result)

    def test_get_user_stats(self):
        stats = UserService.get_user_stats()
        self.assertIn('total_users', stats)
        self.assertIn('active_users', stats)
        self.assertIn('manager_users', stats)
        self.assertIn('leader_users', stats)
        self.assertIn('employee_users', stats)


class AuthServiceTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='test12345678'
        )

    def test_login_max_failures_default(self):
        max_failures = AuthService.get_login_max_failures()
        self.assertEqual(max_failures, 5)

    def test_login_lock_minutes_default(self):
        lock_minutes = AuthService.get_login_lock_minutes()
        self.assertEqual(lock_minutes, 30)


class SettingsServiceTestCase(TestCase):
    def test_get_setting_existing(self):
        SettingsService.save_setting('test_key', 'test_value')
        value = SettingsService.get_setting('test_key')
        self.assertEqual(value, 'test_value')

    def test_get_setting_with_default(self):
        value = SettingsService.get_setting('nonexistent', 'default')
        self.assertEqual(value, 'default')

    def test_save_setting_updates_cache(self):
        SettingsService.save_setting('cache_test', 'value1')
        value1 = SettingsService.get_setting('cache_test')
        self.assertEqual(value1, 'value1')
        
        SettingsService.save_setting('cache_test', 'value2')
        value2 = SettingsService.get_setting('cache_test')
        self.assertEqual(value2, 'value2')