# 文件路径：init_schema.py
# 更新日期：2026-02-17
# 功能说明：数据库初始化脚本（非迁移版），使用 db.create_all() 创建所有缺失表（包括 SystemSetting），可选插入初始管理员用户和系统设置默认记录，支持命令行参数控制（--with-data、--force、--dry-run），生产环境慎用

import sys
import os
from datetime import datetime
from flask import current_app
from app import create_app, db
from app.models import User, SystemSetting
from app.services import SettingsService  # 使用服务层初始化默认设置
from app.modules.core.taxonomy.service import TaxonomyService  # 初始化词汇表数据

# 终端颜色辅助函数
def colored(text: str, color: str = "white") -> str:
    colors = {
        "green": "\033[92m",
        "yellow": "\033[93m",
        "red": "\033[91m",
        "cyan": "\033[96m",
        "blue": "\033[94m",
        "white": "\033[97m",
        "reset": "\033[0m",
    }
    return f"{colors.get(color, colors['white'])}{text}{colors['reset']}"


def init_database(with_data: bool = False, force: bool = False, dry_run: bool = False):
    """
    初始化数据库核心逻辑：
    1. 创建所有缺失表（db.create_all()）
    2. 可选：插入/重置默认管理员用户
    3. 可选：通过 SettingsService 初始化/重置系统设置默认值
    """
    app = create_app()
    
    with app.app_context():
        print(colored(f"FFE 项目跟进系统 - 数据库初始化工具 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})", "cyan"))
        print(colored(f"当前环境: {app.config.get('ENV', 'development')}", "cyan"))
        print(colored(f"数据库 URI: {current_app.config['SQLALCHEMY_DATABASE_URI']}", "cyan"))
        print("-" * 80)

        if dry_run:
            print(colored("【DRY-RUN 模式】仅模拟执行，不会修改数据库", "yellow"))
            print("-" * 80)

        # ── 步骤 1：创建所有缺失的表（包括 system_settings） ────────────────
        print(colored("步骤 1：检查并创建缺失的表 (db.create_all()) ...", "yellow"))
        
        try:
            if not dry_run:
                db.create_all()
                print(colored("db.create_all() 执行完成，已创建所有缺失表（含 system_settings）", "green"))
            else:
                print(colored("[模拟] 将执行 db.create_all()，包含 system_settings 表", "yellow"))
        except Exception as e:
            print(colored(f"创建表失败：{str(e)}", "red"))
            print("可能原因：数据库连接失败、权限不足、模型定义错误")
            if not dry_run:
                sys.exit(1)

        if not with_data:
            print(colored("未指定 --with-data，跳过初始数据插入", "yellow"))
            print("-" * 80)
            return

        # ── 步骤 2：初始化系统设置（使用 SettingsService 确保默认值） ────────
        print(colored("\n步骤 2.1：初始化系统设置默认值（通过 SettingsService）...", "blue"))
        try:
            if not dry_run:
                reset_count = SettingsService.reset_to_default()
                print(colored(f"  系统设置默认值已重置/插入，共 {reset_count} 项", "green"))
            else:
                print(colored("[模拟] 将调用 SettingsService.reset_to_default() 重置所有默认设置", "yellow"))
        except Exception as e:
            print(colored(f"  系统设置初始化失败：{str(e)}", "red"))
            if not dry_run:
                sys.exit(1)

        # ── 步骤 2.2：初始化/重置默认管理员用户 ──────────────────────────────
        print(colored("步骤 2.2：初始化默认管理员用户...", "blue"))

        # 默认管理员配置（环境变量覆盖优先）
        admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
        admin_nickname = os.environ.get('ADMIN_NICKNAME', '系统管理员')
        admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')  # 生产环境必须覆盖！
        admin_email    = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
        admin_theme    = os.environ.get('ADMIN_THEME', 'default')
        admin_notifications = os.environ.get('ADMIN_NOTIFICATIONS', 'true').lower() in ('true', '1', 'yes', 'on')
        admin_language = os.environ.get('ADMIN_PREFERRED_LANGUAGE', 'zh')

        # 生产环境安全限制
        if app.config.get('ENV') == 'production' and not os.environ.get('ALLOW_SEED_PROD'):
            print(colored("【生产环境安全限制】禁止自动插入初始数据！", "red"))
            print("如需强制执行，请设置环境变量 ALLOW_SEED_PROD=1 （极度不推荐）")
            sys.exit(1)

        # 密码长度最低要求（仅生产环境强制检查）
        if app.config.get('ENV') == 'production':
            if len(admin_password) < 10:
                print(colored("错误：管理员密码长度不足 10 位！请通过环境变量 ADMIN_PASSWORD 设置更强密码", "red"))
                sys.exit(1)

        existing_admin = User.query.filter_by(username=admin_username).first()

        if existing_admin and not force:
            print(colored(f"管理员 '{admin_username}' 已存在，跳过创建（使用 --force 可强制重置）", "yellow"))
        else:
            if existing_admin and force:
                print(colored(f"强制删除旧管理员 '{admin_username}' ...", "yellow"))
                if not dry_run:
                    db.session.delete(existing_admin)
                    db.session.commit()

            try:
                if not dry_run:
                    admin = User(
                        username=admin_username,
                        nickname=admin_nickname,
                        email=admin_email,
                        role='admin',
                        permissions=['*'],
                        is_admin=True,
                        is_active=True,
                        theme=admin_theme,
                        notifications_enabled=admin_notifications,
                        preferred_language=admin_language,
                        created_at=datetime.utcnow(),
                        last_login_at=None
                    )
                    admin.set_password(admin_password)
                    db.session.add(admin)
                    db.session.commit()

                print(colored("成功创建/重置默认管理员：", "green"))
                print(f"  用户名             : {admin_username}")
                print(f"  昵称               : {admin_nickname}")
                print(f"  密码               : {admin_password}  （生产环境请立即修改！）")
                print(f"  邮箱               : {admin_email}")
                print(f"  角色               : 管理员")
                print(f"  权限               : 全部 (*)")
                print(f"  主题偏好           : {admin_theme}")
                print(f"  通知开关           : {'开启' if admin_notifications else '关闭'}")
                print(f"  首选语言           : {admin_language}")
                print(colored("\n警告：请登录后立即修改密码！", "yellow"))
            except Exception as e:
                print(colored(f"创建管理员失败：{str(e)}", "red"), file=sys.stderr)
                sys.exit(1)

        # ── 步骤 2.3：初始化词汇表数据 ─────────────────────────────────────────
        print(colored("\n步骤 2.3：初始化词汇表数据...", "blue"))
        try:
            if not dry_run:
                TaxonomyService.init_default_taxonomies()
                print(colored("  词汇表数据初始化完成", "green"))
            else:
                print(colored("[模拟] 将调用 TaxonomyService.init_default_taxonomies() 初始化词汇表", "yellow"))
        except Exception as e:
            print(colored(f"  词汇表数据初始化失败：{str(e)}", "red"))
            if not dry_run:
                sys.exit(1)

        print(colored("\n所有初始化完成！", "green"))
        print("-" * 80)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="FFE 项目数据库初始化脚本（db.create_all 版）",
        epilog="生产环境请谨慎使用此脚本，建议手动建表或使用 Flask-Migrate/Alembic 管理结构变更"
    )
    parser.add_argument("--with-data", action="store_true", help="创建表 + 插入/重置初始管理员 + 系统设置默认记录")
    parser.add_argument("--force", action="store_true", help="强制重置 admin 用户（不影响 system_settings）")
    parser.add_argument("--dry-run", action="store_true", help="模拟执行，不实际写入数据库")
    args = parser.parse_args()

    try:
        init_database(
            with_data=args.with_data,
            force=args.force,
            dry_run=args.dry_run
        )
        print(colored("\n初始化流程完成。", "green"))
        if args.with_data:
            print(colored("下一步建议：", "cyan"))
            print("  1. 登录后台访问 /admin/dashboard 验证仪表盘统计")
            print("  2. 访问 /admin/system-settings 验证设置表内容")
            print("  3. 强烈建议切换到 Flask-Migrate 管理后续表结构变更")
            print("  4. 生产环境：删除 instance/site.db 后重新初始化（或使用迁移工具）")
    except KeyboardInterrupt:
        print("\n用户取消操作。")
        sys.exit(0)
    except Exception as e:
        print(colored(f"初始化过程中发生未预期错误：{str(e)}", "red"), file=sys.stderr)
        sys.exit(1)
