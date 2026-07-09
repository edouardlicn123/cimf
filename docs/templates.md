# 模板继承索引

## 继承树

```
base.html
├── auth/login.html
├── includes/error_base.html
│   └── errors/{400,401,403,404,500}.html
├── frames/frame_dashboard.html            # 仪表盘布局
│   └── indexdashboard.html
├── frames/frame_sidebar_base.html         # 侧边栏布局基类
│   ├── frames/frame_admin.html            # 系统管理
│   │   ├── admin/{dashboard,system_users,system_user_edit,
│   │   │         system_permissions,permission_check,
│   │   │         system_settings,logs,system_cron_manager}.html
│   │   └── smtp/{config,history}.html
│   ├── frames/frame_node.html             # 节点布局 → node/node_dashboard.html
│   ├── frames/frame_structure.html        # 内容结构布局
│   │   ├── node/{edit,node_types_list}.html
│   │   ├── module/modules/create.html
│   │   ├── structure/{structure_dashboard,
│   │   │         taxonomies/{index,view,edit},
│   │   │         field_types/field_types}.html
│   ├── frames/frame_myinfo.html           # 个人信息
│   │   ├── usermenu/{profile,settings,homepage_settings}.html
│   │   └── nav_cards/settings.html
│   ├── frames/frame_importexport.html     # 导入导出
│   │   ├── importexport/{dashboard,import,import_page,
│   │   │         import_result,export,export_confirm,
│   │   │         export_fields,export_exporting}.html
│   └── frames/frame_tools.html            # 工具 → tools/tools_dashboard.html
└── frames/frame_module.html               # 模块管理
    ├── module/modules.html
    └── marketplace/index.html

smtp/base_email.html (独立邮件基类, 非页面继承链)
└── smtp/{notification,verification_code}.html
```

## 公共片段 (includes/)

| 文件 | 用途 |
|------|------|
| nav/header/footer.html | 导航栏/标题栏/页脚 |
| sidebar.html + content_area.html | 侧边栏布局外壳 |
| watermark.html / toast_messages.html | 水印 / Toast |
| card_section.html / dashboard_cards_area.html / nav_cards_area.html | 卡片容器 |
| entry_card.html / entry_card_grid.html / stat_card.html / table_card.html | 卡片类型 |
| form_errors.html / form_actions.html / form_switch.html / filter_bar.html | 表单组件 |
| modal.html / pagination.html / alert.html / empty_state.html | UI 组件 |
| permissions_table.html / role_badge.html / status_badge.html | 数据展示 |
| csrf.html / style.html / js.html | 基础设施 |

## Block 名称

**base.html**: `title`, `head_extra`, `main_content`, `content`, `scripts`

**frame_sidebar_base.html** (extends base): `sidebar_nav`, `admin_title_content`, `admin_buttons_content`, `admin_content`

**frame_dashboard.html** (extends base): `admin_content`

**smtp/base_email.html**: `email_content`
